"""StudyAI — Multi-agent pipeline orchestrated with LangGraph."""
import asyncio
import logging
import os
from typing import Any, Optional, TypedDict, List

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from agents.parser import parse_node
from agents.extractor import extract_node
from agents.retriever import retrieve_node
from agents.connections import connection_node
from agents.summarizer import summarize_node
from agents.quiz_gen import quiz_node
from agents.revision import revision_node
from agents.analytics import analytics_node

load_dotenv()

log = logging.getLogger(__name__)


# ─── Pipeline State ───────────────────────────────────────────────────────────

class PipelineState(TypedDict):
    """LangGraph state schema."""
    file_path: str
    filename: str
    user_id: str
    material_id: str
    db: Any
    chunks: List[str]
    metadata: dict
    concepts: List[dict]
    embeddings: List[Any]
    faiss_ids: List[str]
    related: List[dict]
    connections: List[str]
    summary: dict
    questions: List[dict]
    revision: dict
    analytics: dict
    progress_queue: Optional[asyncio.Queue]
    error: Optional[str]
    pipeline_quiz_id: Optional[int]


# ─── Embed + Index nodes ──────────────────────────────────────────────────────

async def embed_node(state: PipelineState) -> PipelineState:
    """Generate embeddings for all chunks using sentence-transformers."""
    from tools.embedder import generate_embeddings

    chunks = state.get("chunks", [])
    if not chunks:
        log.warning("embed_node: no chunks to embed, skipping")
        return state

    await _push(state, "embed", "running", "Generating embeddings…")
    # Run CPU-bound encoding in a thread so the event loop stays free
    loop = asyncio.get_event_loop()
    embeddings = await loop.run_in_executor(None, generate_embeddings, chunks)
    state["embeddings"] = embeddings
    log.info("embed_node: embedded %d chunks", len(embeddings))
    await _push(state, "embed", "done", f"Embedded {len(embeddings)} chunks")
    return state


async def index_node(state: PipelineState) -> PipelineState:
    """Add embeddings to the per-user FAISS index and persist to disk."""
    from tools.faiss_store import FAISSStore

    embeddings  = state.get("embeddings", [])
    chunks      = state.get("chunks", [])
    material_id = state.get("material_id")
    user_id     = state.get("user_id")

    if not embeddings:
        log.warning("index_node: no embeddings to index, skipping")
        return state

    await _push(state, "index", "running", "Indexing into FAISS…")

    store = FAISSStore(user_id)
    store.load()

    meta_list = [
        {
            "material_id": material_id,
            "chunk_text":  chunk,
            "chunk_index": i,
            "embedding":   emb,
        }
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
    ]
    ids = store.add(embeddings, meta_list)
    state["faiss_ids"] = ids
    log.info("index_node: indexed %d vectors", len(ids))
    await _push(state, "index", "done", f"Indexed {len(ids)} vectors")
    return state


# ─── Helpers ──────────────────────────────────────────────────────────────────

async def _push(state: PipelineState, step: str, status: str, message: str):
    """Send a progress event to the WebSocket queue if one exists."""
    q: Optional[asyncio.Queue] = state.get("progress_queue")
    if q:
        await q.put({"step": step, "status": status, "message": message})


# ─── LangGraph Orchestration ──────────────────────────────────────────────────

workflow = StateGraph(PipelineState)

# Add Nodes
workflow.add_node("parse",     parse_node)
workflow.add_node("extract",   extract_node)
workflow.add_node("embed",     embed_node)
workflow.add_node("index",     index_node)
workflow.add_node("retrieve",  retrieve_node)
workflow.add_node("connections", connection_node)
workflow.add_node("summarize", summarize_node)
workflow.add_node("quiz",      quiz_node)
workflow.add_node("revision",  revision_node)
workflow.add_node("analytics", analytics_node)

# Add Edges (Linear Flow)
workflow.set_entry_point("parse")
workflow.add_edge("parse",     "extract")
workflow.add_edge("extract",   "embed")
workflow.add_edge("embed",     "index")
workflow.add_edge("index",     "retrieve")
workflow.add_edge("retrieve",  "connections")
workflow.add_edge("connections", "summarize")
workflow.add_edge("summarize", "quiz")
workflow.add_edge("quiz",      "revision")
workflow.add_edge("revision",  "analytics")
workflow.add_edge("analytics", END)

# Compile
app = workflow.compile()


async def run_pipeline(state: PipelineState) -> PipelineState:
    """
    Run all pipeline nodes using the LangGraph engine.
    """
    try:
        final_state = await app.ainvoke(state)
        # Final state is a dict that matches PipelineState
        return dict(final_state)
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        log.error("❌ LangGraph Pipeline raised an exception:\n%s", tb)
        state["error"] = f"Pipeline failed: {exc}"
        await _push(state, "pipeline", "error", f"Failed: {exc}")
        return state

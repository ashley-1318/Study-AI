"""StudyAI — Cross-material connection agent node."""
import os
import logging
from typing import Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
log = logging.getLogger(__name__)

_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY", ""),
)

async def connection_node(state: dict) -> dict:
    """
    Identifies semantic links between the newly uploaded content and past study materials.
    Uses retrieved snippets from other materials to synthesize specific connections.
    """
    concepts    = state.get("concepts", [])
    related     = state.get("related", [])  # Found by retriever node
    material_id = state.get("material_id")
    db          = state.get("db")

    if not concepts or not related or not db:
        state["connections"] = []
        return state

    await _push(state, "connections", "running", "Synthesizing cross-material intelligence…")

    from database import StudyMaterial

    # 1. Structure raw related chunks into meaningful connections
    connections = []
    seen_mats = set()
    
    # We take the top related results which now have AI 'reasons'
    for r in related:
        m_id = r.get("material_id")
        if m_id and m_id != material_id and m_id not in seen_mats:
            mat_obj = db.query(StudyMaterial).filter(StudyMaterial.id == m_id).first()
            if mat_obj:
                connections.append({
                    "filename": mat_obj.filename,
                    "reason":   r.get("reason", "Semantic conceptual link found."),
                    "score":    round(1.0 - (r.get("score", 0.5)), 2), # Convert distance to similarity
                    "snippet":  r.get("chunk_text", "")[:200] + "..."
                })
                seen_mats.add(m_id)
        if len(connections) >= 4:
            break

    # 2. Persist to StudyMaterial
    mat = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
    if mat:
        mat.connections = connections
        db.commit()

    state["connections"] = connections
    await _push(state, "connections", "done", f"Synthesized {len(connections)} specific cross-material links")
    return state

async def _push(state: dict, step: str, status: str, message: str):
    q = state.get("progress_queue")
    if q:
        await q.put({"step": step, "status": status, "message": message})

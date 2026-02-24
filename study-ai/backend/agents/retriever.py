"""StudyAI — FAISS semantic retriever agent node."""


async def retrieve_node(state: dict) -> dict:
    """
    Find related content from other materials using FAISS similarity search.
    Searches using the first 10 chunk embeddings.
    Results exclude the current material to avoid self-retrieval.
    """
    embeddings  = state.get("embeddings", [])
    user_id     = state.get("user_id")
    material_id = state.get("material_id")

    if not embeddings or not user_id:
        state["related"] = []
        return state

    await _push(state, "retrieve", "running", "Searching related knowledge…")
    from tools.faiss_store import FAISSStore
    from database import StudyMaterial
    import os
    from langchain_groq import ChatGroq

    _llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.1,
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
    )

    db = state.get("db")
    mat = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first() if db else None
    ctx = f"File: {mat.filename}\nSummary: {mat.summary[:200]}" if mat and mat.summary else ""

    store = FAISSStore(user_id)
    store.load()

    seen_ids = set()
    related  = []

    for emb in embeddings[:5]:
        results = store.search(query_embedding=emb, top_k=3, exclude_material=material_id)
        for r in results:
            vid = r.get("_vector_id")
            if vid and vid not in seen_ids:
                seen_ids.add(vid)
                chunk = r.get("chunk_text", "")
                fname = r.get("filename", "Existing Doc")
                try:
                    p = f"Why does this chunk from '{fname}': '{chunk[:200]}' relate to my current study on: '{ctx}'? 20 words max."
                    r["reason"] = _llm.invoke(p).content.strip().replace('"', '')
                except Exception:
                    r["reason"] = "Related conceptual context found."
                related.append(r)

    state["related"] = related[:10]
    await _push(state, "retrieve", "done", f"Found {len(state['related'])} related segments with AI explanations")
    return state


async def _push(state: dict, step: str, status: str, message: str):
    q = state.get("progress_queue")
    if q:
        await q.put({"step": step, "status": status, "message": message})

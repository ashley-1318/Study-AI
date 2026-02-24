"""StudyAI — Quiz generation agent node."""
from datetime import datetime


async def quiz_node(state: dict) -> dict:
    """
    Generate quiz questions for the top 8 extracted concepts.
    Persists a Quiz row with questions JSON (answers stripped for frontend).
    """
    concepts:   list = state.get("concepts", [])
    material_id      = state.get("material_id")
    user_id          = state.get("user_id")
    db               = state.get("db")

    if not concepts or not db:
        state["questions"] = []
        return state

    await _push(state, "quiz", "running", "Generating quiz questions…")

    from tools.quiz_tool import generate_questions
    from tools.embedder import generate_embedding
    from tools.faiss_store import FAISSStore
    from database import Quiz

    store = FAISSStore(user_id)
    store.load()

    all_questions = []
    for concept in concepts[:8]:
        # RAG: Search for relevant context using concept name
        emb = generate_embedding(concept["name"])
        results = store.search(query_embedding=emb, top_k=3, exclude_material=None)
        context = "\n".join([r.get("chunk_text", "") for r in results if r.get("material_id") == material_id])

        qs = await generate_questions(
            concept_name=concept["name"],
            concept_def=concept.get("definition", ""),
            context=context,
            difficulty="adaptive",
            count=2,
        )
        all_questions.extend(qs)

    # Save quiz to DB (with answers — frontend receives stripped version)
    quiz = Quiz(
        user_id     = user_id,
        material_id = material_id,
        questions   = all_questions,
        difficulty  = "adaptive",
        created_at  = datetime.utcnow(),
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    state["questions"]   = all_questions
    state["pipeline_quiz_id"] = quiz.id

    await _push(state, "quiz", "done", f"Generated {len(all_questions)} questions")
    return state


async def _push(state: dict, step: str, status: str, message: str):
    q = state.get("progress_queue")
    if q:
        await q.put({"step": step, "status": status, "message": message})

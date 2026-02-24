"""StudyAI — Summarizer agent node using Groq LLM."""
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.5,
    groq_api_key=os.getenv("GROQ_API_KEY", ""),
)


async def summarize_node(state: dict) -> dict:
    """
    Generate a hierarchical Markdown summary of the document.
    Uses the first chunks + extracted concept list as context.
    Saves summary text back to the StudyMaterial row in SQLite.
    """
    chunks:    list = state.get("chunks", [])
    concepts:  list = state.get("concepts", [])
    material_id     = state.get("material_id")
    db              = state.get("db")
    filename: str   = state.get("filename", "document")

    if not chunks:
        state["summary"] = ""
        return state

    await _push(state, "summarize", "running", "Generating AI summary…")

    # Build context from first 5 chunks + concept names
    context_chunks = "\n\n---\n\n".join(chunks[:5])
    concept_names  = ", ".join(c["name"] for c in concepts[:20])

    prompt = f"""You are an expert tutor for StudyAI. Create a comprehensive, well-structured summary.

Document: {filename}
Key concepts identified: {concept_names}

Content sample:
\"\"\"
{context_chunks[:4000]}
\"\"\"

Write a hierarchical Markdown summary suitable for exam revision:
- Use ## for main sections
- Use ### for subsections
- Include bullet points for key facts
- Add a "Key Concepts" section at the end
- Be concise but complete (400-600 words)"""

    try:
        response = await _llm.ainvoke(prompt)
        summary  = response.content.strip()
    except Exception as exc:
        summary = f"## Summary of {filename}\n\nSummary generation failed: {exc}\n\n**Concepts:** {concept_names}"

    # Persist summary to DB
    if db and material_id:
        from database import StudyMaterial
        mat = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
        if mat:
            mat.summary = summary
            db.commit()

    state["summary"] = summary
    await _push(state, "summarize", "done", "Summary generated")
    return state


async def _push(state: dict, step: str, status: str, message: str):
    q = state.get("progress_queue")
    if q:
        await q.put({"step": step, "status": status, "message": message})

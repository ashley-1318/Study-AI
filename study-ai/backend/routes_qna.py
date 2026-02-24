"""StudyAI — RAG-powered Q&A (Ask AI) routes."""
import os
import logging
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langchain_groq import ChatGroq

from auth import get_current_user
from database import User, get_db, StudyMaterial
from tools.faiss_store import FAISSStore
from tools.embedder import generate_embedding

router = APIRouter(tags=["qna"])
log = logging.getLogger(__name__)

_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY", ""),
)

class QuestionRequest(BaseModel):
    question: str
    material_id: Optional[str] = None # Optional filter to a single doc

class SourceInfo(BaseModel):
    filename: str
    snippet: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]

@router.post("/qna/ask")
async def ask_ai(
    body: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    RAG-powered Q&A: Search FAISS across all user materials and answer based on found context.
    """
    if not body.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    # 1. Retrieve context via FAISS
    store = FAISSStore(current_user.id)
    try:
        store.load()
    except Exception:
        raise HTTPException(404, "No study materials indexed yet. Please upload content first.")

    emb = generate_embedding(body.question)
    search_results = store.search(query_embedding=emb, top_k=5, exclude_material=None)
    
    if not search_results:
        return {
            "success": True,
            "data": {
                "answer": "I couldn't find any relevant information in your study materials to answer this question. Try uploading more content or rephrasing.",
                "sources": []
            },
            "error": None
        }

    # 2. Build context string and track sources
    context_chunks = []
    sources_map = {} # mat_id -> filename
    final_sources = []
    
    unique_sources = set()

    for res in search_results:
        mat_id = res.get("material_id")
        text = res.get("chunk_text", "")
        
        if mat_id not in sources_map:
            mat = db.query(StudyMaterial).filter(StudyMaterial.id == mat_id).first()
            sources_map[mat_id] = mat.filename if mat else "Unknown Material"
        
        fname = sources_map[mat_id]
        context_chunks.append(f"Source [{fname}]:\n{text}")
        
        if fname not in unique_sources:
            final_sources.append({"filename": fname, "snippet": text[:150] + "..."})
            unique_sources.add(fname)

    context_str = "\n\n".join(context_chunks)

    # 3. Call LLM to synthesize answer
    prompt = f"""You are 'StudyAI', a premium AI study companion. Your task is to answer the user's question based ONLY on the provided study context.

USER QUESTION: {body.question}

STUDY CONTEXT FROM USER'S MATERIALS:
\"\"\"
{context_str}
\"\"\"

INSTRUCTIONS:
1. Answer the question accurately using the snippets above.
2. If the answer is not in the context, say: "Based on your current materials, I don't have enough information to answer that accurately. However, here is what I found related to [topic]..."
3. Keep the tone academic, helpful, and concise. 
4. Use Markdown for formatting (bolding, lists).
5. Mention the source filenames in your answer if relevant.
"""

    try:
        response = await _llm.ainvoke(prompt)
        answer = response.content
    except Exception as e:
        log.error("Ask AI failed: %s", e)
        raise HTTPException(500, "AI synthesis failed. Try again later.")

    return {
        "success": True,
        "data": {
            "answer": answer,
            "sources": final_sources[:3]
        },
        "error": None
    }

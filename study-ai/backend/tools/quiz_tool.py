"""StudyAI — LLM-based quiz question generator tool."""
import json
import os
import re

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY", ""),
)


async def generate_questions(
    concept_name: str,
    concept_def: str,
    difficulty: str = "medium",
    count: int = 2,
    context: str = "",
) -> list:
    """
    Generate MCQ, true/false, or fill-in-the-blank questions for a concept.
    Returns a list of question dicts validated for required fields.
    """
    context_str = f"\nRelevant study context:\n\"\"\"\n{context[:3000]}\n\"\"\"\n" if context else ""

    prompt = f"""You are an expert educator creating quiz questions for StudyAI.
    Return ONLY a valid JSON array. Each item must have:
    - "type": "mcq"
    - "question": string
    - "options": list of exactly 4 strings
    - "answer": string (must be one of the options)
    - "explanation": string explaining the correct answer
    - "concept": "{concept_name}"

    Concept: {concept_name}
    Definition: {concept_def}
    {context_str}
    Difficulty: {difficulty}
    Number of questions: {count}

    Generate exactly {count} Multiple Choice Questions (mcq).
    IMPORTANT: Base the questions on the provided study context if available.
    """

    response = await _llm.ainvoke(prompt)
    raw = response.content.strip()

    # Parse JSON robustly
    json_match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not json_match:
        return []
    try:
        questions = json.loads(json_match.group())
    except json.JSONDecodeError:
        return []

    # Validate and sanitize each question
    valid = []
    for q in questions:
        if all(k in q for k in ("type", "question", "answer")):
            q.setdefault("options", [])
            q.setdefault("explanation", "")
            q.setdefault("concept", concept_name)
            valid.append(q)

    return valid

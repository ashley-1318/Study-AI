"""StudyAI — LLM-based quiz question generator tool."""
import asyncio
import json
import os
import re

from dotenv import load_dotenv
from groq import RateLimitError
from langchain_groq import ChatGroq

load_dotenv()

_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY", ""),  # type: ignore
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

    # Retry logic for rate limit errors
    max_retries = 5
    response = None
    for attempt in range(max_retries):
        try:
            response = await _llm.ainvoke(prompt)
            break  # Success, exit retry loop
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise  # Last attempt failed, re-raise the error
            # Extract wait time from error message (default to exponential backoff)
            wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
            print(f"⚠️  Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            # For other errors, fail immediately
            print(f"❌ Quiz generation error: {e}")
            return []
    
    if response is None:
        return []
    
    # Handle response content which can be a list or string
    if isinstance(response.content, list):
        raw = str(response.content[0]).strip() if response.content else ""
    else:
        raw = str(response.content).strip()

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

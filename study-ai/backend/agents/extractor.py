"""StudyAI — Concept extractor agent node using Groq LLM."""
import json
import logging
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

log = logging.getLogger(__name__)

_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY", ""),
)


def _sanitize_json(raw: str) -> str:
    """Replace smart/curly quotes and other common LLM JSON artifacts."""
    # Replace curly/smart quotes with straight quotes
    raw = raw.replace('\u201c', '"').replace('\u201d', '"')
    raw = raw.replace('\u2018', "'").replace('\u2019', "'")
    raw = raw.replace('\u2032', "'").replace('\u2033', '"')
    # Remove trailing commas before ] or }
    raw = re.sub(r',\s*([\]}])', r'\1', raw)
    return raw


def _extract_json_array(raw: str):
    """Try to extract and parse the first JSON array from LLM output."""
    # Sanitize smart quotes first
    raw = _sanitize_json(raw)
    # Greedy match: find the outermost [ ... ]
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError as e:
        log.warning("JSON parse failed (%s), attempting repair...", e)
        # Try stripping the block and reparsing
        block = match.group()
        # Remove embedded newlines inside string values that break JSON
        block = re.sub(r'(?<!\\)\n', ' ', block)
        try:
            return json.loads(block)
        except Exception:
            return None


async def extract_node(state: dict) -> dict:
    """
    Extract named concepts + definitions from document chunks.
    Processes up to 20 chunks to stay within LLM token limits.
    Deduplicates by concept name and persists to SQLite.
    """
    chunks: list = state.get("chunks", [])
    material_id  = state.get("material_id")
    user_id      = state.get("user_id")
    db           = state.get("db")

    if not chunks or not material_id or not db:
        state["concepts"] = []
        return state

    await _push(state, "extract", "running", "Extracting concepts with AI…")

    all_concepts: dict[str, dict] = {}  # name → dict

    for chunk in chunks[:20]:  # limit to first 20 chunks
        prompt = f"""You are an AI tutor extracting key concepts from study material for StudyAI.

Text chunk:
\"\"\"
{chunk[:2000]}
\"\"\"

Extract 3-7 important concepts. Return ONLY a valid JSON array:
[
  {{
    "name": "Concept Name",
    "definition": "Clear, concise definition (1-2 sentences)",
    "related_concepts": ["Related Concept 1", "Related Concept 2"]
  }}
]"""

        try:
            response = await _llm.ainvoke(prompt)
            raw = response.content.strip()
            items = _extract_json_array(raw)
            if not items:
                log.warning("No JSON array found in LLM response for chunk %d", chunks.index(chunk))
                log.debug("LLM raw output: %s", raw[:500])
                continue
            for item in items:
                name = item.get("name", "").strip()
                if name and name not in all_concepts:
                    all_concepts[name] = {
                        "name":             name,
                        "definition":       item.get("definition", ""),
                        "related_concepts": item.get("related_concepts", []),
                    }
        except Exception as exc:
            log.warning("Chunk extraction failed: %s", exc)
            continue  # skip bad chunks

    # Persist to database
    saved_concepts = []
    from database import Concept
    for data in all_concepts.values():
        concept = Concept(
            material_id      = material_id,
            user_id          = user_id,
            name             = data["name"],
            definition       = data["definition"],
            related_concepts = data["related_concepts"],
            mastery_score    = 0.0,
            next_review      = datetime.utcnow(),
        )
        db.add(concept)
        saved_concepts.append(data)

    db.commit()

    state["concepts"] = saved_concepts
    await _push(state, "extract", "done", f"Extracted {len(saved_concepts)} unique concepts")
    return state


async def _push(state: dict, step: str, status: str, message: str):
    q = state.get("progress_queue")
    if q:
        await q.put({"step": step, "status": status, "message": message})

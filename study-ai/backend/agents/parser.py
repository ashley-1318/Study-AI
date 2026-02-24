"""StudyAI — Document parser agent node."""
import asyncio
import re
from typing import Any


def _extract_text(file_path: str, ext: str) -> str:
    """Synchronous text extraction — safe to run in a thread executor."""
    if ext == "pdf":
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = "\n\n".join(page.get_text() for page in doc)
        doc.close()
        return text
    elif ext in ("docx", "doc"):
        from docx import Document
        doc = Document(file_path)
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    else:  # txt, md
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()


async def parse_node(state: dict) -> dict:
    """
    Parse uploaded file into text chunks.
    Supports PDF (PyMuPDF), DOCX (python-docx), and plain TXT/MD.
    Chunks must be at least 100 characters to be useful for embedding.
    """
    file_path: str = state.get("file_path", "")
    filename: str  = state.get("filename", "")

    await _push(state, "parse", "running", f"Parsing {filename}…")

    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else "txt"

    try:
        # Run blocking file I/O in a thread so the event loop stays free
        loop = asyncio.get_event_loop()
        raw_text = await loop.run_in_executor(None, _extract_text, file_path, ext)
    except Exception as exc:
        state["error"] = f"Parse error: {exc}"
        await _push(state, "parse", "error", f"Failed to parse: {exc}")
        return state

    # Split on blank lines, keep chunks ≥100 chars
    raw_chunks = [c.strip() for c in re.split(r"\n\s*\n", raw_text)]
    chunks = [c for c in raw_chunks if len(c) >= 100]

    # If no chunks (e.g. very short doc), treat full text as one chunk
    if not chunks and raw_text.strip():
        chunks = [raw_text.strip()]

    # Sub-split any chunk that is too large (>1500 chars) into ~800-char pieces
    # by splitting on sentence boundaries so context stays coherent
    MAX_CHUNK = 1500
    SPLIT_SIZE = 800
    refined: list[str] = []
    for chunk in chunks:
        if len(chunk) <= MAX_CHUNK:
            refined.append(chunk)
        else:
            # Split on sentence-end punctuation
            sentences = re.split(r"(?<=[.!?])\s+", chunk)
            current = ""
            for sent in sentences:
                if len(current) + len(sent) + 1 <= SPLIT_SIZE:
                    current = (current + " " + sent).strip()
                else:
                    if current:
                        refined.append(current)
                    current = sent
            if current:
                refined.append(current)
    chunks = [c for c in refined if len(c) >= 100]
    if not chunks and raw_text.strip():
        chunks = [raw_text.strip()]

    state["chunks"]   = chunks
    state["metadata"] = {"filename": filename, "chunk_count": len(chunks)}

    # Update material chunk_count in DB
    db = state.get("db")
    material_id = state.get("material_id")
    if db and material_id:
        from database import StudyMaterial
        mat = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
        if mat:
            mat.chunk_count = len(chunks)
            db.commit()

    await _push(state, "parse", "done", f"Extracted {len(chunks)} chunks from {filename}")
    return state


async def _push(state: dict, step: str, status: str, message: str):
    """Send progress to the WebSocket queue if available."""
    import asyncio
    q = state.get("progress_queue")
    if q:
        await q.put({"step": step, "status": status, "message": message})

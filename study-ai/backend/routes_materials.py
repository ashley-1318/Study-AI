"""StudyAI — Material upload, listing, retrieval and deletion routes."""
import asyncio
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from auth import get_current_user
from database import Concept, LearningEvent, StudyMaterial, User, get_db

router = APIRouter(tags=["materials"])

UPLOAD_PATH = os.getenv("UPLOAD_PATH", "./uploads")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_TYPES = {"pdf", "docx", "txt", "md"}

# WebSocket progress queues — shared with main.py
progress_queues: dict[str, asyncio.Queue] = {}


@router.post("/materials/upload")
async def upload_material(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accept file upload, validate, save to disk, create DB record,
    then kick off background AI pipeline and return immediately.
    """
    ext = (file.filename or "").lower().rsplit(".", 1)[-1]
    if ext not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type '{ext}' not supported. Use: {ALLOWED_TYPES}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File exceeds 20 MB limit")

    # Save to disk
    user_upload_dir = os.path.join(UPLOAD_PATH, current_user.id)
    os.makedirs(user_upload_dir, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(user_upload_dir, safe_name)
    with open(file_path, "wb") as f:
        f.write(content)

    # Create DB record
    material = StudyMaterial(
        user_id   = current_user.id,
        filename  = file.filename,
        file_path = file_path,          # store absolute path for pipeline re-runs
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    # Log upload event
    event = LearningEvent(
        user_id    = current_user.id,
        event_type = "upload",
        result     = {"material_id": material.id, "filename": file.filename},
        timestamp  = datetime.utcnow(),
    )
    db.add(event)
    db.commit()

    # Create progress queue for WebSocket streaming
    q: asyncio.Queue = asyncio.Queue()
    progress_queues[material.id] = q

    # Background task: run full AI pipeline
    background_tasks.add_task(
        run_pipeline_task,
        material_id  = material.id,
        user_id      = current_user.id,
        file_path    = file_path,
        filename     = file.filename,
        queue        = q,
    )

    return {
        "success": True,
        "data": {"material_id": material.id, "status": "processing"},
        "error": None,
    }


async def run_pipeline_task(
    material_id: str,
    user_id: str,
    file_path: str,
    filename: str,
    queue: asyncio.Queue,
):
    """Run the agent pipeline in background, streaming progress to WebSocket queue."""
    import logging
    import traceback
    log = logging.getLogger("pipeline")
    log.setLevel(logging.DEBUG)

    from database import SessionLocal, StudyMaterial
    from agents.graph import PipelineState, run_pipeline

    log.info("🚀 Pipeline starting for material_id=%s file=%s", material_id, filename)
    db = SessionLocal()
    try:
        state = PipelineState(
            file_path       = file_path,
            filename        = filename,
            user_id         = user_id,
            material_id     = material_id,
            db              = db,
            progress_queue  = queue,
        )
        await run_pipeline(state)
        log.info("✅ Pipeline complete for material_id=%s", material_id)

        # Signal completion
        await queue.put({"step": "analytics", "status": "done", "message": "✅ All agents complete"})

    except Exception as exc:
        tb = traceback.format_exc()
        log.error("❌ Pipeline FAILED for material_id=%s:\n%s", material_id, tb)
        print(f"\n[PIPELINE ERROR] material_id={material_id}\n{tb}", flush=True)
        # Mark material as error
        try:
            mat = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
            if mat:
                mat.status = "error"
                db.commit()
        except Exception:
            pass
        await queue.put({"step": "error", "status": "error", "message": str(exc)})
    finally:
        db.close()
        # Remove queue after a delay to allow WS to drain
        await asyncio.sleep(5)
        progress_queues.pop(material_id, None)


@router.get("/materials/")
async def list_materials(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all study materials for the authenticated user."""
    materials = (
        db.query(StudyMaterial)
        .filter(StudyMaterial.user_id == current_user.id)
        .order_by(StudyMaterial.created_at.desc())
        .all()
    )
    result = []
    for m in materials:
        concept_count = db.query(Concept).filter(Concept.material_id == m.id).count()
        result.append({
            "id":            m.id,
            "filename":      m.filename,
            "status":        m.status,
            "chunk_count":   m.chunk_count,
            "concept_count": concept_count,
            "created_at":    m.created_at.isoformat() if m.created_at else None,
            "updated_at":    m.updated_at.isoformat() if m.updated_at else None,
        })

    return {"success": True, "data": result, "error": None}


@router.get("/materials/{material_id}")
async def get_material(
    material_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single material with its concepts."""
    mat = db.query(StudyMaterial).filter(
        StudyMaterial.id == material_id,
        StudyMaterial.user_id == current_user.id,
    ).first()
    if not mat:
        raise HTTPException(404, "Material not found")

    concepts = db.query(Concept).filter(Concept.material_id == material_id).all()
    return {
        "success": True,
        "data": {
            "id":           mat.id,
            "filename":     mat.filename,
            "status":       mat.status,
            "chunk_count":  mat.chunk_count,
            "summary":      mat.summary,
            "connections":  mat.connections or [],
            "created_at":   mat.created_at.isoformat() if mat.created_at else None,
            "concepts": [
                {
                    "id":            c.id,
                    "name":          c.name,
                    "definition":    c.definition,
                    "mastery_score": c.mastery_score,
                    "next_review":   c.next_review.isoformat() if c.next_review else None,
                }
                for c in concepts
            ],
        },
        "error": None,
    }


@router.get("/materials/{material_id}/summary")
async def get_summary(
    material_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the AI-generated summary and concept list for a material."""
    mat = db.query(StudyMaterial).filter(
        StudyMaterial.id == material_id,
        StudyMaterial.user_id == current_user.id,
    ).first()
    if not mat:
        raise HTTPException(404, "Material not found")

    concepts = db.query(Concept).filter(Concept.material_id == material_id).all()
    return {
        "success": True,
        "data": {
            "summary":     mat.summary or "Summary not yet generated.",
            "connections": mat.connections or [],
            "filename":    mat.filename,
            "concepts": [
                {
                    "id":               c.id,
                    "name":             c.name,
                    "definition":       c.definition,
                    "mastery_score":    c.mastery_score,
                    "related_concepts": c.related_concepts or [],
                }
                for c in concepts
            ],
        },
        "error": None,
    }


@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a material: remove file from disk, FAISS index, and DB cascade."""
    mat = db.query(StudyMaterial).filter(
        StudyMaterial.id == material_id,
        StudyMaterial.user_id == current_user.id,
    ).first()
    if not mat:
        raise HTTPException(404, "Material not found")

    # Delete from FAISS
    try:
        from tools.faiss_store import FAISSStore
        store = FAISSStore(current_user.id)
        store.load()
        store.delete_by_material(material_id)
    except Exception:
        pass  # best-effort

    # Delete file from disk
    try:
        upload_dir = os.path.join(UPLOAD_PATH, current_user.id)
        for fname in os.listdir(upload_dir):
            if mat.filename in fname:
                os.remove(os.path.join(upload_dir, fname))
                break
    except Exception:
        pass

    # DB cascade handles concepts, quiz_answers, etc.
    db.delete(mat)
    db.commit()

    return {"success": True, "data": {"deleted": material_id}, "error": None}

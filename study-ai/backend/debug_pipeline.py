"""Debug script: re-runs the pipeline on the most recent stuck material."""
import sys, os, asyncio, traceback, logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("debug_pipeline")

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal, StudyMaterial
from agents.graph import PipelineState, run_pipeline

async def main():
    db = SessionLocal()
    try:
        # Find the most recent 'processing' material
        mat = (
            db.query(StudyMaterial)
            .filter(StudyMaterial.status == "processing")
            .order_by(StudyMaterial.created_at.desc())
            .first()
        )
        if not mat:
            log.info("No stuck materials found — all done!")
            return

        log.info("Re-running pipeline for: %s (id=%s)", mat.filename, mat.id)
        log.info("user_id=%s", mat.user_id)

        # Resolve file path — stored in DB for new uploads, scan disk for old ones
        file_path = getattr(mat, "file_path", None)
        if not file_path or not os.path.exists(file_path):
            import glob
            upload_dir = os.path.join("./uploads", mat.user_id)
            pattern = os.path.join(upload_dir, f"*_{mat.filename}")
            matches = glob.glob(pattern)
            if not matches:
                # Try any file in the user's upload dir
                matches = glob.glob(os.path.join(upload_dir, "*.pdf")) + \
                          glob.glob(os.path.join(upload_dir, "*.docx")) + \
                          glob.glob(os.path.join(upload_dir, "*.txt"))
                matches.sort(key=os.path.getmtime, reverse=True)
            if not matches:
                log.error("Cannot find uploaded file for material '%s'", mat.filename)
                return
            file_path = matches[0]
            log.info("Resolved file_path from disk: %s", file_path)
        else:
            log.info("file_path from DB: %s", file_path)

        # Reset chunk count so we can verify it changes
        mat.chunk_count = 0
        db.commit()

        state = PipelineState(
            file_path      = file_path,
            filename       = mat.filename,
            user_id        = mat.user_id,
            material_id    = mat.id,
            db             = db,
            progress_queue = None,
        )

        log.info("▶ Running pipeline…")
        result = await run_pipeline(state)

        chunks   = result.get("chunks", [])
        concepts = result.get("concepts", [])
        error    = result.get("error", None)

        if error:
            log.error("Pipeline returned error: %s", error)
        else:
            log.info("✅ SUCCESS: %d chunks, %d concepts", len(chunks), len(concepts))
            for i, c in enumerate(concepts[:10], 1):
                name = c.get("name", "?") if isinstance(c, dict) else getattr(c, "name", str(c))
                log.info("  Concept %d: %s", i, name)

        # Verify DB was updated
        db.refresh(mat)
        log.info("DB chunk_count=%d | status=%s", mat.chunk_count, mat.status)

    except Exception:
        log.error("CRASHED:\n%s", traceback.format_exc())
    finally:
        db.close()

asyncio.run(main())

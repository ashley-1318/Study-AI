"""StudyAI — FastAPI application entry point with WebSocket pipeline streaming."""
import asyncio
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="StudyAI",
    version="1.0.0",
    description="Multi-Agent Adaptive Learning System",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and mount routers
from routes_auth      import router as auth_router
from routes_materials import router as materials_router, progress_queues
from routes_quiz      import router as quiz_router
from routes_concepts  import router as concepts_router
from routes_revision  import router as revision_router
from routes_analytics import router as analytics_router
from routes_history   import router as history_router
from routes_qna       import router as qna_router

app.include_router(auth_router)                           # /auth/*
app.include_router(materials_router, prefix="/api/v1")   # /api/v1/materials/*
app.include_router(quiz_router,      prefix="/api/v1")   # /api/v1/quiz/*
app.include_router(concepts_router,  prefix="/api/v1")   # /api/v1/concepts/*
app.include_router(revision_router,  prefix="/api/v1")   # /api/v1/revision/*
app.include_router(analytics_router, prefix="/api/v1")   # /api/v1/analytics/*
app.include_router(history_router,   prefix="/api/v1")   # /api/v1/history/*
app.include_router(qna_router,       prefix="/api/v1")   # /api/v1/qna/*


# ─── WebSocket: Pipeline Progress Stream ─────────────────────────────────────

@app.websocket("/ws/pipeline/{material_id}")
async def ws_pipeline(
    websocket: WebSocket,
    material_id: str,
    token: str = Query(...),
):
    """
    Stream real-time pipeline progress for a material upload.
    Client connects immediately after POST /materials/upload.
    Messages: {"step": str, "status": str, "message": str}
    Closes when analytics step is done or error occurs.
    """
    from auth import decode_token
    try:
        decode_token(token)  # validate JWT; raises 401 on failure
    except Exception:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    # Wait for the queue to be created (upload handler does this)
    timeout = 10
    while material_id not in progress_queues and timeout > 0:
        await asyncio.sleep(0.5)
        timeout -= 0.5

    if material_id not in progress_queues:
        await websocket.send_json({"step": "error", "status": "error", "message": "Queue not found"})
        await websocket.close()
        return

    q: asyncio.Queue = progress_queues[material_id]

    try:
        while True:
            try:
                # Wait up to 120s for next message, then send a keepalive ping
                msg = await asyncio.wait_for(q.get(), timeout=120)
                await websocket.send_json(msg)

                # Close stream when pipeline is complete
                if msg.get("step") == "analytics" and msg.get("status") == "done":
                    break
                if msg.get("step") == "error":
                    break

            except asyncio.TimeoutError:
                await websocket.send_json({"step": "ping", "status": "running", "message": "Still processing…"})

    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()


# ─── Startup ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    from database import init_db
    init_db()

    upload_path = os.getenv("UPLOAD_PATH", "./uploads")
    faiss_path  = os.getenv("FAISS_INDEX_PATH", "./faiss_indexes")
    os.makedirs(upload_path, exist_ok=True)
    os.makedirs(faiss_path,  exist_ok=True)

    print("✅ StudyAI backend ready on http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status":  "ok",
        "service": "StudyAI",
        "db":      "sqlite",
        "llm":     "groq/llama-3.3-70b-versatile",
    }

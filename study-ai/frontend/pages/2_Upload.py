"""StudyAI — Upload Material page."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import time

st.set_page_config(page_title="StudyAI — Upload", page_icon="📚", layout="wide")

from streamlit_auth import require_auth, show_user_sidebar
from api_client import api_get, api_delete, ws_url

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Lora:ital@0;1&display=swap');
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0b0c14}
section[data-testid="stSidebar"]{background:#0d0e1a!important;border-right:1px solid #1e2135!important}
h1,h2,h3{font-family:Syne,sans-serif!important;color:#e8e9f0!important}
.stButton>button{background:rgba(31,184,154,0.08)!important;border:1px solid rgba(31,184,154,0.4)!important;
    color:#1fb89a!important;border-radius:12px!important;font-family:Syne,sans-serif!important;
    font-weight:700!important;transition:all 0.3s!important}
.stButton>button:hover{background:#1fb89a!important;color:#0b0c14!important}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#1fb89a,#15a085)!important;
    color:#0b0c14!important;border:none!important;box-shadow:0 4px 20px rgba(31,184,154,0.35)!important}
[data-testid="stFileUploader"]{
    background:rgba(18,20,31,0.4)!important;
    border:2px dashed rgba(31,184,154,0.5)!important;
    border-radius:20px!important;
    padding:40px!important;
    transition:all 0.3s ease!important;
}
</style>""", unsafe_allow_html=True)

user = require_auth()

# ── Back button
_back_col, _title_col = st.columns([1, 9])
with _back_col:
    if st.button("← Back", key="back_upload"):
        st.switch_page("app.py")

with st.sidebar:
    st.markdown("""<div style='display:flex;align-items:center;gap:12px;padding:16px 8px 24px;
        border-bottom:1px solid #1e2135;margin-bottom:16px'>
        <span style='font-size:28px'>📚</span>
        <span style='font-family:Syne,sans-serif;font-weight:900;font-size:24px'>
            <span style='color:#1fb89a'>Study</span><span style='color:#e8a020'>AI</span>
        </span></div>""", unsafe_allow_html=True)
    st.page_link("app.py",               label="🏠 Home")
    st.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_Upload.py",    label="📤 Upload Material")
    st.page_link("pages/3_Quiz.py",      label="❓ Adaptive Quiz")
    st.page_link("pages/4_Summaries.py", label="📝 Summaries")
    st.page_link("pages/5_Revision.py",  label="🔄 Revision Planner")
    st.page_link("pages/6_Analytics.py", label="📈 Analytics")
    show_user_sidebar()

st.title("📤 Upload Study Material")
st.markdown("""
<p style='color:#7a7f9a;font-size:16px;margin-bottom:32px;font-family:Lora,serif;font-style:italic'>
    Upload PDFs, Word documents, or text files. Our multi-agent AI pipeline will extract
    concepts, generate summaries, and prepare adaptive quizzes — automatically.
</p>
""", unsafe_allow_html=True)

# ── Upload Section ─────────────────────────────────────────────────────────────
col_upload, col_info = st.columns([3, 2], gap="large")

with col_upload:
    uploaded_file = st.file_uploader(
        "Drop your file here or click to browse",
        type=["pdf", "docx", "txt", "md"],
        key="file_uploader",
        label_visibility="collapsed",
    )

    if uploaded_file:
        st.markdown(f"""
        <div style='padding:16px;background:rgba(31,184,154,0.08);border:1px solid rgba(31,184,154,0.3);
            border-radius:12px;margin:12px 0'>
            <b style='color:#1fb89a'>📄 {uploaded_file.name}</b><br>
            <small style='color:#7a7f9a'>{uploaded_file.size / 1024:.1f} KB · {uploaded_file.type}</small>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Upload & Process with AI", type="primary", use_container_width=True, key="upload_btn"):
            with st.spinner("Uploading…"):
                import requests as _req
                token = st.session_state.get("access_token", "")
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    resp = _req.post(
                        "http://localhost:8000/api/v1/materials/upload",
                        headers={"Authorization": f"Bearer {token}"},
                        files=files,
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        material_id = data.get("data", {}).get("material_id")
                        st.success("✅ File uploaded! AI pipeline is running…")

                        # ── Live progress polling ───────────────────────────
                        progress_area = st.empty()
                        status_text   = st.empty()
                        MAX_POLLS     = 90   # 90 × 4s = 6 minutes max
                        consecutive_errors = 0

                        for attempt in range(MAX_POLLS):
                            time.sleep(4)  # poll every 4 seconds

                            check = None
                            try:
                                check_resp = _req.get(
                                    f"http://localhost:8000/api/v1/materials/{material_id}",
                                    headers={"Authorization": f"Bearer {token}"},
                                    timeout=35,
                                )
                                if check_resp.status_code == 200:
                                    check = check_resp.json()
                                    consecutive_errors = 0
                            except Exception:
                                consecutive_errors += 1
                                if consecutive_errors <= 5:
                                    status_text.info(f"⏳ Backend busy processing… (attempt {attempt+1})")
                                    continue
                                else:
                                    status_text.error("❌ Backend not responding after multiple retries.")
                                    break

                            if not check or not check.get("success"):
                                continue

                            mat_data    = check["data"]
                            status      = mat_data.get("status", "processing")
                            chunk_count = mat_data.get("chunk_count", 0)
                            concepts    = mat_data.get("concepts", [])
                            n_concepts  = len(concepts)

                            # Infer completed pipeline steps from DB state
                            steps = [
                                ("📄 Parsing document",      chunk_count > 0),
                                ("🧠 Extracting concepts",   n_concepts  > 0),
                                ("🔢 Generating embeddings", n_concepts  > 0),
                                ("📦 Indexing into FAISS",   n_concepts  > 0),
                                ("🔍 Retrieving context",    n_concepts  > 0),
                                ("✍️  Generating summary",   status == "done"),
                                ("❓  Preparing quiz questions", status == "done"),
                                ("📅  Building revision plan",  status == "done"),
                                ("📈  Computing analytics",     status == "done"),
                            ]
                            rows = "".join(
                                f"<div style='padding:5px 0;color:#e8e9f0'>{'✅' if done else '⏳'} {label}</div>"
                                for label, done in steps
                            )
                            progress_area.markdown(f"""
                            <div style='background:rgba(18,20,31,0.8);border:1px solid #1e2135;
                                border-radius:16px;padding:24px;margin-top:12px'>
                                <b style='color:#1fb89a;font-family:Syne,sans-serif;font-size:16px'>
                                    Pipeline Status
                                </b>
                                <div style='margin:12px 0'>{rows}</div>
                                <hr style='border:0;border-top:1px solid #1e2135;margin:12px 0'>
                                <small style='color:#7a7f9a'>
                                    {chunk_count} chunks extracted · {n_concepts} concepts found
                                </small>
                            </div>""", unsafe_allow_html=True)

                            if status == "done":
                                st.balloons()
                                progress_area.empty()
                                st.success(f"🎉 Done! **{chunk_count}** chunks · **{n_concepts}** concepts extracted.")
                                
                                # Show Connections immediately after upload
                                connections = mat_data.get("connections", [])
                                if connections:
                                    st.markdown("### 🔗 Related Knowledge Found")
                                    for conn in connections:
                                        st.markdown(f"""
                                        <div style='background:rgba(31,184,154,0.05);border:1px solid rgba(31,184,154,0.2);
                                            border-radius:12px;padding:16px;margin-bottom:12px'>
                                            <b style='color:#1fb89a'>📎 {conn.get("filename")}</b><br>
                                            <p style='color:#e8e9f0;font-size:14px;margin-top:4px'><i>"{conn.get("reason")}"</i></p>
                                        </div>""", unsafe_allow_html=True)

                                if st.button("📊 View Dashboard", key="post_upload_dash"):
                                    st.switch_page("pages/1_Dashboard.py")
                                break
                            elif status == "error":
                                st.error("❌ Processing failed. Please try re-uploading.")
                                break
                        else:
                            st.warning("⏰ Processing is taking longer than expected. Check the Dashboard for status.")
                    else:
                        st.error(f"Upload failed ({resp.status_code}): {resp.text[:300]}")
                except Exception as e:
                    st.error(f"Upload error: {e}")

with col_info:
    st.markdown("""
    <div style='background:rgba(18,20,31,0.8);border:1px solid #1e2135;border-radius:20px;padding:28px'>
        <h3 style='margin-top:0;color:#e8e9f0;font-family:Syne,sans-serif'>🤖 AI Pipeline</h3>
        <div style='margin-top:8px'>
    """, unsafe_allow_html=True)

    pipeline_steps = [
        ("📄", "Parse",     "Extract raw text from PDF/DOCX/TXT"),
        ("🧠", "Extract",   "LLM identifies key concepts & definitions"),
        ("🔢", "Embed",     "Sentence-transformer encodes each chunk"),
        ("📦", "Index",     "FAISS vector store for semantic search"),
        ("✍️", "Summarize", "Hierarchical Markdown summary generated"),
        ("❓", "Quiz Gen",  "Adaptive MCQ, T/F and fill-in questions"),
        ("📅", "Revision",  "SM-2 spaced repetition schedule built"),
        ("📈", "Analytics", "Mastery tracking and learning events"),
    ]
    for icon, name, desc in pipeline_steps:
        st.markdown(f"""
        <div style='display:flex;gap:14px;margin-bottom:14px;align-items:flex-start'>
            <span style='font-size:20px;min-width:28px'>{icon}</span>
            <div>
                <b style='color:#1fb89a;font-family:Syne,sans-serif;font-size:14px'>{name}</b><br>
                <small style='color:#7a7f9a;font-family:Lora,serif'>{desc}</small>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
        <hr style='border-top:1px solid #1e2135;margin-top:8px'>
        <p style='color:#3a3f5a;font-size:12px;margin:8px 0 0;text-align:center'>
            Max size: 20 MB · Formats: PDF, DOCX, TXT, MD
        </p>
    </div>""", unsafe_allow_html=True)

# ── Your Materials ─────────────────────────────────────────────────────────────
st.markdown("<br>### 📋 Your Materials", unsafe_allow_html=True)
col_h, col_r = st.columns([8, 2])
with col_r:
    if st.button("🔄 Refresh", key="upload_refresh"):
        st.rerun()

mats_resp = api_get("/materials/")
materials = mats_resp.get("data", []) if mats_resp else []

if not materials:
    st.markdown("<p style='color:#7a7f9a'>No materials uploaded yet.</p>", unsafe_allow_html=True)
else:
    for m in materials:
        status = m.get("status", "unknown")
        status_cfg = {
            "done":       ("#1fb89a", "✅ DONE"),
            "processing": ("#3b82f6", "⏳ PROCESSING"),
            "error":      ("#ef4444", "❌ ERROR"),
        }
        color, label = status_cfg.get(status, ("#7a7f9a", status.upper()))
        st.markdown(f"""
        <div style='padding:16px 24px;background:rgba(18,20,31,0.6);border-radius:14px;
            margin-bottom:10px;border:1px solid #1e2135;border-left:4px solid {color}'>
            <div style='display:flex;justify-content:space-between;align-items:center'>
                <div>
                    <b style='color:#e8e9f0'>{m["filename"]}</b><br>
                    <small style='color:#7a7f9a'>
                        {m.get("chunk_count",0)} chunks · {m.get("concept_count",0)} concepts ·
                        {(m.get("created_at") or "")[:10]}
                    </small>
                </div>
                <span style='color:{color};font-size:11px;font-family:JetBrains Mono,monospace;
                    background:{color}22;padding:4px 14px;border-radius:100px;border:1px solid {color}44'>
                    {label}
                </span>
            </div>
        </div>""", unsafe_allow_html=True)

        bc1, bc2, bc3, _ = st.columns([2, 2, 2, 4])
        with bc1:
            if status == "done" and st.button("📝 Summary", key=f"u_sum_{m['id']}", use_container_width=True):
                st.session_state["view_summary_id"] = m["id"]
                st.switch_page("pages/4_Summaries.py")
        with bc2:
            if status == "done" and st.button("❓ Quiz", key=f"u_quiz_{m['id']}", use_container_width=True):
                st.session_state["quiz_material_id"] = m["id"]
                st.switch_page("pages/3_Quiz.py")
        with bc3:
            if st.button("🗑️ Delete", key=f"u_del_{m['id']}", use_container_width=True):
                st.session_state[f"udel_{m['id']}"] = True

        if st.session_state.get(f"udel_{m['id']}"):
            st.warning(f"Delete **{m['filename']}**?")
            cc1, cc2, _ = st.columns([1, 1, 4])
            with cc1:
                if st.button("✅ Yes", key=f"udy_{m['id']}", use_container_width=True):
                    res = api_delete(f"/materials/{m['id']}")
                    if res and res.get("success"):
                        st.session_state.pop(f"udel_{m['id']}", None)
                        st.rerun()
            with cc2:
                if st.button("❌ No", key=f"udn_{m['id']}", use_container_width=True):
                    st.session_state.pop(f"udel_{m['id']}", None)
                    st.rerun()

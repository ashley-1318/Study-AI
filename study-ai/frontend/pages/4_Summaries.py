"""StudyAI — Summaries page with full material concept browser."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

st.set_page_config(page_title="StudyAI — Summaries", page_icon="📚", layout="wide")

from streamlit_auth import require_auth, show_user_sidebar
from api_client import api_get

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap');
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0b0c14}
section[data-testid="stSidebar"]{background:#0d0e1a!important;border-right:1px solid #1e2135!important}
h1,h2,h3{font-family:Syne,sans-serif!important;color:#e8e9f0!important}
.stButton>button{background:rgba(31,184,154,0.08)!important;border:1px solid rgba(31,184,154,0.4)!important;color:#1fb89a!important;border-radius:12px!important;font-family:Syne,sans-serif!important;font-weight:700!important;transition:all 0.3s!important}
.stButton>button:hover{background:#1fb89a!important;color:#0b0c14!important}
</style>""", unsafe_allow_html=True)

user = require_auth()

with st.sidebar:
    st.markdown("""<div style='display:flex;align-items:center;gap:12px;padding:16px 8px 24px;border-bottom:1px solid #1e2135;margin-bottom:16px'>
        <span style='font-size:28px'>📚</span>
        <span style='font-family:Syne,sans-serif;font-weight:900;font-size:24px'>
            <span style='color:#1fb89a'>Study</span><span style='color:#e8a020'>AI</span>
        </span></div>""", unsafe_allow_html=True)
    st.page_link("app.py",              label="🏠 Home")
    st.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_Upload.py",    label="📤 Upload Material")
    st.page_link("pages/3_Quiz.py",      label="❓ Adaptive Quiz")
    st.page_link("pages/4_Summaries.py", label="📝 Summaries")
    st.page_link("pages/5_Revision.py",  label="🔄 Revision Planner")
    st.page_link("pages/6_Analytics.py", label="📈 Analytics")
    show_user_sidebar()

# ── Back button
_back_col, _title_col = st.columns([1, 9])
with _back_col:
    if st.button("← Back", key="back_summaries"):
        st.switch_page("app.py")

st.title("📝 Summaries & Concepts — StudyAI")

mats_resp = api_get("/materials/")
materials = mats_resp.get("data", []) if mats_resp else []
done_mats = [m for m in materials if m.get("status") == "done"]

if not done_mats:
    st.markdown("""
        <div style='padding:48px;background:rgba(18,20,31,0.5);border-radius:20px;text-align:center;border:1px dashed #1e2135'>
            <p style='color:#7a7f9a;font-size:18px'>No processed materials yet.<br>Upload a file to see summaries here.</p>
        </div>""", unsafe_allow_html=True)
    if st.button("📤 Go to Upload", key="goto_upload_4"):
        st.switch_page("pages/2_upload.py")
else:
    col_left, col_right = st.columns([3, 7], gap="large")

    with col_left:
        st.markdown("### 📑 Materials")

        # Check if pre-selected via session
        preselect_id = st.session_state.pop("view_summary_id", None)

        for m in done_mats:
            is_sel = preselect_id == m["id"] or st.session_state.get("selected_mat_id") == m["id"]
            border_color = "#1fb89a" if is_sel else "#1e2135"
            st.markdown(f"""
                <div style='padding:14px;background:rgba(18,20,31,0.7);border-radius:12px;
                    margin-bottom:10px;border:2px solid {border_color};cursor:pointer'>
                    <b style='color:#e8e9f0;font-size:13px'>{m["filename"]}</b><br>
                    <small style='color:#7a7f9a'>{m.get("chunk_count",0)} chunks · {m.get("concept_count",0)} concepts</small>
                </div>""", unsafe_allow_html=True)
            if st.button(f"View →", key=f"view_mat_{m['id']}", use_container_width=True):
                st.session_state["selected_mat_id"] = m["id"]
                st.rerun()

        if preselect_id:
            st.session_state["selected_mat_id"] = preselect_id

    with col_right:
        selected_id = st.session_state.get("selected_mat_id")
        if not selected_id and done_mats:
            selected_id = done_mats[0]["id"]
            st.session_state["selected_mat_id"] = selected_id

        if selected_id:
            resp = api_get(f"/materials/{selected_id}/summary")
            if resp and resp.get("success"):
                sdata = resp["data"]
                st.markdown(f"### 📄 {sdata['filename']}")
                st.markdown("<hr style='border-top:1px solid #1e2135'>", unsafe_allow_html=True)

                # Summary
                with st.expander("📝 AI-Generated Summary", expanded=True):
                    summary = sdata.get("summary", "No summary generated yet.")
                    st.markdown(f"""
                        <div style='background:rgba(18,20,31,0.5);border-radius:12px;padding:24px;
                            border-left:4px solid #1fb89a;font-family:Lora,serif;line-height:1.8;color:#e8e9f0'>
                            {summary}
                        </div>""", unsafe_allow_html=True)

                # Cross-Material Connections
                connections = sdata.get("connections", [])
                if connections:
                    with st.expander("🌐 Cross-Material Intelligence", expanded=True):
                        st.markdown("<p style='color:#7a7f9a;margin-bottom:16px'>How this material relates to your previous studies:</p>", unsafe_allow_html=True)
                        for conn in connections:
                            if isinstance(conn, str):
                                # Fallback for old string-based connections
                                st.markdown(f"""
                                    <div style='background:rgba(31,184,154,0.05);border:1px solid rgba(31,184,154,0.2);
                                        border-radius:12px;padding:16px;margin-bottom:12px;display:flex;gap:12px;align-items:start'>
                                        <div style='font-size:20px'>🔗</div>
                                        <div style='color:#e8e9f0;font-size:14px;line-height:1.5'>{conn}</div>
                                    </div>""", unsafe_allow_html=True)
                            else:
                                # New structured connections
                                score = conn.get("score", 0)
                                st.markdown(f"""
                                    <div style='background:rgba(31,184,154,0.05);border:1px solid rgba(31,184,154,0.2);
                                        border-radius:16px;padding:20px;margin-bottom:16px'>
                                        <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>
                                            <b style='color:#1fb89a;font-size:14px'>📎 {conn["filename"]}</b>
                                            <span style='color:#7a7f9a;font-size:11px'>Similarity: {score:.2f}</span>
                                        </div>
                                        <p style='color:#e8e9f0;font-size:14px;margin-bottom:12px;font-style:italic'>"{conn["reason"]}"</p>
                                        <div style='padding:10px;background:rgba(0,0,0,0.2);border-radius:8px'>
                                            <small style='color:#5a5f7a'>Preview: {conn["snippet"]}</small>
                                        </div>
                                    </div>""", unsafe_allow_html=True)

                # Concepts
                st.markdown("#### 🔑 Extracted Concepts")
                concepts = sdata.get("concepts", [])
                if not concepts:
                    st.markdown("<p style='color:#7a7f9a'>No concepts extracted yet.</p>", unsafe_allow_html=True)
                else:
                    # Sort by mastery ascending (weakest first)
                    concepts.sort(key=lambda c: c.get("mastery_score", 0))
                    for c in concepts:
                        score = c.get("mastery_score", 0)
                        score_pct = score * 100
                        color = "#22c55e" if score >= 0.7 else "#e8a020" if score >= 0.4 else "#ef4444"

                        with st.expander(f"{'🔴' if score < 0.4 else '🟡' if score < 0.7 else '🟢'} {c['name']} — {score_pct:.0f}% mastery"):
                            col_def, col_meta = st.columns([7, 3])
                            with col_def:
                                st.markdown(f"**Definition:** {c.get('definition','No definition available.')}")
                                if c.get("related_concepts"):
                                    rels = [r for r in c["related_concepts"] if isinstance(r, str)]
                                    if rels:
                                        tags = " ".join(f"<span style='background:#1e2135;color:#7a7f9a;padding:3px 10px;border-radius:20px;font-size:12px;margin:2px'>{r}</span>" for r in rels)
                                        st.markdown(f"**Related:** {tags}", unsafe_allow_html=True)
                            with col_meta:
                                # Mastery bar
                                st.markdown(f"""
                                    <div style='background:#1e2135;height:8px;border-radius:8px;margin:8px 0'>
                                        <div style='background:{color};width:{score_pct:.0f}%;height:100%;border-radius:8px'></div>
                                    </div>
                                    <small style='color:{color};font-weight:bold'>{score_pct:.0f}% mastered</small>
                                """, unsafe_allow_html=True)

                                if c.get("next_review"):
                                    review_date = c["next_review"][:10]
                                    st.markdown(f"<small style='color:#7a7f9a'>📅 Next review: {review_date}</small>", unsafe_allow_html=True)

                # Semantic search
                st.markdown("<br>#### 🔍 Semantic Search", unsafe_allow_html=True)
                search_q = st.text_input("Search related concepts…", placeholder="e.g. backpropagation gradient", key="semantic_search")
                if search_q:
                    results = api_get("/concepts/related", params={"query": search_q})
                    chunks = results.get("data", []) if results else []
                    if chunks:
                        for ch in chunks:
                            st.markdown(f"""
                                <div style='padding:12px;background:rgba(18,20,31,0.5);border-radius:10px;
                                    margin-bottom:8px;border-left:3px solid #3b82f6'>
                                    <small style='color:#7a7f9a'>Score: {ch.get("score",0):.3f}</small><br>
                                    <p style='color:#e8e9f0;margin:4px 0'>{ch.get("chunk_text","")}</p>
                                </div>""", unsafe_allow_html=True)
                    else:
                        st.info("No related chunks found. Try a different query.")

"""StudyAI — Dashboard page: all materials + status."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="StudyAI — Dashboard", page_icon="📚", layout="wide")

from streamlit_auth import require_auth, show_user_sidebar
from api_client import api_get, api_delete

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap');
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0b0c14}
section[data-testid="stSidebar"]{background:#0d0e1a!important;border-right:1px solid #1e2135!important}
h1,h2,h3{font-family:Syne,sans-serif!important;color:#e8e9f0!important}
.stButton>button{background:rgba(31,184,154,0.08)!important;border:1px solid rgba(31,184,154,0.4)!important;
    color:#1fb89a!important;border-radius:12px!important;font-family:Syne,sans-serif!important;
    font-weight:700!important;transition:all 0.3s!important}
.stButton>button:hover{background:#1fb89a!important;color:#0b0c14!important}
</style>""", unsafe_allow_html=True)

user = require_auth()

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

if st.button("← Back", key="back_to_home"):
    st.switch_page("app.py")

st.title("📊 Dashboard — Your Materials")

# ── Header actions ────────────────────────────────────────────────────────────
col_title, col_btn = st.columns([8, 2])
with col_btn:
    if st.button("🔄 Refresh", key="dash_refresh", use_container_width=True):
        st.rerun()

# ── Fetch materials ───────────────────────────────────────────────────────────
resp = api_get("/materials/")
materials = resp.get("data", []) if resp else []

if not materials:
    st.markdown("""
    <div style='padding:64px;background:rgba(18,20,31,0.5);border-radius:20px;
        text-align:center;border:1px dashed #1e2135;margin-top:24px'>
        <div style='font-size:64px;margin-bottom:16px'>📂</div>
        <h3 style='color:#e8e9f0;margin:0 0 8px'>No materials yet</h3>
        <p style='color:#7a7f9a'>Upload a PDF, DOCX, or text file to get started.</p>
    </div>""", unsafe_allow_html=True)
    if st.button("📤 Upload your first material", key="dash_upload_btn"):
        st.switch_page("pages/2_Upload.py")
else:
    # ── Summary metrics ────────────────────────────────────────────────────────
    done = [m for m in materials if m.get("status") == "done"]
    proc = [m for m in materials if m.get("status") == "processing"]
    err  = [m for m in materials if m.get("status") == "error"]
    total_concepts = sum(m.get("concept_count", 0) for m in done)

    # Fetch additional analytics for the gauge
    analytics_resp = api_get("/analytics/overview")
    overview_data = analytics_resp.get("data", {}) if analytics_resp else {}
    mastery_pct = overview_data.get("overall_mastery", 0)

    # Layout: Metrics (Left) + Gauge (Right)
    col_metrics, col_gauge = st.columns([3, 2], gap="large")

    with col_metrics:
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("📂 Total Files", len(materials))
        with m2: st.metric("✅ Done", len(done))
        with m3: st.metric("🔑 Concepts", total_concepts)
        
        m4, m5, m6 = st.columns(3)
        with m4: st.metric("⏳ Processing", len(proc))
        with m5: st.metric("🔥 Streak", f"{overview_data.get('study_streak_days', 0)} days")
        with m6: st.metric("❌ Error", len(err))

    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode  = "gauge+number",
            value = round(mastery_pct, 1),
            title = {
                "text": "Knowledge Mastery",
                "font": {"color": "white", "size": 16, "family": "Syne"}
            },
            number = {
                "suffix": "%",
                "font":   {"color": "#1fb89a", "size": 36, "family": "Syne"}
            },
            gauge = {
                "axis": {
                    "range":     [0, 100],
                    "tickcolor": "white",
                    "tickwidth": 1,
                },
                "bar":   {"color": "#1fb89a", "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0,  40], "color": "#3a1211"}, # Deep red
                    {"range": [40, 70], "color": "#3a2a0d"}, # Deep amber
                    {"range": [70, 100],"color": "#0d3a24"}, # Deep green
                ],
                "threshold": {
                    "line": {"color": "#e8a020", "width": 4},
                    "thickness": 0.75,
                    "value": mastery_pct,
                },
            },
        ))
        fig_gauge.update_layout(
            template      = "plotly_dark",
            paper_bgcolor = "rgba(0,0,0,0)",
            plot_bgcolor  = "rgba(0,0,0,0)",
            font_color    = "white",
            height        = 240,
            margin        = dict(t=40, b=10, l=20, r=20),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Material cards ─────────────────────────────────────────────────────────
    for m in materials:
        status = m.get("status", "unknown")
        status_cfg = {
            "done":       ("#1fb89a", "✅ DONE"),
            "processing": ("#3b82f6", "⏳ PROCESSING"),
            "error":      ("#ef4444", "❌ ERROR"),
        }
        color, label = status_cfg.get(status, ("#7a7f9a", status.upper()))

        with st.container():
            st.markdown(f"""
            <div style='background:rgba(18,20,31,0.8);border:1px solid #1e2135;border-radius:16px;
                padding:20px 24px;margin-bottom:12px;border-left:4px solid {color}'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                    <div>
                        <b style='color:#e8e9f0;font-size:16px'>{m["filename"]}</b><br>
                        <small style='color:#7a7f9a'>
                            {m.get("chunk_count",0)} chunks ·
                            {m.get("concept_count",0)} concepts ·
                            {(m.get("created_at") or "")[:10]}
                        </small>
                    </div>
                    <span style='color:{color};font-size:11px;font-family:JetBrains Mono,monospace;
                        background:{color}22;padding:4px 14px;border-radius:100px;border:1px solid {color}44;
                        white-space:nowrap'>
                        {label}
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)

            btn_cols = st.columns([2, 2, 2, 4])
            with btn_cols[0]:
                if status == "done":
                    if st.button("📝 Summary", key=f"d_sum_{m['id']}", use_container_width=True):
                        st.session_state["view_summary_id"] = m["id"]
                        st.switch_page("pages/4_Summaries.py")
            with btn_cols[1]:
                if status == "done":
                    if st.button("❓ Quiz", key=f"d_quiz_{m['id']}", use_container_width=True):
                        st.session_state["quiz_material_id"] = m["id"]
                        st.switch_page("pages/3_Quiz.py")
            with btn_cols[2]:
                if st.button("🗑️ Delete", key=f"d_del_{m['id']}", use_container_width=True):
                    st.session_state[f"confirm_del_{m['id']}"] = True

            # Delete confirmation
            if st.session_state.get(f"confirm_del_{m['id']}"):
                st.warning(f"⚠️ Delete **{m['filename']}**? This cannot be undone.")
                conf_cols = st.columns([1, 1, 4])
                with conf_cols[0]:
                    if st.button("Yes, delete", key=f"confirm_yes_{m['id']}", use_container_width=True):
                        result = api_delete(f"/materials/{m['id']}")
                        if result and result.get("success"):
                            st.success("Deleted!")
                            st.session_state.pop(f"confirm_del_{m['id']}", None)
                            st.rerun()
                with conf_cols[1]:
                    if st.button("Cancel", key=f"confirm_no_{m['id']}", use_container_width=True):
                        st.session_state.pop(f"confirm_del_{m['id']}", None)
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📤 Upload More Materials", key="dash_upload_more", use_container_width=False):
        st.switch_page("pages/2_Upload.py")

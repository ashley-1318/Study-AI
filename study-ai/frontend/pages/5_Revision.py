"""StudyAI — Revision Planner with SM-2 review interface."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

st.set_page_config(page_title="StudyAI — Revision", page_icon="📚", layout="wide")

from streamlit_auth import require_auth, show_user_sidebar
from api_client import api_get, api_post

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
    st.page_link("pages/1_dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_upload.py",    label="📤 Upload Material")
    st.page_link("pages/3_quiz.py",      label="❓ Adaptive Quiz")
    st.page_link("pages/4_summaries.py", label="📝 Summaries")
    st.page_link("pages/5_revision.py",  label="🔄 Revision Planner")
    st.page_link("pages/6_analytics.py", label="📈 Analytics")
    show_user_sidebar()

# ── Back button
_back_col, _title_col = st.columns([1, 9])
with _back_col:
    if st.button("← Back", key="back_revision"):
        st.switch_page("app.py")

st.title("🔄 Revision Planner — StudyAI")
st.markdown("<p style='color:#7a7f9a'>SM-2 spaced repetition: rate each concept to schedule optimal review intervals.</p>", unsafe_allow_html=True)

resp = api_get("/revision/plan")
if not resp or not resp.get("success"):
    st.info("No revision plan yet — upload and process materials to begin.")
else:
    data      = resp["data"]
    due_today = data.get("due_today", [])
    all_weak  = data.get("all_weak", [])

    # Summary banner
    col_d, col_w, col_p = st.columns([2, 2, 6])
    col_d.metric("📅 Due Today",  len(due_today))
    col_w.metric("🔴 Weak Concepts", len(all_weak))
    
    with col_p:
        with st.expander("⚙️ Adaptive Plan Settings", expanded=False):
            strat = st.radio("Study Strategy", ["balanced", "aggressive", "light"], horizontal=True, 
                             help="Aggressive focuses on more concepts, Light focuses only on critical ones.")
            days = st.slider("Planning Horizon (Days)", 1, 30, 7)
            if st.button("🚀 Regenerate My Study Roadmap", use_container_width=True):
                with st.spinner("Calculating optimal study path..."):
                    gen_resp = api_post("/revision/generate", json={
                        "strategy": strat,
                        "days_available": days
                    })
                    if gen_resp and gen_resp.get("success"):
                        st.success("✨ Your adaptive study plan has been updated!")
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📅 Due Today", "🔴 All Weak Concepts"])

    def _quality_buttons(concept_id: str, tab_key: str):
        """Render SM-2 quality rating buttons (0-5)."""
        labels = {
            0: ("❌ Blackout",   "#ef4444"),
            2: ("😓 Hard",       "#f97316"),
            3: ("✅ OK",         "#e8a020"),
            4: ("💪 Good",       "#3b82f6"),
            5: ("⭐ Perfect",    "#1fb89a"),
        }
        cols = st.columns(len(labels))
        for i, (quality, (label, color)) in enumerate(labels.items()):
            with cols[i]:
                if st.button(label, key=f"rev_{tab_key}_{concept_id}_{quality}", use_container_width=True):
                    result = api_post("/revision/complete", json={
                        "concept_id": concept_id,
                        "quality":    quality,
                    })
                    if result and result.get("success"):
                        new_mastery = result["data"]["mastery_score"]
                        next_rev    = result["data"]["next_review"][:10]
                        st.success(f"✅ Updated! Mastery: {new_mastery*100:.0f}% · Next: {next_rev}")
                        st.rerun()
                    else:
                        st.error("Failed to update. Check backend.")

    with tab1:
        if not due_today:
            st.markdown("""
                <div style='padding:48px;background:rgba(31,184,154,0.06);border-radius:20px;text-align:center;border:1px solid rgba(31,184,154,0.2)'>
                    <p style='font-size:48px'>🎉</p>
                    <h3 style='color:#1fb89a'>All caught up for today!</h3>
                    <p style='color:#7a7f9a'>Come back tomorrow to review scheduled concepts.</p>
                </div>""", unsafe_allow_html=True)
        else:
            for concept in due_today:
                score = concept.get("mastery_score", 0)
                color = "#ef4444" if score < 0.4 else "#e8a020" if score < 0.7 else "#22c55e"
                st.markdown(f"""
<div style='padding:20px;background:rgba(18,20,31,0.7);border-radius:16px;margin-bottom:16px;border:1px solid #1e2135;border-left:4px solid {color}'>
<h4 style='margin:0 0 4px;color:#e8e9f0'>{concept["name"]}</h4>
<div style='background:#1e2135;height:6px;border-radius:6px;margin:8px 0'>
<div style='background:{color};width:{score*100:.0f}%;height:100%;border-radius:6px'></div>
</div>
<small style='color:#7a7f9a'>Mastery: {score*100:.0f}% · Interval: {concept.get("interval_days",1)}d · Due: {concept.get("next_review","")[:10]}</small>
<br><small style='color:#1fb89a;font-weight:bold'>📅 Scheduled Plan: {concept.get("scheduled_day", "No specific day")}</small>
<div style='margin-top:16px;padding-top:16px;border-top:1px solid #1e2135'>
<p style='color:#1fb89a;font-size:12px;font-weight:bold;margin-bottom:8px'>💡 SMART AI GUIDANCE</p>
{f"<div style='background:rgba(31,184,154,0.1);padding:12px;border-radius:10px;margin-bottom:12px;border:1px solid rgba(31,184,154,0.3)'><p style='color:#e8e9f0;font-size:13px;margin:0'>✨ <b>Study Tip:</b> {concept['ai_tip']}</p></div>" if concept.get("ai_tip") else ""}
<p style='color:#e8e9f0;font-size:13px;margin-bottom:12px'>
📄 Focus on: <b>{concept.get("filename", "Material")}</b>
</p>
{" ".join([f"<span style='background:rgba(239,68,68,0.1);color:#ef4444;border:1px solid rgba(239,68,68,0.3);padding:2px 8px;border-radius:10px;font-size:11px;margin-right:6px'>🔗 {link}</span>" for link in concept.get("linked_concepts", [])])}
<div style='background:rgba(18,20,31,0.5);border-radius:8px;padding:12px;margin-top:12px;font-size:13px;color:#7a7f9a;border-left:2px solid #1fb89a'>
<i>Suggested re-read:</i><br>
{'...<br>...'.join(concept.get("suggested_chunks", ["Check full text for more context."]))}
</div>
</div>
</div>""", unsafe_allow_html=True)
                st.markdown("**⭐ Rate your recall (SM-2):**")
                _quality_buttons(concept["id"], "due")
                st.markdown("<br>", unsafe_allow_html=True)

    with tab2:
        if not all_weak:
            st.markdown("<p style='color:#7a7f9a'>No weak concepts — great job!</p>", unsafe_allow_html=True)
        else:
                for concept in all_weak:
                    score = concept.get("mastery_score", 0)
                    color = "#ef4444" if score < 0.4 else "#e8a020"
                    
                    # Safe snippet extraction
                    chunks = concept.get("suggested_chunks", [])
                    snippet = chunks[0][:200] if chunks else "Check original material for context."
                    
                    with st.expander(f"{'🔴' if score < 0.4 else '🟡'} {concept['name']} — {score*100:.0f}%"):
                        st.markdown(f"""
<div style='background:#1e2135;height:6px;border-radius:6px;margin:8px 0'>
<div style='background:{color};width:{score*100:.0f}%;height:100%;border-radius:6px'></div>
</div>
<p>Mastery: <b style='color:{color}'>{score*100:.0f}%</b> · 
Next review: <b style='color:#7a7f9a'>{concept.get("next_review","")[:10]}</b> · 
Interval: {concept.get("interval_days",1)} day(s)</p>
<div style='margin-top:12px;padding:12px;background:rgba(30,33,53,0.3);border-radius:12px;border:1px solid #1e2135'>
<p style='color:#1fb89a;font-size:12px;font-weight:bold;margin-bottom:8px'>💡 SMART AI GUIDANCE</p>
<p style='color:#e8e9f0;font-size:13px;margin-bottom:8px'>
📄 Source: <b>{concept.get("filename", "Material")}</b>
</p>
{" ".join([f"<span style='background:rgba(239,68,68,0.1);color:#ef4444;border:1px solid rgba(239,68,68,0.3);padding:2px 8px;border-radius:10px;font-size:11px;margin-right:6px'>🔗 {link}</span>" for link in concept.get("linked_concepts", [])])}
<div style='margin-top:10px;font-size:12px;color:#7a7f9a;line-height:1.4'>
<i>Key Snippet:</i> "{snippet}..."
</div>
</div>""", unsafe_allow_html=True)
                    st.markdown("**Rate your recall (SM-2):**")
                    _quality_buttons(concept["id"], "weak")

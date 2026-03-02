"""StudyAI — Main entry point / Home page."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="StudyAI — Your AI Study Companion",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

from streamlit_auth import require_auth, show_user_sidebar
from api_client import api_get

# ── Premium Global CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800;900&family=Lora:ital,wght@0,400;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Page fade in ─────────────────────────── */
.main .block-container {
    animation: fadeSlideIn 0.35s ease;
}
@keyframes fadeSlideIn {
    from { opacity:0; transform:translateY(10px); }
    to   { opacity:1; transform:translateY(0); }
}

/* ── App Background ────────────────────────── */
.stApp {
    background: #0b0c14;
    background-image:
        radial-gradient(circle at 15% 25%, rgba(31,184,154,0.06) 0%, transparent 45%),
        radial-gradient(circle at 85% 75%, rgba(232,160,32,0.06) 0%, transparent 45%);
    background-attachment: fixed;
}
#MainMenu, footer, header { visibility: hidden }

/* ── Button Transitions & Glow ────────────────── */
.stButton > button {
    transition: all 0.2s ease !important;
    border-radius: 12px !important;
    border: 1px solid rgba(31,184,154,0.4) !important;
    background: rgba(31,184,154,0.06) !important;
    color: #1fb89a !important;
    font-family: Syne, sans-serif !important;
    font-weight: 700 !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(31,184,154,0.30) !important;
    border-color: #1fb89a !important;
    background: #1fb89a !important;
    color: #0b0c14 !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Expander card hover lift ─────────────── */
div[data-testid="stExpander"] {
    border: 1px solid #1e2135 !important;
    border-radius: 10px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
    background: #12141f !important;
}
div[data-testid="stExpander"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(31,184,154,0.12) !important;
    border-color: #1fb89a !important;
}

/* ── Metric gradient text ─────────────────── */
[data-testid="stMetricValue"] {
    background: linear-gradient(135deg, #1fb89a 0%, #e8a020 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-weight: 800 !important;
    font-family: Syne, sans-serif !important;
}

/* ── Progress bar teal gradient ───────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #1fb89a, #e8a020) !important;
    border-radius: 4px !important;
    transition: width 0.5s ease !important;
}

/* ── Sidebar dark polish ──────────────────── */
[data-testid="stSidebar"] {
    background: #080a12 !important;
    border-right: 1px solid #1e2135 !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    background: transparent !important;
    color: #a0aec0 !important;
    border: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1e2135 !important;
    color: #1fb89a !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Chat message styling ─────────────────── */
[data-testid="stChatMessage"] {
    background: #12141f !important;
    border: 1px solid #1e2135 !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
    transition: border-color 0.2s ease !important;
}
[data-testid="stChatMessage"]:hover {
    border-color: #1fb89a !important;
}

/* ── Input field focus glow ───────────────── */
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #1fb89a !important;
    box-shadow: 0 0 0 2px rgba(31,184,154,0.20) !important;
}

/* ── Selectbox hover ──────────────────────── */
.stSelectbox > div > div {
    border-color: #1e2135 !important;
    background: #12141f !important;
    transition: border-color 0.2s ease !important;
}
.stSelectbox > div > div:hover {
    border-color: #1fb89a !important;
}

/* ── Info / Success / Error box styling ───── */
.stAlert {
    border-radius: 10px !important;
    border-left-width: 4px !important;
}

/* ── Spinner color ────────────────────────── */
.stSpinner > div {
    border-top-color: #1fb89a !important;
}

/* ── Global Header gradient ────────────────── */
h1 {
    background: linear-gradient(135deg, #1fb89a, #e8a020);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-weight: 900 !important;
}
</style>
""", unsafe_allow_html=True)

user = require_auth()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style='display:flex;align-items:center;gap:12px;
        padding:16px 8px 24px;border-bottom:1px solid #1e2135;margin-bottom:16px'>
        <span style='font-size:28px'>📚</span>
        <span style='font-family:Syne,sans-serif;font-weight:900;font-size:24px'>
            <span style='color:#1fb89a'>Study</span><span style='color:#e8a020'>AI</span>
        </span></div>""", unsafe_allow_html=True)
    st.page_link("app.py",                label="🏠 Home")
    st.page_link("pages/1_Dashboard.py",  label="📊 Dashboard")
    st.page_link("pages/2_Upload.py",     label="📤 Upload Material")
    st.page_link("pages/3_Quiz.py",       label="❓ Adaptive Quiz")
    st.page_link("pages/4_Summaries.py",  label="📝 Summaries")
    st.page_link("pages/5_Revision.py",   label="🔄 Revision Planner")
    st.page_link("pages/6_Analytics.py",  label="📈 Analytics")
    st.page_link("pages/7_Ask_AI.py",     label="💬 Ask AI")
    show_user_sidebar()

# ── Hero ───────────────────────────────────────────────────────────────────────
name = user.get("name", "Learner").split()[0]
st.markdown(f"""
<div style='padding:48px 0 32px;border-bottom:1px solid #1e2135;margin-bottom:40px'>
    <p style='color:#7a7f9a;font-size:16px;margin:0 0 8px;font-family:Lora,serif;font-style:italic'>
        Welcome back,
    </p>
    <h1 style='margin:0;font-size:56px;font-weight:900;letter-spacing:-3px;
        background:linear-gradient(135deg,#1fb89a,#e8a020);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        {name} 👋
    </h1>
    <p style='color:#7a7f9a;font-size:18px;margin:12px 0 0;font-family:Lora,serif;font-style:italic'>
        Your adaptive AI study companion — ready to help you learn smarter.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Quick Stats ───────────────────────────────────────────────────────────────
mats_resp = api_get("/materials/")
materials = mats_resp.get("data", []) if mats_resp else []
done_mats = [m for m in materials if m.get("status") == "done"]
total_concepts = sum(m.get("concept_count", 0) for m in done_mats)
total_chunks = sum(m.get("chunk_count", 0) for m in done_mats)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("📂 Materials", len(materials))
with c2:
    st.metric("✅ Processed", len(done_mats))
with c3:
    st.metric("🔑 Concepts", total_concepts)
with c4:
    st.metric("📄 Chunks", total_chunks)

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature Cards ─────────────────────────────────────────────────────────────
st.markdown("### 🚀 What would you like to do?")
st.markdown("<br>", unsafe_allow_html=True)

feature_cards = [
    ("📊 Dashboard",  "1_Dashboard.py", "Overview of your learning progress and stats.", "#1fb89a", "📈"),
    ("📤 Upload",     "2_Upload.py",    "Add new PDFs or notes to your study library.", "#3b82f6", "📁"),
    ("❓ Quiz",       "3_Quiz.py",      "Test your knowledge with adaptive AI quizzes.", "#e8a020", "💡"),
    ("💬 Ask AI",     "7_Ask_AI.py",   "Chat with your documents and find answers.", "#8b5cf6", "💬"),
    ("📝 Summaries",  "4_Summaries.py", "Browse AI-generated summaries of your files.", "#ec4899", "📝"),
    ("🔄 Revision",   "5_Revision.py",  "Optimized spaced-repetition study plans.", "#f97316", "🔄"),
    ("📈 Analytics",  "6_Analytics.py", "Deep dives into your knowledge gaps and coverage.", "#1fb89a", "📊"),
]

# Grid Logic
cols_per_row = 3
for i in range(0, len(feature_cards), cols_per_row):
    cols = st.columns(cols_per_row, gap="medium")
    for j in range(cols_per_row):
        idx = i + j
        if idx < len(feature_cards):
            title, path, desc, color, icon = feature_cards[idx]
            with cols[j]:
                st.markdown(f"""
                <div style='background:rgba(18,20,31,0.8);border:1px solid #1e2135;border-radius:20px;
                    padding:32px;margin-bottom:12px;border-top:3px solid {color};
                    height: 220px; display: flex; flex-direction: column;
                    transition:all 0.3s ease; box-sizing: border-box;'>
                    <div style='font-size:36px;margin-bottom:12px'>{icon}</div>
                    <h3 style='margin:0 0 8px;font-family:Syne,sans-serif;color:#e8e9f0;font-size:20px'>{title}</h3>
                    <p style='color:#7a7f9a;font-size:14px;line-height:1.6;flex-grow:1'>{desc}</p>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Open {title.split()[1] if len(title.split()) > 1 else title}", key=f"btn_{idx}", use_container_width=True):
                    st.switch_page(f"pages/{path}")

# ── Recent Materials ──────────────────────────────────────────────────────────
if materials:
    st.markdown("<br>### 📋 Recent Materials", unsafe_allow_html=True)
    for m in materials[:3]:
        status = m.get("status", "unknown")
        status_colors = {
            "done":       ("#1fb89a", "✅"),
            "processing": ("#3b82f6", "⏳"),
            "error":      ("#ef4444", "❌"),
        }
        color, emoji = status_colors.get(status, ("#7a7f9a", "❓"))
        st.markdown(f"""
        <div style='padding:16px 24px;background:rgba(18,20,31,0.6);border-radius:14px;
            margin-bottom:10px;border:1px solid #1e2135;display:flex;justify-content:space-between;align-items:center'>
            <div>
                <b style='color:#e8e9f0;font-size:15px'>{m["filename"]}</b><br>
                <small style='color:#7a7f9a'>
                    {m.get("chunk_count",0)} chunks · {m.get("concept_count",0)} concepts ·
                    {(m.get("created_at") or "")[:10]}
                </small>
            </div>
            <span style='color:{color};font-size:13px;font-family:JetBrains Mono,monospace;
                background:{color}22;padding:4px 14px;border-radius:100px;border:1px solid {color}44'>
                {emoji} {status.upper()}
            </span>
        </div>
        """, unsafe_allow_html=True)

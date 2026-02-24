"""StudyAI — Ask AI: RAG-powered chat interface."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from streamlit_auth import require_auth, show_user_sidebar
from api_client import api_post

st.set_page_config(page_title="StudyAI — Ask AI", page_icon="💬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap');
#MainMenu,footer,header{visibility:hidden}
.stApp{background:#0b0c14}
section[data-testid="stSidebar"]{background:#0d0e1a!important;border-right:1px solid #1e2135!important}
h1,h2,h3,h4{font-family:Syne,sans-serif!important;color:#e8e9f0!important}

/* Chat bubble styling */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 20px 0;
}
.user-msg {
    align-self: flex-end;
    background: #1fb89a;
    color: #0b0c14;
    padding: 12px 18px;
    border-radius: 20px 20px 0 20px;
    max-width: 80%;
    font-size: 15px;
    box-shadow: 0 4px 15px rgba(31, 184, 154, 0.2);
}
.ai-msg {
    align-self: flex-start;
    background: #161826;
    color: #e8e9f0;
    padding: 18px;
    border-radius: 20px 20px 20px 0;
    max-width: 85%;
    font-size: 15px;
    border: 1px solid #1e2135;
    line-height: 1.6;
}
.source-tag {
    display: inline-block;
    background: rgba(232, 160, 32, 0.1);
    color: #e8a020;
    border: 1px solid rgba(232, 160, 32, 0.3);
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 12px;
    margin-top: 8px;
    font-weight: bold;
}
</style>""", unsafe_allow_html=True)

user = require_auth()

# ── Back button
_back_col, _title_col = st.columns([1, 9])
with _back_col:
    if st.button("← Back", key="back_qna"):
        st.switch_page("app.py")

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
    st.page_link("pages/7_Ask_AI.py",    label="💬 Ask AI Chat")
    show_user_sidebar()

st.title("💬 Ask Your Materials — StudyAI")
st.markdown("<p style='color:#7a7f9a'>Ask anything across all your uploaded PDFs, notes, and study guides. AI answers using your specific content.</p>", unsafe_allow_html=True)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Layout for chat and sources
col_chat, col_sources = st.columns([7, 3], gap="large")

with col_chat:
    # Display history
    chat_box = st.container()
    with chat_box:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='user-msg'>{msg['text']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ai-msg'>{msg['text']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Input area
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        u_input = st.text_input("Type your question here...", placeholder="e.g. What is the main difference between CNN and RNN in my notes?")
        sub = st.form_submit_button("Ask ✨", use_container_width=True)
        
        if sub and u_input:
            st.session_state.chat_history.append({"role": "user", "text": u_input})
            
            with st.spinner("AI is reading your materials..."):
                resp = api_post("/qna/ask", json={"question": u_input})
                
                if resp and resp.get("success"):
                    ans_data = resp["data"]
                    ai_text = ans_data["answer"]
                    sources = ans_data.get("sources", [])
                    st.session_state.chat_history.append({
                        "role": "ai", 
                        "text": ai_text,
                        "sources": sources
                    })
                    st.rerun()
                else:
                    st.error("Ask AI failed. Make sure you have uploaded materials first!")

with col_sources:
    st.markdown("### 🔍 Evidence Sources")
    st.markdown("<hr style='border-top:1px solid #1e2135;margin-top:0'>", unsafe_allow_html=True)
    
    # Show sources for the LAST AI message
    last_ai = next((m for m in reversed(st.session_state.chat_history) if m["role"] == "ai"), None)
    
    if last_ai and last_ai.get("sources"):
        for src in last_ai["sources"]:
            st.markdown(f"""
                <div style='background:rgba(18,20,31,0.5);border:1px solid #1e2135;
                    border-radius:12px;padding:16px;margin-bottom:12px'>
                    <span class='source-tag'>📄 {src['filename']}</span>
                    <p style='color:#7a7f9a;font-size:12px;margin-top:10px;line-height:1.4'>
                        "...{src['snippet']}..."
                    </p>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#7a7f9a;font-style:italic'>Ask a question to see where the information came from.</p>", unsafe_allow_html=True)

    if st.button("Clear Chat 🗑️", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

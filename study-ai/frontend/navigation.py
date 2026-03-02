"""Shared navigation component for all StudyAI pages."""
import streamlit as st

def show_navigation(current_page=None):
    """Display the standard sidebar navigation for all pages."""
    st.markdown("""<div style='display:flex;align-items:center;gap:12px;
        padding:16px 8px 24px;border-bottom:1px solid #1e2135;margin-bottom:16px'>
        <span style='font-size:28px'>📚</span>
        <span style='font-family:Syne,sans-serif;font-weight:900;font-size:24px'>
            <span style='color:#1fb89a'>Study</span><span style='color:#e8a020'>AI</span>
        </span></div>""", unsafe_allow_html=True)
    
    # Navigation links - use correct paths for Streamlit multipage apps
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_Dashboard.py", label="📊 Dashboard")
    st.page_link("pages/2_Upload.py", label="📤 Upload Material")
    st.page_link("pages/3_Quiz.py", label="❓ Adaptive Quiz")
    st.page_link("pages/4_Summaries.py", label="📝 Summaries")
    st.page_link("pages/5_Revision.py", label="🔄 Revision Planner")
    st.page_link("pages/6_Analytics.py", label="📈 Analytics")
    st.page_link("pages/7_Ask_AI.py", label="💬 Ask AI")

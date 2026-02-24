import streamlit as st
from datetime import datetime

def inject_css():
    """Injects full global CSS for a premium, interactive look."""
    st.markdown("""
    <style>
    /* Hide default Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* App background */
    .stApp { 
        background-color: #0b0c14;
        background-image: 
            radial-gradient(circle at 20% 20%, rgba(31, 184, 154, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 80% 80%, rgba(232, 160, 32, 0.05) 0%, transparent 40%);
        background-attachment: fixed;
    }
    
    section[data-testid="stSidebar"] {
        background: rgba(13, 14, 26, 0.95) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(30, 33, 53, 0.5) !important;
    }

    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

    /* Typography */
    h1, h2, h3 { 
        font-family: 'Syne', sans-serif !important;
        color: #e8e9f0 !important; 
        letter-spacing: -1.5px; 
        font-weight: 800 !important;
    }
    p, li, div, label, .stMarkdown { 
        font-family: 'Lora', serif !important;
        color: #e8e9f0 !important; 
        font-size: 16px;
    }
    code, .mono, [data-testid="stMarkdownContainer"] code { 
        font-family: 'JetBrains Mono', monospace !important; 
        background: #1e2135 !important;
        color: #1fb89a !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }

    /* Buttons - Glassmorphism & Neon */
    .stButton > button {
        background: rgba(31, 184, 154, 0.05) !important;
        border: 1px solid rgba(31, 184, 154, 0.4) !important;
        color: #1fb89a !important;
        border-radius: 12px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        padding: 10px 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 14px !important;
    }
    .stButton > button:hover {
        background: #1fb89a !important;
        color: #0b0c14 !important;
        box-shadow: 0 0 30px rgba(31, 184, 154, 0.4) !important;
        transform: translateY(-2px) scale(1.02) !important;
    }

    /* Primary button variant */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1fb89a 0%, #15a085 100%) !important;
        color: #0b0c14 !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(31, 184, 154, 0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(31, 184, 154, 0.5) !important;
    }

    /* Metric cards - Glassmorphism */
    [data-testid="metric-container"] {
        background: rgba(18, 20, 31, 0.6) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(30, 33, 53, 0.8) !important;
        border-left: 4px solid #1fb89a !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.3s ease;
    }
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: rgba(31, 184, 154, 0.4) !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        font-size: 38px !important;
        font-weight: 800 !important;
        color: #e8e9f0 !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    [data-testid="stMetricLabel"] {
        font-family: 'Syne', sans-serif !important;
        color: #7a7f9a !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600 !important;
    }

    /* Study Cards */
    .study-card {
        background: rgba(18, 20, 31, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(30, 33, 53, 1);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }
    .study-card:hover {
        border-color: rgba(31, 184, 154, 0.3);
        box-shadow: 0 15px 50px rgba(0,0,0,0.5);
    }

    /* Status badges */
    .badge {
        display:inline-block; padding:4px 14px;
        border-radius:100px; font-size:11px;
        font-family:'JetBrains Mono',monospace; font-weight:700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-done     { background: rgba(31, 184, 154, 0.1); color:#1fb89a; border: 1px solid rgba(31, 184, 154, 0.3); }
    .badge-pending  { background: rgba(232, 160, 32, 0.1); color:#e8a020; border: 1px solid rgba(232, 160, 32, 0.3); }
    .badge-error    { background: rgba(196, 64, 26, 0.1); color:#c4401a; border: 1px solid rgba(196, 64, 26, 0.3); }
    .badge-processing { background: rgba(59, 130, 246, 0.1); color:#3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(18, 20, 31, 0.4) !important;
        border: 2px dashed rgba(31, 184, 154, 0.5) !important;
        border-radius: 20px !important;
        padding: 40px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #1fb89a !important;
        background: rgba(31, 184, 154, 0.03) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(18, 20, 31, 0.8) !important;
        border: 1px solid #1e2135 !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
    }
    .streamlit-expanderContent {
        background: rgba(18, 20, 31, 0.5) !important;
        border: 1px solid #1e2135 !important;
        border-top: none !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0b0c14; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(#1fb89a, #e8a020); 
        border-radius: 10px; 
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1fb89a, #e8a020) !important;
        height: 8px !important;
        border-radius: 10px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(18, 20, 31, 0.8) !important;
        border-radius: 14px !important;
        padding: 6px !important;
        gap: 12px !important;
        border: 1px solid #1e2135 !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #7a7f9a !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1fb89a !important;
        background: rgba(31, 184, 154, 0.1) !important;
    }

    /* Sidebar nav items styling */
    .stPageLink > div {
        padding: 6px 12px !important;
        border-radius: 10px !important;
    }
    .stPageLink:hover > div {
        background: rgba(31, 184, 154, 0.1) !important;
    }

    /* Shimmer effect for loading */
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    .shimmer-card {
        background: linear-gradient(90deg, #12141f 25%, #1e2135 50%, #12141f 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        height: 120px;
        border-radius: 16px;
        margin-bottom: 20px;
    }
    
    /* Animations */
    .fade-in {
        animation: fadeIn 0.8s ease-out forwards;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

def mastery_color(score: float) -> str:
    if score >= 0.7: return "#1fb89a"
    elif score >= 0.4: return "#e8a020"
    else: return "#c4401a"

def mastery_label(score: float) -> str:
    if score >= 0.7: return "Mastered"
    elif score >= 0.4: return "Learning"
    else: return "Under Review"

def status_badge(status: str) -> str:
    status = status.lower()
    colors = {
        "done":       ("#1a3a30", "#1fb89a"),
        "pending":    ("#3a2a1a", "#e8a020"),
        "processing": ("#1a2a3a", "#3b82f6"),
        "error":      ("#3a1a1a", "#c4401a"),
    }
    bg, fg = colors.get(status, ("#1e2135", "#7a7f9a"))
    return (f'<span style="background:{bg};color:{fg};border:1px solid {fg};'
            f'padding:3px 14px;border-radius:100px;font-size:11px;'
            f'font-family:JetBrains Mono,monospace;font-weight:700;">{status.upper()}</span>')

def format_date(dt_str: str) -> str:
    if not dt_str: return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y · %H:%M")
    except Exception:
        return dt_str

def page_header(icon: str, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div style="margin-bottom:48px;padding-bottom:32px;border-bottom:1px solid rgba(30, 33, 53, 0.6)" class="fade-in">
      <div style="display:flex;align-items:center;gap:20px">
        <div style="font-size:48px;background:rgba(30,33,53,0.5);width:80px;height:80px;display:flex;align-items:center;justify-content:center;border-radius:20px;border:1px solid rgba(31,184,154,0.2)">{icon}</div>
        <div>
          <h1 style="margin:0;font-size:48px;font-family:Syne,sans-serif;font-weight:800;color:#e8e9f0;letter-spacing:-2px">
            {title}
          </h1>
          {f'<p style="margin:8px 0 0;color:#7a7f9a;font-size:18px;font-family:Lora,serif;font-style:italic">{subtitle}</p>' if subtitle else ''}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def concept_chip(name: str, score: float) -> str:
    color = mastery_color(score)
    return (f'<span style="background:{color}11;color:{color};'
            f'border:1px solid {color}44;padding:6px 16px;'
            f'border-radius:100px;font-size:13px;margin:5px;display:inline-block;'
            f'font-family:JetBrains Mono,monospace;font-weight:600;">{name}</span>')

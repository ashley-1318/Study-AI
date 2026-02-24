"""StudyAI — Streamlit authentication helpers."""
import time
import requests
import streamlit as st

AUTH_BASE            = "http://localhost:8000"
TOKEN_LIFETIME_HOURS = 23


# ─── Session Management ──────────────────────────────────────────────────────

def _save_session(access_token: str, refresh_token: str, user_dict: dict):
    st.session_state["access_token"]  = access_token
    st.session_state["refresh_token"] = refresh_token
    st.session_state["user"]          = user_dict
    st.session_state["auth_time"]     = time.time()


def _clear_session():
    for key in ("access_token", "refresh_token", "user", "auth_time"):
        st.session_state.pop(key, None)


def _token_needs_refresh() -> bool:
    if "auth_time" not in st.session_state:
        return False
    return (time.time() - st.session_state["auth_time"]) > (TOKEN_LIFETIME_HOURS * 3600)


def _try_refresh() -> bool:
    refresh_token = st.session_state.get("refresh_token")
    if not refresh_token:
        return False
    try:
        resp = requests.post(
            f"{AUTH_BASE}/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            _save_session(
                data["access_token"],
                data["refresh_token"],
                data.get("user", st.session_state.get("user", {})),
            )
            return True
    except Exception:
        pass
    _clear_session()
    return False


def _handle_oauth_redirect():
    """Read tokens from Google OAuth 2.0 redirect URL parameters."""
    params = st.query_params
    if "access_token" in params:
        user = {
            "name":       params.get("user_name", "User"),
            "email":      params.get("user_email", ""),
            "avatar_url": params.get("avatar_url", ""),
        }
        _save_session(
            params["access_token"],
            params.get("refresh_token", ""),
            user,
        )
        # Clear tokens from URL
        st.query_params.clear()
        st.rerun()


def get_auth_headers() -> dict:
    token = st.session_state.get("access_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


# ─── Auth Guard ───────────────────────────────────────────────────────────────

def require_auth() -> dict:
    """
    Enforce authentication. Shows login page and stops execution if not authed.
    Returns the user dict if authenticated.
    """
    _handle_oauth_redirect()

    if _token_needs_refresh():
        _try_refresh()

    if "user" not in st.session_state or not st.session_state.get("access_token"):
        show_login_page()
        st.stop()

    return st.session_state["user"]


# ─── Login Page ───────────────────────────────────────────────────────────────

def show_login_page():
    """Full-page premium login UI for StudyAI."""
    st.set_page_config(page_title="StudyAI — Login", page_icon="📚", layout="wide")
    _inject_login_css()

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style='display:flex;align-items:center;gap:16px;margin-bottom:8px'>
                <div style='font-size:64px;'>📚</div>
                <h1 style='margin:0;font-size:64px;font-weight:900;
                    background:linear-gradient(135deg,#1fb89a,#e8a020);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    font-family:Syne,sans-serif;letter-spacing:-3px;'>
                    StudyAI
                </h1>
            </div>
            <p style='color:#7a7f9a;font-size:22px;margin-bottom:48px;font-style:italic;'>
                Your adaptive AI study companion
            </p>
        """, unsafe_allow_html=True)

        features = [
            ("🎯", "Adaptive Quizzes",    "Generated from your personal weak spots using multi-agent AI"),
            ("🧠", "Smart Summaries",      "Hierarchical knowledge maps from any PDF, DOCX, or text file"),
            ("📅", "Revision Planning",    "SM-2 spaced repetition schedules for maximum retention"),
        ]
        for icon, title, desc in features:
            st.markdown(f"""
                <div style='display:flex;align-items:flex-start;gap:20px;margin-bottom:28px;
                    padding:20px;background:rgba(18,20,31,0.7);border-radius:16px;
                    border:1px solid #1e2135;'>
                    <span style='font-size:32px;min-width:48px'>{icon}</span>
                    <div>
                        <b style='color:#1fb89a;font-family:Syne,sans-serif;font-size:18px'>{title}</b><br/>
                        <span style='color:#7a7f9a;font-size:14px'>{desc}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("""
            <p style='color:#3a3f5a;font-size:13px;margin-top:40px;text-align:center'>
                Powered by Groq · LangGraph · FAISS · sentence-transformers
            </p>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("<div style='height:15vh'></div>", unsafe_allow_html=True)
        
        # Open card div
        st.markdown("""
            <div style='background:rgba(18,20,31,0.9);border:1px solid #1e2135;
                border-radius:24px;padding:40px;max-width:440px;margin:auto;
                box-shadow:0 20px 60px rgba(0,0,0,0.5);margin-bottom:-10px'>
                <h2 style='margin-top:0;font-family:Syne,sans-serif;color:#e8e9f0;
                    font-size:32px;letter-spacing:-1px'>Welcome back 👋</h2>
                <p style='color:#7a7f9a;margin-bottom:32px'>
                    Sign in to continue your learning journey
                </p>
                <hr style='border:0;border-top:1px solid #1e2135;margin-bottom:28px'>
        """, unsafe_allow_html=True)

        # Button logic (Streamlit widgets)
        # Try to get the Google OAuth URL from backend
        auth_url = None
        backend_ok = False
        try:
            resp = requests.get(f"{AUTH_BASE}/auth/login", timeout=5)
            if resp.status_code == 200:
                auth_url = resp.json().get("auth_url", "")
                backend_ok = bool(auth_url)
        except Exception:
            pass

        if backend_ok and auth_url:
            st.link_button(
                "🔐 Continue with Google",
                url=auth_url,
                use_container_width=True,
            )
            st.markdown("""
                <p style='color:#3a3f5a;font-size:12px;text-align:center;margin-top:12px'>
                    You will be redirected to Google to sign in securely.
                </p>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Backend offline — running in Demo Mode")
            if st.button("🎭 Enter Demo Mode", key="demo_btn", use_container_width=True):
                _save_session(
                    "demo_token",
                    "demo_refresh",
                    {
                        "name":       "Alex Learner",
                        "email":      "test@studyai.dev",
                        "avatar_url": "https://i.pravatar.cc/150?u=studyai",
                    },
                )
                st.rerun()
        
        # Close card div
        st.markdown("</div>", unsafe_allow_html=True)


def _inject_login_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800;900&family=Lora:ital@0;1&display=swap');
    #MainMenu, footer, header { visibility:hidden }
    .stApp { background:#0b0c14 }
    section[data-testid="stSidebar"] { display:none }
    /* Regular buttons */
    .stButton > button {
        background: linear-gradient(135deg,#1fb89a,#15a085) !important;
        color:#0b0c14 !important; font-weight:800 !important;
        border:none !important; border-radius:12px !important;
        font-size:16px !important; padding:14px !important;
        font-family:Syne,sans-serif !important;
        box-shadow:0 4px 20px rgba(31,184,154,0.4) !important;
        transition:all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform:translateY(-2px) !important;
        box-shadow:0 8px 30px rgba(31,184,154,0.5) !important;
    }
    /* st.link_button styling — matches google sign-in look */
    .stLinkButton > a {
        background: linear-gradient(135deg,#1fb89a,#15a085) !important;
        color:#0b0c14 !important; font-weight:800 !important;
        border:none !important; border-radius:12px !important;
        font-size:16px !important; padding:14px 20px !important;
        font-family:Syne,sans-serif !important;
        box-shadow:0 4px 20px rgba(31,184,154,0.4) !important;
        transition:all 0.3s ease !important;
        text-decoration:none !important;
        display:block !important; text-align:center !important;
        width:100% !important;
    }
    .stLinkButton > a:hover {
        transform:translateY(-2px) !important;
        box-shadow:0 8px 30px rgba(31,184,154,0.5) !important;
        color:#0b0c14 !important;
    }
    p, div, span, h1, h2, h3, label { font-family:Lora,serif !important; }
    </style>
    """, unsafe_allow_html=True)


# ─── Sidebar User Panel ───────────────────────────────────────────────────────

def show_user_sidebar():
    """Render avatar, name, email and logout in the sidebar."""
    user = st.session_state.get("user")
    if not user:
        return

    st.sidebar.markdown("<hr style='border-top:1px solid #1e2135;margin:20px 0'>", unsafe_allow_html=True)

    avatar = user.get("avatar_url", "")
    name   = user.get("name", "User")
    email  = user.get("email", "")

    cols = st.sidebar.columns([1, 3])
    with cols[0]:
        if avatar:
            st.image(avatar, width=40)
        else:
            st.markdown(f"""
                <div style='width:40px;height:40px;border-radius:50%;
                    background:linear-gradient(135deg,#1fb89a,#e8a020);
                    display:flex;align-items:center;justify-content:center;
                    font-weight:bold;color:#0b0c14;font-size:16px'>
                    {name[0].upper()}
                </div>""", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<b style='color:#e8e9f0;font-size:14px'>{name}</b>", unsafe_allow_html=True)
        st.markdown(f"<small style='color:#7a7f9a'>{email}</small>", unsafe_allow_html=True)

    if st.sidebar.button("🚪 Sign out", key="logout_btn", use_container_width=True):
        logout()


def logout():
    try:
        requests.post(f"{AUTH_BASE}/auth/logout", headers=get_auth_headers(), timeout=5)
    except Exception:
        pass
    _clear_session()
    st.rerun()

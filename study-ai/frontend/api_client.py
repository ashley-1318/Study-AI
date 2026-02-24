"""StudyAI — API client for Streamlit → FastAPI calls."""
import streamlit as st
import requests

BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = "http://localhost:8000"
WS_BASE  = "ws://localhost:8000/ws"


def _headers() -> dict:
    token = st.session_state.get("access_token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _clear_session():
    for key in ("access_token", "refresh_token", "user", "auth_time"):
        st.session_state.pop(key, None)


def api_get(endpoint: str, params: dict = None) -> dict | None:
    url = f"{BASE_URL}{endpoint}"
    try:
        resp = requests.get(url, headers=_headers(), params=params, timeout=30)
        if resp.status_code == 401:
            _clear_session()
            st.rerun()
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return None  # handled by caller (Demo Mode or error display)
    except requests.exceptions.Timeout:
        return None  # caller will retry on next poll cycle
    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            detail = resp.json().get("detail", "")
        except Exception:
            pass
        st.error(f"API error {resp.status_code}: {detail or str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def api_post(endpoint: str, json: dict = None, files: dict = None, data: dict = None) -> dict | None:
    url = f"{BASE_URL}{endpoint}"
    headers = _headers()
    if files:
        # Let requests set multipart Content-Type with boundary
        pass
    else:
        headers["Content-Type"] = "application/json"
    try:
        resp = requests.post(url, headers=headers, json=json, files=files, data=data, timeout=30)
        if resp.status_code == 401:
            _clear_session()
            st.rerun()
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("🔌 Backend offline — start the StudyAI server on port 8000")
        return None
    except requests.exceptions.HTTPError as e:
        detail = ""
        try:
            detail = resp.json().get("detail", "")
        except Exception:
            pass
        st.error(f"API error {resp.status_code}: {detail or str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def api_delete(endpoint: str) -> dict | None:
    url = f"{BASE_URL}{endpoint}"
    try:
        resp = requests.delete(url, headers=_headers(), timeout=15)
        if resp.status_code == 401:
            _clear_session()
            st.rerun()
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("🔌 Backend offline")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def ws_url(path: str) -> str:
    """Build authenticated WebSocket URL."""
    token = st.session_state.get("access_token", "")
    return f"{WS_BASE}/{path}?token={token}"

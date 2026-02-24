"""StudyAI — Auth routes: login, OAuth callback, refresh, me, logout."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import (
    create_access_token, create_refresh_token,
    decode_token, exchange_code, fetch_google_profile,
    generate_state, get_current_user, get_google_auth_url,
    get_or_create_user, verify_state,
)
from database import get_db

router = APIRouter(tags=["auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.get("/auth/login")
async def login():
    """Redirect the frontend to Google's OAuth consent page."""
    state = generate_state()
    auth_url = get_google_auth_url(state)
    return {"auth_url": auth_url}


@router.get("/auth/callback")
async def oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    """
    Google redirects here with an auth code.
    We exchange for tokens, upsert the user, issue JWTs,
    then redirect to the Streamlit frontend.
    """
    if not verify_state(state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state — possible CSRF")

    token_data = await exchange_code(code)
    profile    = await fetch_google_profile(token_data["access_token"])
    user       = get_or_create_user(db, profile)

    access_token  = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id)

    redirect_url = (
        f"http://localhost:8501"
        f"?access_token={access_token}"
        f"&refresh_token={refresh_token}"
        f"&user_name={user.name}"
        f"&user_email={user.email}"
        f"&avatar_url={user.avatar_url or ''}"
    )
    return RedirectResponse(url=redirect_url)


@router.post("/auth/refresh")
async def refresh_tokens(body: RefreshRequest, db: Session = Depends(get_db)):
    """Validate a refresh token and issue a new access + refresh token pair."""
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user_id = payload["sub"]
    from database import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access  = create_access_token(user.id, user.email)
    new_refresh = create_refresh_token(user.id)

    return {
        "success": True,
        "data": {
            "access_token":  new_access,
            "refresh_token": new_refresh,
            "user": {
                "id":         user.id,
                "email":      user.email,
                "name":       user.name,
                "avatar_url": user.avatar_url,
            },
        },
        "error": None,
    }


@router.get("/auth/me")
async def get_me(current_user=Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return {
        "success": True,
        "data": {
            "id":         current_user.id,
            "email":      current_user.email,
            "name":       current_user.name,
            "avatar_url": current_user.avatar_url,
        },
        "error": None,
    }


@router.post("/auth/logout")
async def logout():
    """Client should discard tokens; JWT is stateless so no server action needed."""
    return {"success": True, "data": {"message": "Logged out of StudyAI"}, "error": None}

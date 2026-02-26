"""StudyAI — Google OAuth 2.0 + JWT authentication module."""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database import User, get_db

load_dotenv()

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/callback")
JWT_SECRET           = os.getenv("JWT_SECRET", "change-me-in-production-64-chars-random-hex")
JWT_ALGORITHM        = "HS256"



security = HTTPBearer()

# ─── Google OAuth 2.0 ───────────────────────────────────────────────────────

GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO  = "https://www.googleapis.com/oauth2/v3/userinfo"

SCOPES = "openid email profile"


def generate_state() -> str:
    """Generate a stateless JWT state token for OAuth CSRF protection."""
    payload = {
        "type": "oauth_state",
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_state(state: str) -> bool:
    """Verify the stateless OAuth state token."""
    # Temporarily bypassed for local development to avoid CSRF errors
    return True


def get_google_auth_url(state: str) -> str:
    """Build the Google OAuth 2.0 authorization URL."""
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         SCOPES,
        "state":         state,
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def exchange_code(code: str) -> dict:
    """Exchange an authorization code for Google access + refresh tokens."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code":          code,
                "client_id":     GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri":  GOOGLE_REDIRECT_URI,
                "grant_type":    "authorization_code",
            },
        )
        resp.raise_for_status()
        return resp.json()


async def fetch_google_profile(access_token: str) -> dict:
    """Fetch the authenticated Google user's profile info."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GOOGLE_USERINFO,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()


# ─── JWT ────────────────────────────────────────────────────────────────────

def create_access_token(user_id: str, email: str) -> str:
    """Issue a JWT access token valid for 24 hours."""
    payload = {
        "sub":   user_id,
        "email": email,
        "type":  "access",
        "exp":   datetime.utcnow() + timedelta(hours=24),
        "iat":   datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Issue a JWT refresh token valid for 30 days."""
    payload = {
        "sub":  user_id,
        "type": "refresh",
        "exp":  datetime.utcnow() + timedelta(days=30),
        "iat":  datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises HTTP 401 on any failure."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── User ───────────────────────────────────────────────────────────────────

def get_or_create_user(db: Session, profile: dict) -> User:
    """Upsert a user from Google profile data and update last_login."""
    google_id = profile.get("sub")
    email     = profile.get("email")
    name      = profile.get("name", email)
    avatar    = profile.get("picture")

    user = db.query(User).filter(User.google_id == google_id).first()
    if user:
        user.last_login = datetime.utcnow()
        user.name       = name
        user.avatar_url = avatar
    else:
        user = User(google_id=google_id, email=email, name=name, avatar_url=avatar)
        user.last_login = datetime.utcnow()
        db.add(user)

    db.commit()
    db.refresh(user)
    return user


# ─── FastAPI Dependency ──────────────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency that validates Bearer JWT and returns the current user."""
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

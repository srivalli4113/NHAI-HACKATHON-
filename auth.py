from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.contracts import LoginRequest, TokenResponse
from app.security.auth import bearer, create_session, destroy_session, get_current_user, verify_admin_credentials

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if not verify_admin_credentials(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return TokenResponse(access_token=create_session(db, payload.username))


@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> dict:
    if credentials:
        destroy_session(db, credentials.credentials)
    return {"ok": True}


@router.get("/me")
def me(user: str = Depends(get_current_user)) -> dict:
    return {"username": user}


from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.contracts import AccountProfile, LoginRequest, SignupRequest, TokenResponse
from app.security.auth import (
    AuthIdentity,
    authenticate_user,
    bearer,
    create_session,
    create_user_account,
    destroy_session,
    get_current_identity,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    identity = authenticate_user(db, payload.username, payload.password)
    if not identity:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return TokenResponse(
        access_token=create_session(db, identity.username),
        role=identity.role,
        display_name=identity.display_name,
    )


@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    identity = create_user_account(
        db,
        display_name=payload.display_name,
        username=payload.username,
        password=payload.password,
        role=payload.role,
    )
    return TokenResponse(
        access_token=create_session(db, identity.username),
        role=identity.role,
        display_name=identity.display_name,
    )


@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> dict:
    if credentials:
        destroy_session(db, credentials.credentials)
    return {"ok": True}


@router.get("/me")
def me(identity: AuthIdentity = Depends(get_current_identity)) -> AccountProfile:
    return AccountProfile(
        username=identity.username,
        display_name=identity.display_name,
        role=identity.role,
    )

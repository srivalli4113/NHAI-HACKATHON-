import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.entities import AdminSession, UserAccount

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthIdentity:
    username: str
    display_name: str
    role: str


def canonical_role(role: str) -> str:
    """Keep accounts created during earlier demo builds usable after the role rename."""
    return {"employer": "operator", "field_staff": "employee"}.get(role, role)


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 150_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, digest = stored.split("$", 1)
    candidate = hash_password(password, salt).split("$", 1)[1]
    return hmac.compare_digest(candidate, digest)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(db: Session, username: str) -> str:
    settings = get_settings()
    token = secrets.token_urlsafe(36)
    db.add(
        AdminSession(
            token_hash=token_hash(token),
            username=username,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.session_minutes),
        )
    )
    db.commit()
    return token


def destroy_session(db: Session, token: str) -> None:
    session = db.get(AdminSession, token_hash(token))
    if session:
        db.delete(session)
        db.commit()


def _active_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> AdminSession:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    session = db.get(AdminSession, token_hash(credentials.credentials))
    now = datetime.now(timezone.utc)
    expires_at = session.expires_at if session else None
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if not session or not expires_at or expires_at < now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    return session


def identity_for_username(db: Session, username: str) -> AuthIdentity:
    settings = get_settings()
    if hmac.compare_digest(username.casefold(), settings.admin_username.casefold()):
        return AuthIdentity(username=settings.admin_username, display_name="System Administrator", role="admin")

    account = db.scalar(
        select(UserAccount).where(UserAccount.username == username.casefold(), UserAccount.is_active.is_(True))
    )
    if not account:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is unavailable")
    return AuthIdentity(
        username=account.username,
        display_name=account.display_name,
        role=canonical_role(account.role),
    )


def get_current_identity(
    session: AdminSession = Depends(_active_session),
    db: Session = Depends(get_db),
) -> AuthIdentity:
    return identity_for_username(db, session.username)


def get_current_user(identity: AuthIdentity = Depends(get_current_identity)) -> str:
    return identity.username


def require_operator(identity: AuthIdentity = Depends(get_current_identity)) -> AuthIdentity:
    if identity.role not in {"admin", "operator"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operator access is required")
    return identity


def require_admin(identity: AuthIdentity = Depends(get_current_identity)) -> AuthIdentity:
    if identity.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access is required")
    return identity


def verify_admin_credentials(username: str, password: str) -> bool:
    settings = get_settings()
    if not settings.admin_password:
        return False
    stored = hash_password(settings.admin_password, "offline-admin-salt")
    return hmac.compare_digest(username.casefold(), settings.admin_username.casefold()) and verify_password(password, stored)


def authenticate_user(db: Session, username: str, password: str) -> AuthIdentity | None:
    normalized_username = username.strip().casefold()
    if verify_admin_credentials(normalized_username, password):
        return identity_for_username(db, get_settings().admin_username)

    account = db.scalar(
        select(UserAccount).where(UserAccount.username == normalized_username, UserAccount.is_active.is_(True))
    )
    if not account or not verify_password(password, account.password_hash):
        return None
    return AuthIdentity(
        username=account.username,
        display_name=account.display_name,
        role=canonical_role(account.role),
    )


def create_user_account(
    db: Session,
    *,
    display_name: str,
    username: str,
    password: str,
    role: str,
) -> AuthIdentity:
    normalized_username = username.strip().casefold()
    normalized_display_name = " ".join(display_name.split())
    if normalized_username == get_settings().admin_username.casefold():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="That username is reserved")
    if db.scalar(select(UserAccount).where(UserAccount.username == normalized_username)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    account = UserAccount(
        username=normalized_username,
        display_name=normalized_display_name,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(account)
    db.commit()
    return AuthIdentity(
        username=account.username,
        display_name=account.display_name,
        role=canonical_role(account.role),
    )

"""FastAPI dependency injection: auth (JWT + API key), rate limiting, DB session."""
from __future__ import annotations

import hashlib
import uuid as _uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from apps.drug_ref.db.models import ApiKey, Subscription, User
from apps.drug_ref.db.session import SessionLocal
from apps.drug_ref.rate_limiter.redis_limiter import get_rate_limiter
from apps.drug_ref.utils.config import settings

try:
    from jose import JWTError, jwt
except Exception:  # pragma: no cover
    jwt = None
    JWTError = Exception

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Probe — some passlib/bcrypt combos error on certain inputs
    pwd_context.hash("probe123")
except Exception:  # pragma: no cover
    pwd_context = None


JWT_ALGORITHM = "HS256"
bearer_scheme = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------- #
# DB session
# ---------------------------------------------------------------------- #
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------- #
# Password hashing
# ---------------------------------------------------------------------- #
def hash_password(password: str) -> str:
    if pwd_context is not None:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    return "sha256$" + hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("sha256$"):
        return password_hash == "sha256$" + hashlib.sha256(password.encode()).hexdigest()
    if pwd_context is not None:
        try:
            return pwd_context.verify(password, password_hash)
        except Exception:
            return False
    return False


# ---------------------------------------------------------------------- #
# JWT
# ---------------------------------------------------------------------- #
def create_access_token(user_id: str, email: str, role: str, organization_id: Optional[str] = None) -> str:
    expires = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "org": organization_id,
        "exp": expires,
    }
    if jwt is None:
        # Insecure fallback (dev only)
        import base64
        import json
        return base64.urlsafe_b64encode(json.dumps(payload, default=str).encode()).decode()
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    if jwt is None:
        try:
            import base64
            import json
            return json.loads(base64.urlsafe_b64decode(token.encode()).decode())
        except Exception:
            return None
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None


# ---------------------------------------------------------------------- #
# API Key Hashing (deterministic — to allow lookups)
# ---------------------------------------------------------------------- #
def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------- #
# Auth resolution
# ---------------------------------------------------------------------- #
def _user_from_bearer(token: str, db: Session) -> Optional[User]:
    payload = decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    try:
        user_uuid = _uuid.UUID(str(user_id))
    except (ValueError, TypeError):
        return None
    return db.query(User).filter(User.id == user_uuid).first()


def _user_from_api_key(api_key: str, db: Session) -> Tuple[Optional[User], Optional[ApiKey]]:
    if not api_key or len(api_key) < 8:
        return None, None
    prefix = api_key[:8]
    key_hash = hash_api_key(api_key)
    record = (
        db.query(ApiKey)
        .filter(ApiKey.key_prefix == prefix, ApiKey.key_hash == key_hash, ApiKey.is_active == True)
        .first()
    )
    if not record:
        return None, None
    user = db.query(User).filter(User.id == record.created_by_user_id).first()
    return user, record


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> User:
    # Try API key first (for B2B usage)
    if x_api_key:
        user, api_key_record = _user_from_api_key(x_api_key, db)
        if user:
            # Stash on request state
            request.state.api_key_id = str(api_key_record.id) if api_key_record else None
            request.state.auth_method = "api_key"
            return user

    # Then bearer token
    if credentials and credentials.credentials:
        user = _user_from_bearer(credentials.credentials, db)
        if user:
            request.state.api_key_id = None
            request.state.auth_method = "jwt"
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_active_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Subscription:
    sub = (
        db.query(Subscription)
        .filter(
            (Subscription.user_id == user.id)
            | (Subscription.organization_id == user.organization_id)
        )
        .filter(Subscription.status.in_(["active", "trialing"]))
        .order_by(Subscription.created_at.desc())
        .first()
    )
    if not sub:
        # Auto-create trial
        sub = Subscription(
            user_id=user.id,
            organization_id=user.organization_id,
            plan="trial",
            status="active",
            queries_used_this_month=0,
            queries_limit_per_month=10,
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)
    return sub


def enforce_quota_and_rate_limit(
    request: Request,
    user: User = Depends(get_current_user),
    sub: Subscription = Depends(get_active_subscription),
):
    # 1. Monthly quota
    if sub.queries_used_this_month >= sub.queries_limit_per_month:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "monthly_quota_exceeded",
                "plan": sub.plan,
                "queries_limit": sub.queries_limit_per_month,
                "queries_used": sub.queries_used_this_month,
                "upgrade_url": f"{settings.frontend_url}/pricing",
            },
        )

    # 2. Rate limit
    identity = str(user.id)
    allowed, info = get_rate_limiter().check(identity, sub.plan)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "retry_after_seconds": info["retry_after"],
                "limit": info["limit"],
            },
            headers={"Retry-After": str(info["retry_after"])},
        )

    # Attach for response headers
    request.state.rate_limit_info = info
    return {"user": user, "subscription": sub, "rate_limit": info}

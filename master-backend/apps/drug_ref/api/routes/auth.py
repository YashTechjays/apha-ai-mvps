"""Auth endpoints: signup, login, API key management."""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.drug_ref.api.deps import (
    create_access_token,
    get_current_user,
    get_db,
    hash_api_key,
    hash_password,
    verify_password,
)
from apps.drug_ref.api.schemas.auth import (
    ApiKeyCreateRequest,
    ApiKeyResponse,
    LoginRequest,
    SignupRequest,
    TokenResponse,
)
from apps.drug_ref.db.models import ApiKey, Organization, Subscription, User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Create organization if name provided, else single-user account
    org = None
    if req.organization_name:
        org = Organization(
            name=req.organization_name,
            org_type="independent",
            max_seats=1,
        )
        db.add(org)
        db.flush()

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        role="admin" if org else "individual",
        organization_id=org.id if org else None,
        full_name=req.full_name,
    )
    db.add(user)
    db.flush()

    # Default trial subscription
    sub = Subscription(
        user_id=user.id,
        organization_id=org.id if org else None,
        plan="trial",
        status="active",
        queries_limit_per_month=10,
    )
    db.add(sub)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        organization_id=str(user.organization_id) if user.organization_id else None,
    )
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        organization_id=str(user.organization_id) if user.organization_id else None,
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated.")
    token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        organization_id=str(user.organization_id) if user.organization_id else None,
    )
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        organization_id=str(user.organization_id) if user.organization_id else None,
    )


@router.post("/api-keys", response_model=ApiKeyResponse)
def create_api_key(
    req: ApiKeyCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    raw, prefix = ApiKey.generate_key()
    record = ApiKey(
        organization_id=user.organization_id,
        created_by_user_id=user.id,
        key_prefix=prefix,
        key_hash=hash_api_key(raw),
        label=req.label,
        is_active=True,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return ApiKeyResponse(
        id=str(record.id),
        label=record.label,
        key_prefix=record.key_prefix,
        raw_key=raw,
        is_active=record.is_active,
        created_at=(record.created_at or datetime.utcnow()).isoformat(),
    )


@router.get("/api-keys", response_model=list[ApiKeyResponse])
def list_api_keys(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = (
        db.query(ApiKey)
        .filter(ApiKey.created_by_user_id == user.id)
        .order_by(ApiKey.created_at.desc())
        .all()
    )
    return [
        ApiKeyResponse(
            id=str(r.id),
            label=r.label,
            key_prefix=r.key_prefix,
            raw_key=None,
            is_active=r.is_active,
            created_at=(r.created_at or datetime.utcnow()).isoformat(),
        )
        for r in records
    ]


@router.delete("/api-keys/{api_key_id}")
def revoke_api_key(
    api_key_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        key_uuid = uuid.UUID(str(api_key_id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid API key id.")
    rec = (
        db.query(ApiKey)
        .filter(ApiKey.id == key_uuid, ApiKey.created_by_user_id == user.id)
        .first()
    )
    if not rec:
        raise HTTPException(status_code=404, detail="API key not found.")
    rec.is_active = False
    db.commit()
    return {"revoked": True, "id": api_key_id}


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "organization_id": str(user.organization_id) if user.organization_id else None,
        "full_name": user.full_name,
        "is_active": user.is_active,
    }

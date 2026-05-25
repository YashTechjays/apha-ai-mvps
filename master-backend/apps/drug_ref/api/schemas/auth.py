"""Pydantic schemas for auth endpoints."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    organization_name: Optional[str] = None
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24h
    user_id: str
    email: str
    role: str
    organization_id: Optional[str] = None


class ApiKeyCreateRequest(BaseModel):
    label: Optional[str] = None


class ApiKeyResponse(BaseModel):
    id: str
    label: Optional[str]
    key_prefix: str
    raw_key: Optional[str] = None  # Only present on creation
    is_active: bool
    created_at: str

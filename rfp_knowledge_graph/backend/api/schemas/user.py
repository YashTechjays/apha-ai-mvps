from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username may only contain letters, numbers, and underscores")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    years_experience: Optional[int] = None
    location_state: Optional[str] = None
    location_city: Optional[str] = None
    specialties: list[str] = []
    certifications: list[str] = []
    org_types_preferred: list[str] = []
    notify_on_match: bool = True
    notify_threshold: int = 70


class ProfileResponse(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    years_experience: Optional[int] = None
    location_state: Optional[str] = None
    location_city: Optional[str] = None
    specialties: list[str] = []
    certifications: list[str] = []
    org_types_preferred: list[str] = []
    notify_on_match: bool = True
    notify_threshold: int = 70


class UserMeResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    profile: Optional[ProfileResponse] = None

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta
from apps.crosssell.utils.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

DEMO_USERS = {"admin": "apha2026", "analyst": "analyst123"}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if DEMO_USERS.get(form_data.username) != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    token = jwt.encode(
        {"sub": form_data.username, "exp": expire},
        settings.secret_key, algorithm=settings.jwt_algorithm,
    )
    return {"access_token": token, "token_type": "bearer"}

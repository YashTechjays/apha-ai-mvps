from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta
import bcrypt
from sqlalchemy.orm import Session
from backend.utils.config import get_settings
from backend.db.session import get_db
from backend.api.schemas.user import RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

DEMO_USERS = {"admin": "apha2026", "analyst": "analyst123"}


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _make_token(sub: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": sub, "exp": expire},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Check demo users first (unchanged behaviour)
    if DEMO_USERS.get(form_data.username) == form_data.password:
        return {"access_token": _make_token(form_data.username), "token_type": "bearer", "role": "admin"}

    # 2. Fall through to DB users
    from backend.db.models.user import User
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    if not user or not _verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is disabled")

    return {"access_token": _make_token(str(user.id)), "token_type": "bearer", "role": user.role.value}


@router.post("/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    from backend.db.models.user import User
    from backend.db.models.pharmacist_profile import PharmacistProfile

    # Check uniqueness
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=body.username,
        email=body.email,
        password_hash=_hash_password(body.password),
    )
    db.add(user)
    db.flush()  # get user.id before committing

    profile = PharmacistProfile(user_id=user.id)
    db.add(profile)
    db.commit()

    return {"access_token": _make_token(str(user.id)), "token_type": "bearer", "role": "pharmacist"}

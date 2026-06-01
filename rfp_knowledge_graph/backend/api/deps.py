from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from backend.utils.config import get_settings
from backend.db.session import get_db

security = HTTPBearer()
settings = get_settings()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_pharmacist(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Resolves a DB-registered pharmacist from the JWT. Does not accept demo users."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    from backend.db.models.user import User
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

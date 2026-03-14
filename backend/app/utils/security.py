from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.services.settings_service import app_settings

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire_minutes = app_settings.get_int("jwt_expire_minutes", 1440)
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=expire_minutes))
    to_encode.update({"exp": expire})
    jwt_secret = app_settings.get("jwt_secret")
    return jwt.encode(to_encode, jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        jwt_secret = app_settings.get("jwt_secret")
        payload = jwt.decode(token, jwt_secret, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

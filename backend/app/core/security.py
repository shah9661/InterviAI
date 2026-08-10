import logging
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError

from backend.app.core.logging import get_logger
from backend.app.core.config import settings

logger = get_logger("security", log_file="logs/security.log", level=logging.INFO)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    try:
        password_bytes = password.encode("utf-8")[:72]
        return pwd_context.hash(password_bytes)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        plain_password_bytes = plain_password.encode("utf-8")[:72]
        return pwd_context.verify(plain_password_bytes, hashed_password)
    except Exception as e:
        logger.warning(f"Password verification failed: {e}")
        return False


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.now() + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Access token created for sub={data.get('sub')}")
        return token
    except Exception as e:
        logger.error(f"Token creation failed: {e}")
        raise


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token decode failed: {e}")
        return None
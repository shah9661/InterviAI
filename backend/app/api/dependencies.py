import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.candidate import Candidate
from app.core.security import decode_access_token
from app.core.logging import get_logger

logger = get_logger("auth_dependency", log_file="logs/auth.log", level=logging.INFO)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="candidates/login")


def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends  (get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Token decode failed — invalid or expired token")
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        logger.warning("Token payload missing 'sub' claim")
        raise credentials_exception

    try:
        user = db.query(Candidate).filter(Candidate.id == int(user_id)).first()
    except (ValueError, TypeError) as e:
        
        logger.error(f"Invalid user_id format in token: {user_id} — {e}")
        raise credentials_exception
    except Exception as e:
        # DB query level ka unexpected error (connection drop, etc.)
        logger.error(f"DB error while fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while authenticating"
        )

    if user is None:
        logger.warning(f"No user found for id: {user_id}")
        raise credentials_exception

    logger.debug(f"Authenticated user: {user_id}")
    return user
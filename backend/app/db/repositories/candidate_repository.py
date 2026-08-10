import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.db.models.candidate import Candidate
from app.core.logging import get_logger

logger = get_logger("candidate_repository", log_file="logs/candidate_repository.log", level=logging.INFO)


def get_candidate_by_email(db: Session, email: str):
    try:
        return db.query(Candidate).filter(Candidate.email == email).first()
    except SQLAlchemyError as e:
        logger.error(f"DB error while fetching candidate by email {email}: {e}")
        raise


def create_candidate(db: Session, name: str, email: str, hashed_password: str):
    try:
        candidate = Candidate(name=name, email=email, hashed_password=hashed_password)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        logger.info(f"Candidate created in DB: {email}")
        return candidate
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Integrity error creating candidate {email}: {e}")
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"DB error while creating candidate {email}: {e}")
        raise
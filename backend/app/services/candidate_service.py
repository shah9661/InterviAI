import logging
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from backend.app.db.models.candidate import Candidate
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.logging import get_logger
from backend.app.utils.extract import extract_pdf,extract_docx
from backend.app.ml.rag.context_builder import store_resume_vector

logger = get_logger("candidate_service", log_file="logs/candidate_service.log", level=logging.INFO)


async def extract_resume_text(resume: UploadFile) -> str:
    try:
        if not resume.filename:
            raise HTTPException(status_code=400,detail="Resume filename is missing")
        content = await resume.read()
        if not content:
            raise HTTPException(status_code=400,detail="Resume file is empty")
        filename = resume.filename.lower()
        if filename.endswith(".pdf"):
            resume_text = extract_pdf(content)
        elif filename.endswith(".docx"):
            resume_text = extract_docx(content)
        else:
            raise HTTPException(status_code=400,
                detail="Only PDF and DOCX files are supported")

        if not resume_text or not resume_text.strip():
            raise HTTPException(status_code=422,
                detail="Could not extract text from resume")
        return resume_text

    except HTTPException:
        raise

    except Exception:
        logger.exception(f"Resume text extraction failed filename={resume.filename}")
        raise HTTPException(
            status_code=422,
            detail="Could not process resume file")


async def register_candidate(
    db: Session,
    name: str,
    email: str,
    password: str,
    target_role: str,
    resume: UploadFile,
) -> Candidate:
    existing = db.query(Candidate).filter(Candidate.email == email).first()
    if existing:
        logger.warning(f"Registration attempt with existing email: {email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    resume_text = await extract_resume_text(resume)
    hashed = hash_password(password)

    try:
        candidate = Candidate(
            name=name,
            email=email,
            password_hash=hashed,
            target_role=target_role,
            resume_text=resume_text,
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    except Exception as e:
        db.rollback()
        logger.error(f"DB error while creating candidate {email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create candidate")

    logger.info(f"Candidate registered: {candidate.email}")
    return candidate

def embed_resume_task(candidate_id: int, resume_text: str,db:Session) -> None:
    try:
        store_resume_vector(db=db, candidate_id=candidate_id, resume_text=resume_text)
    finally:
        db.close()


def authenticate(db: Session, email: str, password: str) -> dict:
    user = db.query(Candidate).filter(Candidate.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logger.warning(f"Failed login attempt: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    logger.info(f"Login successful: {user.email}")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "candidate_id": user.id,
        "name": user.name,
    }


def get_candidate_by_email(db: Session, email: str) -> Candidate | None:
    return db.query(Candidate).filter(Candidate.email == email).first()


def update_password(db: Session, candidate: Candidate, new_password: str) -> Candidate:
    try:
        candidate.password_hash = hash_password(new_password)
        db.commit()
        db.refresh(candidate)
        logger.info(f"Password updated for candidate: {candidate.email}")
        return candidate
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update password for {candidate.email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset password")
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.candidate import Token, LoginRequest
from backend.app.services.candidate_service import authenticate


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    return authenticate(
        db=db,
        email=credentials.email,
        password=credentials.password,
    )

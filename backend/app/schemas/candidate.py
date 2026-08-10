from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class CandidateOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    candidate_id: int
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# class ForgotPasswordRequest(BaseModel):
#     email: EmailStr

# class ResetPasswordRequest(BaseModel):
#     email: EmailStr
#     otp_code: str
#     new_password: str

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ── 회원가입 ──────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


# ── 로그인 응답 ───────────────────────────────────────
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── JWT 토큰 ──────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
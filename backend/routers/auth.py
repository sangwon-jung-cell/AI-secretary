from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from backend.schemas.userschema import Token, UserCreate, UserResponse
from backend.models.users import User

router = APIRouter(prefix="/auth", tags=["인증"])

# OAuth2 토큰 스킴 (Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── 현재 로그인 유저 가져오기 (공통 의존성) ─────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = decode_access_token(token)
    if username is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 계정입니다.")
    return current_user


# ── 회원가입 ──────────────────────────────────────────
@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """새 유저를 등록합니다."""

    # 이메일 중복 확인
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")

    # 유저명 중복 확인
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="이미 사용 중인 유저명입니다.")

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── 로그인 (JWT 토큰 발급) ────────────────────────────
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """username + password로 로그인 후 JWT 토큰을 반환합니다."""

    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유저명 또는 비밀번호가 틀렸습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 계정입니다.")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ── 내 정보 조회 ──────────────────────────────────────
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """현재 로그인된 유저 정보를 반환합니다."""
    return current_user


# ── 로그아웃 (클라이언트 측에서 토큰 삭제) ───────────────
@router.post("/logout")
def logout():
    """
    JWT는 서버에 상태를 저장하지 않으므로,
    실제 로그아웃은 클라이언트에서 토큰을 삭제하면 됩니다.
    (블랙리스트 기능이 필요하면 Redis 등을 활용하세요)
    """
    return {"message": "로그아웃 되었습니다. 클라이언트에서 토큰을 삭제해주세요."}
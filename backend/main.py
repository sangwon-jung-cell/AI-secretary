from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import model

# 우리가 만든 부품들을 가져옵니다.
from .database import Base, engine, get_db
from .models import model  # models 폴더 안의 model.py
from .schemas import schema # schemas 폴더 안의 schema.py
from .crud import crud  # crud 폴더 안의 crud.py

# 1. 서버 시작 시 DB 테이블 생성
# 이 코드가 실행되면 PostgreSQL에 memos와 todos 테이블이 생깁니다.
model.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "AI 비서 백엔드 서버가 정상적으로 실행 중입니다!"}

@app.get("/db-test")
def test_db_connection(db: Session = Depends(get_db)):
    # DB 연결을 확인하기 위한 간단한 테스트
    try:
        # 간단한 쿼리 실행
        return {"status": "success", "message": "PostgreSQL DB 연결에 성공했습니다!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 연결 실패: {str(e)}")

# [POST] 메모 저장 API 창구
@app.post("/memos", response_model=schema.Memo)
def create_memo_endpoint(memo: schema.MemoCreate, db: Session = Depends(get_db)):
    """
    사용자가 메모 원문을 보내면 DB에 저장하는 창구입니다.
    """
    return crud.create_memo(db=db, memo_data=memo)
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import model

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
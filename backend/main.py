from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import model
from backend.ai_service import analyze_memo_with_ai

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
    db_memo = crud.create_memo(db=db, memo_data=memo)

    # 이제 내부적으로 Gemini가 작동합니다.
    ai_result = analyze_memo_with_ai(db_memo.content)
    
    todo_data = schema.TodoCreate(
        task=ai_result.get("task") or "할 일 알 수 없음",
        date=ai_result.get("date"),
        time=ai_result.get("time")
    )
    crud.create_todo(db=db, todo_data=todo_data, memo_id=db_memo.id)
    
    return db_memo

@app.delete("/todos/{todo_id}")
def delete_todo_endpoint(todo_id: int, db: Session = Depends(get_db)):
    success = crud.delete_todo(db, todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="삭제할 아이템을 찾을 수 없습니다.")
    return {"message": f"ID {todo_id} 삭제 완료"}

@app.delete("/memos/{memo_id}")
def delete_memo_endpoint(memo_id: int, db: Session = Depends(get_db)):
    success = crud.delete_memo(db, memo_id)
    if not success:
        raise HTTPException(status_code=404, detail="삭제할 아이템을 찾을 수 없습니다.")
    return {"message": f"ID {memo_id} 삭제 완료"}

@app.delete("/all")
def clear_database_endpoint(db: Session = Depends(get_db)):
    crud.delete_all_data(db)
    return {"message": "모든 데이터가 삭제되었습니다."}
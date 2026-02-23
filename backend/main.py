from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import model
from backend.ai_service import analyze_memo_with_ai
from .routers import auth

# 우리가 만든 부품들을 가져옵니다.
from .database import Base, engine, get_db
from .models import model  # models 폴더 안의 model.py
from .schemas import schema # schemas 폴더 안의 schema.py
from .crud import crud  # crud 폴더 안의 crud.py

from fastapi.middleware.cors import CORSMiddleware # 프론트엔드 위해 추가

# 1. 서버 시작 시 DB 테이블 생성
# 이 코드가 실행되면 PostgreSQL에 memos와 todos 테이블이 생깁니다.
model.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 모든 접속 허용 (개발 단계에서만!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 라우터 등록 ───────────────────────────────────────
app.include_router(auth.router)

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


@app.get("/todos")
def read_todos(page: int = 1, db: Session = Depends(get_db)):
    limit = 5
    skip = (page - 1) * limit
    
    todos = crud.get_todos(db, skip=skip, limit=limit)
    total_count = crud.get_todos_count(db)
    
    # 데이터와 함께 전체 페이지 수도 같이 보내줍니다.
    return {
        "items": todos,
        "total_pages": (total_count + limit - 1) // limit
    }

@app.patch("/todos/{todo_id}/toggle") # 일부만 수정하므로 PATCH가 적절합니다.
def toggle_todo_status(todo_id: int, db: Session = Depends(get_db)):
    updated_todo = crud.update_todo_status(db, todo_id)
    if not updated_todo:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없습니다.")
    return updated_todo
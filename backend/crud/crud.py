from sqlalchemy.orm import Session
from ..models import model as models  # models/model.py 참조
from ..schemas import schema as schemas  # schemas/schema.py 참조

# 1. 사용자가 입력한 원문 메모 저장하기
def create_memo(db: Session, memo_data: schemas.MemoCreate):
    # 스키마 데이터를 바탕으로 실제 DB 모델 객체 생성
    db_memo = models.Memo(content=memo_data.content)
    db.add(db_memo)
    db.commit()      # DB에 반영
    db.refresh(db_memo)  # DB에서 생성된 ID 등을 다시 읽어오기
    return db_memo

# 2. AI 분석 결과를 바탕으로 할 일 저장하기
# (어떤 메모에서 추출되었는지 알기 위해 memo_id를 함께 받습니다)
def create_todo(db: Session, todo_data: schemas.TodoCreate, memo_id: int):
    db_todo = models.Todo(
        task=todo_data.task,
        date=todo_data.date,
        time=todo_data.time,
        memo_id=memo_id  # 외래키로 메모와 연결
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo
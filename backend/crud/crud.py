from sqlalchemy.orm import Session
from ..models import model as models  # models/model.py 참조
from ..schemas import schema as schemas  # schemas/schema.py 참조
from sqlalchemy import text

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

# todos id별로 테이블 내용 지우기
def delete_todo(db: Session, todo_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
        return True
    return False

def delete_memo(db: Session, memo_id: int):
    db_memo = db.query(models.Memo).filter(models.Memo.id == memo_id).first()
    if db_memo:
        db.delete(db_memo)
        db.commit()
        return True
    return False


# 모든 memos, todos 테이블의 데이터 제거(초기화)
def delete_all_data(db: Session):
    # RESTART IDENTITY가 바로 "번호표를 1번부터 다시 시작하라"는 뜻입니다.
    # CASCADE는 연결된 자식 데이터도 같이 지우라는 뜻입니다.
    db.execute(text("TRUNCATE TABLE todos, memos RESTART IDENTITY CASCADE"))
    db.commit()


def get_todos(db: Session):
    # .order_by()를 사용해 날짜(asc: 오름차순)와 시간 순으로 정렬합니다.
    return db.query(models.Todo).order_by(models.Todo.date.asc(), models.Todo.time.asc()).all()


def update_todo_status(db: Session, todo_id: int):
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if db_todo:
        db_todo.is_completed = not db_todo.is_completed  # 상태 반전
        db.commit()
        db.refresh(db_todo)
        return db_todo
    return None
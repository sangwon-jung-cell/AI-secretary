from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- Todo 관련 스키마 ---

class TodoBase(BaseModel):
    task: str
    date: Optional[str] = None
    time: Optional[str] = None
    is_completed: bool = False

class TodoCreate(TodoBase):
    pass  # 생성할 때는 TodoBase의 필드만 있으면 됨

class Todo(TodoBase):
    id: int
    memo_id: int

    class Config:
        from_attributes = True  # SQLAlchemy 모델 객체를 Pydantic으로 자동 변환

# --- Memo 관련 스키마 ---

class MemoBase(BaseModel):
    content: str

class MemoCreate(MemoBase):
    pass

class Memo(MemoBase):
    id: int
    created_at: datetime
    todos: List[Todo] = []  # 이 메모에서 추출된 할 일 목록을 포함해서 응답

    class Config:
        from_attributes = True
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Memo(Base):
    __tablename__ = "memos"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)  # 사용자가 입력한 전체 문장
    created_at = Column(DateTime, default=datetime.now)

    # Memo와 Todo의 관계 설정 (1대N)
    # 메모 하나에서 여러 개의 할 일이 추출될 수 있음
    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, nullable=False)     # 할 일 내용 (예: 친구와 약속)
    date = Column(String, nullable=True)       # 날짜 (예: 2026-01-22)
    time = Column(String, nullable=True)       # 시간 (예: 18:00)
    is_completed = Column(Boolean, default=False) # 완료 여부
    
    # 외래키: 이 할 일이 어떤 메모에서 왔는지 연결
    memo_id = Column(Integer, ForeignKey("memos.id"))
    
    # 관계 설정
    owner = relationship("Memo", back_populates="todos")
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 데이터베이스 접속 주소
SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/aidb"

# 2. SQLALCHEMY 엔진 생성
# 엔진은 DB에 실제 연결을 관리하는 핵심 객체입니다.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. 세션 생성기
# 세션은 DB와 대화하는 '단위'입니다. (데이터를 넣거나 뺄 때 이 세션을 사용합니다.)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 베이스 클래스
# 이 클래스를 상속받아야 models.py에서 만드는 클래스들이 DB 테이블로 인식됩니다.
Base = declarative_base()

# 5. DB 세션을 가져오는 의존성 주입 함수
# 나중에 FastAPI 엔드포인트에서 DB를 사용할 때 이 함수를 사용하게 됩니다.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
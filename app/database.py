from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
from app.secure.db_config import db_config

Base = declarative_base()

# DB 싱글톤 패턴 유지
class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.engine = cls._instance.create_db_connection()
            Base.metadata.create_all(bind=cls._instance.engine)
        return cls._instance

    def create_db_connection(self):
        # 로컬 MySQL 서버에 직접 연결
        db_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        engine = create_engine(db_url)

        try:
            # 연결 테스트
            connection = engine.connect()
            connection.close()
            print(f"Successfully connected to database {db_config['database']}")
            return engine
        except Exception as e:
            print(f"An error occurred when trying to connect to database {db_config['database']}: {str(e)}")
            raise

    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Database().engine)
    
def get_db():
    # 세션 생성 및 관리
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
      

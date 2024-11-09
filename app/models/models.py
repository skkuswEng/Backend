from sqlalchemy import Column, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    studentId = Column(String, primary_key=True, index=True)
    pw = Column(String)

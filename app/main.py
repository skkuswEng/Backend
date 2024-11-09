from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from fastapi import FastAPI, HTTPException, Depends, status

app = FastAPI()

# Favicon Static
# Get rid of favicon.ico 404 Not Found error
app.mount("/static", StaticFiles(directory="static"), name="static")

# routers
# app.include_router(router_name)

# root router for testing
@app.get('/')
async def home(request: Request):
    domain = request.headers.get("host")
    return {"message": f"Hello from {domain}"}

class UserLogin(BaseModel):
    studentId: str
    pw: str

class UserRegister(BaseModel):
    studentId: str
    pw: str

class UserUnregister(BaseModel):
    studentId: str
    pw: str
    
# 회원가입
@app.post("/auth/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.studentId == user.studentId).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")
    new_user = User(studentId=user.studentId, pw=user.pw )
    db.add(new_user)
    db.commit()
    return {"message": "Registration successful"}

# 로그인
@app.post("/auth/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.studentId == user.studentId, User.pw == user.pw).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "Login successful"}

# 회원탈퇴
@app.post("/auth/unregister")
async def unregister(user: UserUnregister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.studentId == user.studentId, User.pw == user.pw).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    db.delete(db_user)
    db.commit()
    return {"message": "Unregistration successful"}
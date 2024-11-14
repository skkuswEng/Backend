from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.schemas.user.request import LoginRequest, SignUpRequest
from app.schemas.user.response import LoginResponse, SignUpResponse, LoginResponseData

from backend.app.handlers.handler import LoginError

from app.crud.user_crud import user_login, user_signup

router = APIRouter()

@router.post("/user/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user_df = user_login(request.student_id, request.password)

    if user_df.empty:
        # 사용자 정보가 DB에 없음
        raise LoginError(status_code=404, details="User not found")
    else:
        # 사용자 정보가 DB에 있음
        return LoginResponse(
            status="success",
            message="Successfully Logged in",
            content=LoginResponseData
        )
    

@router.post("/user/register", response_model=SignUpResponse)
async def signup(request: SignUpRequest):
    # 회원가입 성공여부
    is_valid = user_signup(request)
    
    if is_valid :
        return SignUpResponse(
            status="success",
            message="Successfully Signed Up"
        )
    else :
        return SignUpResponse(
            status="failure",
            message="Try again"
        )

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.schemas.user.request import LoginRequest, SimulationParamsRequest
from app.schemas.user.response import LoginResponse

from backend.app.handlers.handler import LoginError

from app.crud.user_crud import user_login

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
            status= "success",
            message= "Succesfully Logged in"
        )
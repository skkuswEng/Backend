from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from ..schemas.user.request import LoginRequest, SignUpRequest, UnregisterRequest
from ..schemas.user.response import LoginResponse, SignUpResponse, LoginResponseData, UnregisterResponse

from ..handlers.handler import UserError

from ..crud.user_crud import user_login, user_signup, user_unregister

router = APIRouter()

@router.post("/user/login", response_model=LoginResponse, status_code=200)
async def login(request: LoginRequest):
    user_df = user_login(request.student_id, request.password)

    if user_df.empty:
        # 사용자 정보가 DB에 없음
        raise UserError(status_code=404, detail="없는 유저입니다")
    else:
        # 사용자 정보가 DB에 있음
        return LoginResponse(      
            message="로그인 성공",
            content=LoginResponseData(
                student_id=request.student_id,
                name=str(user_df.name)
            )
        )
    

@router.post("/user/register", response_model=SignUpResponse, status_code=200)
async def signup(request: SignUpRequest):
    # 회원가입 성공여부
    validity = user_signup(request)
    
    if validity["result"] :
        return SignUpResponse(
            message="회원가입 성공"
        )
    else :
        # 409번 에러는 conflict, 이미 회원가입 되어 있음을 타켓팅함
        raise UserError(status_code=409, detail=validity["error"])


@router.post("/user/unregister", response_model=UnregisterResponse)
async def unregister(request: UnregisterRequest):
    unregister_data = user_unregister(request)

    if unregister_data["result"] :
        return UnregisterResponse(
            message="회원 삭제 성공"
        )
    elif unregister_data["error"] == "없는 유저입니다":
        raise UserError(status_code=404, detail=unregister_data["error"])
    elif unregister_data["error"] == "비밀번호가 틀립니다":
        raise UserError(status_code=401, detail=unregister_data["error"])
    else :
        # 뭔가 회원탈퇴 중 DB에러일때
        raise UserError(status_code=400, detail=unregister_data["error"])
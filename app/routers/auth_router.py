from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse

from ..schemas.auth.request import *
from ..schemas.auth.response import *

from ..handlers.handler import UserError

from ..crud.auth_crud import *

from datetime import datetime, timedelta

router = APIRouter()

@router.post("/auth/message-token", response_model=registerAuthTokenResponse )
async def registerAuthToken( request: registerAuthtokenRequest ):
    result = registerAuthTokenDB( request.student_id, request.token )
    print(result)
    if result["result"] == False:
        raise UserError( status_code=500, detail="DB에 토큰 등록 불가능" )
    return registerAuthTokenResponse(
        message="Token Accepted"
    )
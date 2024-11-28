from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse

from ..schemas.auth.request import *
from ..schemas.auth.response import *

from ..handlers.handler import UserError

from ..crud.auth_crud import *

from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, messaging

router = APIRouter()

#Firbase amdin sdk
cred = credentials.Certificate("app/secure/sokk-82ce3-firebase-adminsdk-ajvfn-2b4d13b4ef.json")
firebase_admin.initialize_app(cred)

@router.post("/auth/message-token", response_model=registerAuthTokenResponse )
async def registerAuthToken( request: registerAuthtokenRequest ):
    result = registerAuthTokenDB( request.student_id, request.token )
    print(result)
    if result["result"] == False:
        raise UserError( status_code=500, detail="DB에 토큰 등록 불가능" )
    return registerAuthTokenResponse(
        message="Token Accepted"
    )

#fcm request 
@router.post("/send-push")
async def send_push_notification( request: PushNotificationRequest ):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=request.title,
                body=request.body,
            ),
            token=request.fcm_token,
        )

        response = messaging.send(message)

        return {
            "message": "Notification sent successfully",
            "response_id": response
            }
    except Exception as e:
        print( f"{str(e)}")
        raise UserError(status_code=500, detail=f"Failed to send notification: {str(e)}")
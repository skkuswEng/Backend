from pydantic import BaseModel
from app.schemas.base_schema import RequestModel
from typing import Optional

class registerAuthtokenRequest(RequestModel):
    student_id: str
    token: str
    
class PushNotificationRequest(BaseModel):
    title: str
    body: str
    fcm_token: str
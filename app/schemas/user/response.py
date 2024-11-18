from pydantic import BaseModel
from app.schemas.base_schema import ResponseModel
from typing import Optional

# Login
class LoginResponseData(BaseModel):
    student_id: str
    name: str

class LoginResponse(ResponseModel):
    message: str
    content: LoginResponseData

# Sign up
class SignUpResponse(ResponseModel):
    message: str 

# Unregister
class UnregisterResponse(ResponseModel):
    message: str
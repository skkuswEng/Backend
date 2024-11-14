from app.schemas.base_schema import ResponseModel
from typing import Optional

# Login
class LoginResponseData():
    student_id: str
    name: str

class LoginResponse(ResponseModel):
    status: str
    message: str

# Sign up
class SignUpResponse(ResponseModel):
    status: str
    message: str 
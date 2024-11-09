from app.schemas.base_schema import ResponseModel
from typing import Optional

# Login
class LoginResponse(ResponseModel):
    status: str
    message: str

# Sign up
class SignUpResponse(ResponseModel):
    status: str
    message: str 
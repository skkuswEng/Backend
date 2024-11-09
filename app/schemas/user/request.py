from app.schemas.base_schema import ResponseModel
from typing import Optional

# Login
class LoginRequest(ResponseModel):
    student_id: str
    password: str

# Sign up
class SignUpRequest(ResponseModel):
    student_id: str
    password: str
    student_name: str
    email: str
    # is_admin: bool
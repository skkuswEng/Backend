from app.schemas.base_schema import RequestModel
from typing import Optional

# Login
class LoginRequest(RequestModel):
    student_id: str
    password: str

# Sign up
class SignUpRequest(RequestModel):
    student_id: str
    password: str
    student_name: str
    email: str
    # is_admin: bool

# Unregister
class UnregisterRequest(RequestModel):
    student_id: str
    password: str
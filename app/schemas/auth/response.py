from pydantic import BaseModel
from app.schemas.base_schema import ResponseModel
from typing import List, Optional

#response
class registerAuthTokenResponse(ResponseModel):
    message: str
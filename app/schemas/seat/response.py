from pydantic import BaseModel
from app.schemas.base_schema import ResponseModel
from typing import List, Optional

# Response Data
class SeatListData(BaseModel):
    seat_list: list[bool]
class ReservedSeatData(BaseModel):
    seat_number: int
    
#Response
class SeatStatusResponse(ResponseModel):
    message: str
    content: SeatListData

class SeatReserveResponse(ResponseModel):
    message: str
    
class SeatReservedSearchResponse(ResponseModel):
    message: str
    content: ReservedSeatData

class SeatUnreserveResponse(ResponseModel):
    message: str
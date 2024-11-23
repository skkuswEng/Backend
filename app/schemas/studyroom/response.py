from pydantic import BaseModel
from app.schemas.base_schema import ResponseModel
from typing import Dict

# Room Status
class RoomStatusResponse(ResponseModel):
    message: str
    content: dict   # {"09:00": true,, "09:30": false, ...}

# Room Reservation
class RoomReservationResponse(ResponseModel):
    message: str            
    content: Dict[str, int] # 예약 완료 정보 {"reservation_id: 예약 id"}
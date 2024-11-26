from pydantic import BaseModel
from app.schemas.base_schema import ResponseModel
from typing import Dict, List

# Room Status
class RoomStatusResponse(ResponseModel):
    message: str
    content: dict   # {"09:00": true,, "09:30": false, ...}

# Room Reservation
class RoomReservationResponse(ResponseModel):
    message: str            
    content: Dict[str, int] # 예약 완료 정보 {"reservation_id: 예약 id"}

class CompanionData(BaseModel):
    student_id: str
    name: str


class LeaderData(BaseModel):
    student_id: str
    name: str


class ReserveData(BaseModel):
    room_number: int
    startDate: str  # ISO 형식의 날짜 문자열
    endDate: str    # ISO 형식의 날짜 문자열
    leader: LeaderData
    companionData: List[CompanionData]

class ReservationContent(BaseModel):
    reserve: List[ReserveData]

class ReservationQueryResponse(ResponseModel):
    message: str
    content: ReservationContent

class ReservationUpdateResponse(BaseModel):
    message: str
    content: None  # 명세서에 따라 null로 설정

class ReservationUnreserveResponse(BaseModel):
    message: str
    content: None  # 명세서에 따라 null로 설정

from pydantic import BaseModel
from app.schemas.base_schema import RequestModel
from fastapi import Query
from typing import List

# Room Status
class RoomStatusRequest(RequestModel):
    room_id: int = Query(..., ge=1, le=3)   # 방 번호 1~3
    date: str                               # YYYY-MM-DD 형식


# Room Reservation
class CompanionData(BaseModel):
    student_id: str                         # 동반 이용자 학번
    name: str                               # 동반 이용자 이름

class ReserveTime(BaseModel):
    startTime: str                          # 예약 시작 시간
    endTime: str                            # 예약 종료 시간

class RoomReservationRequest(RequestModel):
    student_id: str                         # 대표자 학생
    room_id: int                            # 방 번호
    start_time: str                         # 예약 날짜 (ISOString, e.g., "2024-11-21")
    end_time: str                           # 예약 날짜 (ISOString, e.g., "2024-11-21")
    reserve_time: ReserveTime               # 예약 시간
    companion: List[CompanionData]          # 동반 이용자 리스트

class GetRoomReservationRequest(RequestModel):
    student_id: str

class ReservationUpdateRequest(BaseModel):
    student_id: int  # 대표자
    room_number: int  # 1 | 2 | 3
    startDate: str  # ISOString
    endDate: str  # ISOString
    companion: List[CompanionData]

class ReservationUnreserveRequest(BaseModel):
    student_id: int  # 요청한 사람 (대표자)
    startDate: str  # ISOString
    endDate: str  # ISOString
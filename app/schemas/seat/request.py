from pydantic import BaseModel
from app.schemas.base_schema import RequestModel
from typing import Optional

#좌석 상태(ai 판별)
class Seat(BaseModel):
    seat_number: int
    seat_status: str
#좌석 리스트(ai)
class SeatRenewRequest(RequestModel):
    seats: list[Seat]
    
# 학생을 좌석에 배정 요청
class ReserveSeatRequest(RequestModel):
    student_id: str
    seat_number: int
    reservation_date: str

# 학생의 예약 내역  
class SearchReservedSeatRequest(RequestModel):
    student_id: str

# 학생 좌석 반납
class UnreserveSeatRequest(RequestModel):
    student_id: str
    seat_number: int
from app.schemas.base_schema import RequestModel
from typing import Optional

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
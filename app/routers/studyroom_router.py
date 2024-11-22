from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from ..schemas.studyroom.request import RoomStatusRequest, RoomReservationRequest
from ..schemas.studyroom.response import RoomStatusResponse, RoomReservationResponse

from ..handlers.handler import UserError

from ..crud.user_crud import check_duplicate_user
from ..crud.studyroom_crud import get_room_time, check_duplicate_time, create_room_reservation

from datetime import datetime, timedelta
from typing import Dict

router = APIRouter()

@router.get("/room/status", response_model=RoomStatusResponse, status_code=200)
async def get_room_status(queries: RoomStatusRequest):
    try: 
        date = datetime.strptime(queries.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="ISO 형식의 날짜가 아닙니다. YYYY-MM-DD 형식으로 보내주세요")
    
    if queries.room_id not in [1, 2, 3]: # 방 번호 검증
        raise HTTPException(status_code=400, detail="room_id가 잘못 되었습니다. 1, 2, 3만 가능합니다.")
    
    # 하루의 시작/ 끝 시간 설정 (08:00 ~ 22:00)
    start_time = datetime(date.year, date.month, date.day, 8, 0, 0)
    end_time = datetime(date.year, date.month, date.day, 22, 0, 0)

    data = {
        "room_number": queries.room_id,
        "start_time": start_time,
        "end_time": end_time
    }

    timetable = get_room_time(data)

    # 예약된 시간대를 추출 (HH:MM 형식으로 변환)
    reserved_slots = set(res[0].strftime("%H:%M") for res in timetable)

    # 30분 간격으로 모든 시간대 생성
    time_slots: Dict[str, bool] = {}
    current_time = start_time
    while current_time < end_time:
        time_str = current_time.strftime("%H:%M")
        time_slots[time_str] = time_str in reserved_slots  # 예약 여부 저장
        current_time += timedelta(minutes=30)  # 30분 간격 추가

    return {
        "message": f"room_number {queries.room_id}, date {queries.date} status",
        "content": time_slots
    }


@router.post("/room/reserve", response_model=RoomReservationResponse, status_code=200)
async def reserve_studyroom(request: RoomReservationRequest):
    # request data 검증 및 파싱
    try:
        date = datetime.strptime(request.date, "%Y-%m-%d") # ISO 날짜 형식 확인
    except ValueError:
        raise HTTPException(status_code=400, detail="ISO 형식의 날짜가 아닙니다. YYYY-MM-DD 형식으로 보내주세요")
    
    # 시간 파싱
    try:
        start_time = datetime.strptime(f"{request.date} {request.reserve_time.startTime}", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{request.date} {request.reserve_time.endTime}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="예약 시간이 올바르지 않습니다. HH:MM 형식으로 보내주세요.")
    
    # 방 번호 검증
    if request.room_id not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="room_id가 잘못되었습니다. 1, 2, 3만 가능합니다.")

    # 예약 시간이 올바른지 검증
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="예약 시작 시간은 종료 시간보다 이전이어야 합니다.")

    # 예약 중복 확인
    data = {
        "room_number": request.room_id,
        "start_time": start_time,
        "end_time": end_time
    }

    is_dup_reserved = check_duplicate_time(data)

    if is_dup_reserved > 0:
        raise HTTPException(status_code=400, detail="해당 시간에 이미 예약이 있습니다.")
    
    # 대표자 및 동반 이용자 검증 (동반자가 학생인지 확인 ==> 대표자는 이미 로그인을 했으니 학생임)
    for companion in request.companion:
        user_check_result = check_duplicate_user(companion.student_id)
        if user_check_result == 0:
            raise HTTPException(status_code=400, detail=f"동반 이용자 {companion.name} 은(는) 등록된 학생이 아닙니다.")
        
    # 예약 데이터 DB에 추가
    # 대표자 추가, is_leader boolean 추가
    reservation_ids = create_room_reservation(
        room_id=request.room_id,
        start_time=start_time,
        end_time=end_time,
        companions=request.companion
    )

    return {
        "message": "예약이 완료되었습니다.",
        "content": None
    }
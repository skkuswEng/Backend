from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from ..schemas.studyroom.request import RoomStatusRequest, RoomReservationRequest, GetRoomReservationRequest, ReservationUpdateRequest, ReservationUnreserveRequest
from ..schemas.studyroom.response import RoomStatusResponse, RoomReservationResponse, ReservationQueryResponse, ReservationUpdateResponse, ReservationUnreserveResponse

from ..handlers.handler import UserError

from ..crud.user_crud import check_duplicate_user
from ..crud.studyroom_crud import get_room_time, check_duplicate_time, create_room_reservation, fetch_future_reservations, is_reservation_exists, update_reservation_in_db, delete_reservation_in_db

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

    timetable = get_room_time(queries.room_id, start_time, end_time)

    # 예약된 시간대를 추출 (HH:MM 형식으로 변환)
    reserved_slots = set(res[0].strftime("%H:%M") for res in timetable)

    # 30분 간격으로 모든 시간대 생성
    time_slots: Dict[str, bool] = {}
    current_time = start_time
    while current_time < end_time:
        time_str = current_time.strftime("%H:%M")
        # 현재 시간대가 예약된 시간대에 포함되어 있는지 확인
        time_slots[time_str] = any(
            res_start <= current_time < res_end for res_start, res_end in reserved_slots
        )
        current_time += timedelta(minutes=30)  # 30분 간격 추가

    return {
        "message": f"room_number {queries.room_id}, date {queries.date} status",
        "content": time_slots
    }


@router.post("/room/reserve", response_model=RoomReservationResponse, status_code=200)
async def reserve_studyroom(request: RoomReservationRequest):
    # request data 검증 및 파싱
    try:
        start_time = datetime.strptime(request.startDate, "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.strptime(request.endDate, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="ISO 형식의 날짜가 아닙니다. YYYY-MM-DD 형식으로 보내주세요")
    
    # 방 번호 검증
    if request.room_id not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="room_id가 잘못되었습니다. 1, 2, 3만 가능합니다.")

    # 예약 시간이 올바른지 검증
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="예약 시작 시간은 종료 시간보다 이전이어야 합니다.")

    # 예약 중복 확인

    if check_duplicate_time(request.room_id, start_time, end_time):
        raise HTTPException(status_code=400, detail="해당 시간에 이미 예약이 있습니다.")
    
    # 대표자 및 동반 이용자 검증 (동반자가 학생인지 확인 ==> 대표자는 이미 로그인을 했으니 학생임)
    for companion in request.companion:
        user_check_result = check_duplicate_user(companion.student_id)
        if user_check_result == 0:
            raise HTTPException(status_code=400, detail=f"동반 이용자 {companion.name} 은(는) 등록된 학생이 아닙니다.")
        
    # 예약 데이터 DB에 추가
    create_room_reservation(
        room_id=request.room_id,
        start_time=start_time,
        end_time=end_time,
        leader_id=request.student_id,
        companions=request.companion
    )

    return {
        "message": "예약이 완료되었습니다.",
        "content": None
    }

# 예약 내역 조회
@router.get("/room/reservation", response_model=ReservationQueryResponse, status_code=200)
async def get_reservation_history(queries: GetRoomReservationRequest):
    """
    특정 유저가 예약한 스터디룸의 미래 예약 내역을 조회합니다.
    """
    # 유효한 student_id인지 확인
    if check_duplicate_user(queries.student_id) == 0:
        raise HTTPException(status_code=400, detail="유효하지 않은 학생 ID입니다.")
    
    # 미래 예약 데이터 조회
    reservations = fetch_future_reservations(queries.student_id)

    return {
        "message": "Get Reservation Data",
        "content": {
            "reserve": reservations
        }
    }


@router.post("/room/update", response_model=ReservationUpdateResponse, status_code=200)
async def update_reservation(request: ReservationUpdateRequest):
    """
    예약 내용을 수정하는 API.
    """
    # 시간 형식 검증
    try:
        start_time = datetime.strptime(request.startDate, "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.strptime(request.endDate, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="ISO 형식의 날짜와 시간이 아닙니다. YYYY-MM-DDTHH:MM:SS 형식으로 보내주세요.")
    
    # 예약 시간 검증
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="예약 시작 시간은 종료 시간보다 이전이어야 합니다.")
    
    # 예약 존재 여부 확인
    if not is_reservation_exists(request.student_id, request.room_number, start_time, end_time):
        raise HTTPException(status_code=400, detail="해당 예약이 존재하지 않습니다.")
    
    # 예약 내용 업데이트
    update_reservation_in_db(request.student_id, request.room_number, start_time, end_time, request.companion)
    
    return {"message": "reservation updated", "content": None}


@router.delete("/room/unreserve", response_model=ReservationUnreserveResponse, status_code=200)
async def delete_reservation(request: ReservationUnreserveRequest):
    """
    예약 내용을 취소하는 API.
    """
    # 시간 형식 검증
    try:
        start_time = datetime.strptime(request.startDate, "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.strptime(request.endDate, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="ISO 형식의 날짜와 시간이 아닙니다. YYYY-MM-DDTHH:MM:SS 형식으로 보내주세요.")
    
    # 예약 존재 여부 확인
    if not is_reservation_exists(request.student_id, start_time, end_time):
        raise HTTPException(status_code=400, detail="존재하지 않는 예약입니다.")
    
    # 예약 취소
    delete_reservation_in_db(request.student_id, start_time, end_time)
    
    return {"message": "Unreserve completed", "content": None}
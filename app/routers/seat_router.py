from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from ..schemas.seat.request import *
from ..schemas.seat.response import *

from ..handlers.handler import UserError

from ..crud.seat_crud import *

router = APIRouter()

@router.get("/seat/status", response_model=SeatStatusResponse, status_code=200)
async def getSeatList( ):
    # get all seats from DB
    seat_df = getSeatData()
    #print("Debug: seat_df = ", seat_df)
    # seat_data에 student_id 가 없는 좌석을 false, 그외엔 bool로 list 넘겨야함
    seat_status_list = seat_df["is_reserved"].astype(bool).tolist()
    
    #response
    return SeatStatusResponse(
        message = "Get Seat Status",
        content= SeatListData(
            seat_list = seat_status_list
        )
    )

@router.post("/seat/reserve", response_model=SeatReserveResponse, status_code=200 )
async def ReserveSeat(request: ReserveSeatRequest ):
    # get selected seat from DB
    seat_df = getSelectedSeatData(request.seat_number)
    room_reservation_df = getUserRoomReservation( request.student_id )
    seat_reservation_df = getUserSeatReservation( request.student_id )
    # reponse
    if seat_df.empty: 
        raise HTTPException( status_code=404, detail="요청한 seat_number가 존재하지 않습니다")
    else :
        if seat_df["is_reserved"].any() == True :
            raise HTTPException( status_code=409, detail="이미 배정된 좌석입니다")
        if room_reservation_df.empty == False :
            raise HTTPException( status_code=409, detail="이미 해당 시간에 스터디룸 예약한 상황입니다")
        if seat_reservation_df.empty == False :
            raise HTTPException(status_code=409, detail="이미 다른 좌석을 예약한 상황입니다.")
        #date = datetime.strptime( request.date, "%Y-%m-%d")
        #result = reserveSeat( request.student_name, request.seat_number, request.reservation_date )
        return SeatReserveResponse(
            message= "Reservation Complete"
        )
    
@router.get("/seat/reservation?quries", response_model=SeatReservedSearchResponse)
async def SearchReservedSeat( request: SearchReservedSeatRequest ):
    seat_reservation_df = getUserSeatReservation( request.student_id )
    
    if seat_reservation_df.empty == True:
        return SeatReservedSearchResponse(
            message = "Get User Seat Status"
        )
    else :
        return SeatReservedSearchResponse(
            message = "Get User Seat Status",
            content = ReservedSeatData(
                seat_number = seat_reservation_df.seat_number
            )
        )
@router.delete("/seat/unreserve", response_model=SeatUnreserveResponse )
async def UnreserveSeat( request: UnreserveSeatRequest ):
    seat_reservation_df = getUserSeatReservation( request.student_id )
    if seat_reservation_df.empty == True :
        raise HTTPException( status_code=409, detail="해당 유저가 예약한 좌석이 없습니다.")
    
    elif seat_reservation_df.seat_number == request.seat_number :
        result = UnreserveSeat( request.seat_number )
        if result == False :
            raise HTTPException(status_code=409, detail="좌석 반납중 서버 DB에서 에러 발생")
        else :
            return SeatUnreserveResponse(
                message="Unreserve completed"
            )

    raise HTTPException( status_code=400, detail="요청 오류 있음")
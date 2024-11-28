from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse

from ..schemas.seat.request import *
from ..schemas.seat.response import *

from ..handlers.handler import UserError

from ..crud.seat_crud import *

from datetime import datetime, timedelta

from .auth_router import send_push_notification
from ..crud.auth_crud import *
from ..schemas.auth.request import *

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
    reservation_date = datetime.strptime( request.reservation_date, "%Y-%m-%d %H:%M")
    # get selected seat from DB
    seat_df = getSelectedSeatData(request.seat_number)
    room_reservation_df = getUserStudyroom( request.student_id, reservation_date )
    seat_reservation_df = getUserSeatReservation( request.student_id )
    # reponse
    if seat_df.empty: 
        raise UserError( status_code=404, detail="요청한 seat_number가 존재하지 않습니다") # 확인
    else :
        if seat_df["is_reserved"].any() == True :
            raise UserError( status_code=409, detail="이미 배정된 좌석입니다") #확인
        if room_reservation_df.empty == False:
            raise UserError( status_code=409, detail="이미 해당 시간에 스터디룸 예약한 상황입니다") #확인 
        if seat_reservation_df.empty == False :
            raise UserError(status_code=409, detail="이미 다른 좌석을 예약한 상황입니다.") #확인

        result = reserveSeat( request.student_id, request.seat_number, request.reservation_date )
        
        if result["result"] == False:
            raise UserError( status_code=500, detail="좌석 배정 중 db 오류")
        return SeatReserveResponse(
            message= "Reservation Complete"
        )
    
@router.get("/seat/reservation", response_model=SeatReservedSearchResponse)
async def SearchReservedSeat( student_id: str= Query(...) ):
    seat_reservation_df = getUserSeatReservation( student_id )
    
    if seat_reservation_df.empty == True:
        return SeatReservedSearchResponse(
            message = "Get User Seat Status",
            content = ReservedSeatData(
                seat_number = 0 # NUll 의미
            )
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
        raise UserError( status_code=409, detail="해당 유저가 예약한 좌석이 없습니다.")
    
    #print( "df: ", int( seat_reservation_df.seat_number ) )
    #print( "req: ", request.seat_number )
    if seat_reservation_df.seat_number.iloc[0] == request.seat_number :
        result = unreserveSeat( request.seat_number )
        if result["result"] == False :
            raise UserError(status_code=409, detail="좌석 반납중 서버 DB에서 에러 발생")
        else :
            return SeatUnreserveResponse(
                message="Unreserve completed"
            )
    else:
        raise UserError( status_code=400, detail="요청 오류 있음")
    
@router.post("/seat/renew", response_model=SeatRenewResponse )
async def renewSeat( request: SeatRenewRequest ):
    for seat in request.seats:
        if seat.seat_status == "Occupied" :
            renewCountRst = resetSeatCount( seat.seat_number )
        else:
            renewCountRst = addSeatCount( seat.seat_number )
        
        if renewCountRst["result"] == False:
            raise UserError(status_code=409, detail="좌석 갱신 중 db 에러")
    
    
    returnSeatRst = returnSeat()
    if returnSeatRst["result"] == False:
            raise UserError(status_code=409, detail="좌석 자동 반납 중 db 에러")
    
    if returnSeatRst["rowcount"] > 0 :
        #Seat data 
        rows_data = returnSeatRst["rows"]
        
        for row in rows_data:
            #Get student's token
            token_df = searchStudentToken(row["student_id"])
            #push_request to FCM
            push_request = PushNotificationRequest(
                title="Return seat notification",
                body="Your reservation has been returned automatically",
                fcm_token= token_df.fcm_token.iloc[0]
            )
            result = await send_push_notification(push_request)
            print( f" result in seat_router: {result}")
    return SeatRenewResponse(
        message="Renew complete"
    )
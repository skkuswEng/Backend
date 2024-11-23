from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from ..schemas.user.request import LoginRequest, SignUpRequest, UnregisterRequest
from ..schemas.user.response import LoginResponse, SignUpResponse, LoginResponseData, UnregisterResponse

from ..handlers.handler import UserError

from ..crud.user_crud import user_login, user_signup, user_unregister

router = APIRouter()

@router.get("/seat/status", response_model=SeatStatusResponse, status_code=200)
async def getSeatList( ):
    # get all seats from DB
    seat_df = getSeatData()
    
    # seat_data에 student_id 가 없는 좌석을 false, 그외엔 bool로 list 넘겨야함
    seat_status_list = [
        False if seat["is_reserved"] is False else True for seat in seat_df
    ]
    #response
    return SeatStatusResponse(
        message = "Get Seat Status"
        content= SeatListData(
            seat_status_list
        )
    )

@router.post("/seat/reserve", response_model=SeatReserveResponse, status_code=200 )
async def ReserveSeat(request: ReserveRequest ):
    # get selected seat from DB
    seat_df = getSelectedSeatData(request.seat_number)
    # reponse
    if seat_df.emtpy: 
        return UserError( status_code=404)
    else :
        if ( seat_df.is_reserved == True )
            return UserError( status_code=)
        return SeatReserveResponse(
            message= "Reservation Complete"
        )
        
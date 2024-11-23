from app.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text

import pandas as pd

from app.utils.functions import hash_password
engine = Database().get_engine()

def getSeatData():
    query = """
        SELECT *
        FROM Seat;
    """
    seat_df = pd.read_sql(query, engine )
    return seat_df

def getSelectedSeatData(seat_number: int ):
    query = """
        SELECT * 
        FROM Seat
        WHERE seat_number = %s;
    """
    params = (seat_number, )
    seat_df = pd.read_sql( query, engine, params=params )

    return seat_df

def getUserRoomReservation( student_id: str ):
    query = """
        SELECT *
        FROM Reservation
        WHERE student_id = %s;
    """
    params = (student_id, )
    room_reservation_df = pd.read_sql( query, engine, params=params )
    return room_reservation_df

def getUserSeatReservation( student_id: str ):
    query = """
        SELECT *
        FROM Seat
        WHERE  student_id = %s;
    """
    params = (student_id, )
    seat_reservation_df = pd.read_sql( query, engine, params=params)
    return seat_reservation_df

def reserveSeat( student_id: str, seat_number: int, reservation_date: str):
    return True
    
def UnreserveSeat( seat_number: int ):
    with Session(engine) as session:
        try:
            unreserve_query = """
                UPDATE Seat
                SET 
                    student_id = NULL,
                    time = NULL,
                    is_reserved = FALSE
                WHERE 
                    seat_number = :seat_number;
            """
            session.execute(
                text(unreserve_query),
                {"seat_number": seat_number }
            )
            sessoin.commit()
        except Exception as e:
            session.rollback()
            return{
                "result": False,
                "error": f"좌석 반납 중 에러 발생: {str(e)}"
            }
        
        return {
            "result": True,
            "message" : "좌석 반납 성공"
        }
            
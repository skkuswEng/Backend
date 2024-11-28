from app.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text

import pandas as pd

from app.utils.functions import hash_password
from datetime import datetime, timedelta
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

def getUserReservation( student_id: str, reservation_date: datetime ):
    query = """
        SELECT *
        FROM Reservation
        WHERE student_id = %s
        AND start_time <= %s
        AND %s <= end_time;
    """
    params = (student_id, reservation_date, reservation_date )
    room_reservation_df = pd.read_sql( query, engine, params=params )
    return room_reservation_df

def getUserStudyroom( student_id: str, reservation_date: datetime ):
    query = """
        SELECT *
        FROM Studyroom
        WHERE student_id = %s
        AND start_time <= %s
        AND %s <= end_time;
    """
    params = (student_id, reservation_date, reservation_date )
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
    with Session(engine) as session:
        try:
            reserve_query = """
                UPDATE Seat
                SET
                    student_id = :student_id,
                    time = :reservation_date,
                    is_reserved = TRUE
                WHERE
                    seat_number = :seat_number;
            """
            session.execute(
                text(reserve_query),
                {
                    "student_id": student_id, 
                    "reservation_date": reservation_date,
                    "seat_number": seat_number 
                }
            )
            session.commit()
            
            return {
                "result": True,
                "message": "좌석 배정 성공"
            }
        except Exception as e:
            session.rollback()
            return {
                "result" : False,
                "error": f"좌석 배정 중 에러 발생: {str(e)}"
            }
    
def unreserveSeat( seat_number: int ):
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
            session.commit()
            return {
                "result": True,
                "message" : "좌석 반납 성공"
            }
        except Exception as e:
            session.rollback()
            return{
                "result": False,
                "error": f"좌석 반납 중 에러 발생: {str(e)}"
            }
def addSeatCount( seat_number: int):
    with Session(engine) as session:
        try:
            renewSeat_query = """
                UPDATE Seat
                SET 
                    count = count + 1
                WHERE 
                    seat_number = :seat_number
                    AND is_reserved = TRUE;
            """
            session.execute(
                text(renewSeat_query),
                { "seat_number": seat_number }
            )
            session.commit()
            
            return {
                "result": True,
                "message" : "좌석 갱신 성공"
            }
        except Exception as e:
            session.rollback()
            return{
                "result": False,
                "error": f"좌석 갱신 중 에러 발생: {str(e)}"
            }
            
def resetSeatCount( seat_number: int):
    with Session(engine) as session:
        try:
            renewSeat_query = """
                UPDATE Seat
                SET 
                    count = 0
                WHERE 
                    seat_number = :seat_number
                    AND is_reserved = TRUE;
            """
            session.execute(
                text(renewSeat_query),
                { "seat_number": seat_number }
            )
            session.commit()
            
            return {
                "result": True,
                "message" : "좌석 갱신 성공"
            }
        except Exception as e:
            session.rollback()
            return{
                "result": False,
                "error": f"좌석 갱신 중 에러 발생: {str(e)}"
            }
            
def returnSeat():
    with Session(engine) as session:
        try:
            renewSeat_query = """
                UPDATE Seat
                SET 
                    student_id = NULL,
                    time = NULL,
                    is_reserved = FALSE,
                    count = 0
                WHERE 
                    is_reserved = TRUE
                    AND count >= 20;
            """
            result = session.execute(
                text(renewSeat_query),
            )
            session.commit()
            
            if result.rowcount == 0:
                return {
                    "result": True,
                    "message" : "자동 반납할 좌석 없음"
                }
            else :
                return {
                    "result": True,
                    "message" : "좌석 자동 반납 성공"
                }
        except Exception as e:
            session.rollback()
            return{
                "result": False,
                "error": f"좌석 자동 반납 중 에러 발생: {str(e)}"
            }
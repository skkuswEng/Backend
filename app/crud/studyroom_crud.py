from app.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import List

import pandas as pd

from ..schemas.studyroom.request import CompanionData

engine = Database().get_engine()

# 스터디룸 상태 확인
def get_room_time(room_id: int, start_time: datetime, end_time: datetime):
    query = """
    SELECT time FROM Studyroom
    WHERE room_number = %s
    AND start_time < %s
    AND end_time > %s
    """

    params = (room_id, end_time, start_time)

    reserved_df = pd.read_sql(query, engine, params=params)

    # start_time과 end_time 컬럼을 datetime 객체로 변환하여 튜플로 반환
    return [
        (row["start_time"], row["end_time"]) 
        for _, row in reserved_df.iterrows()
    ]

# 예약 중복 확인
def check_duplicate_time(room_id: int, start_time: datetime, end_time: datetime):
    query = """
    SELECT COUNT(*) 
    FROM Studyroom
    WHERE room_number = %s
    AND (start_time < %s AND end_time > %s)
    """
    result = engine.execute(query, (room_id, end_time, start_time)).scalar()
    return result > 0


# 스터디룸 예약
def create_room_reservation(
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        leader_id: str,
        companions: List[CompanionData]
):
    # 대표자 예약 추가
    query = """
    INSERT INTO Studyroom (room_number, student_id, start_time, end_time, is_leader)
    VALUES (%s, %s, %s, %s, %s)
    """
    engine.execute(query, (room_id, leader_id, start_time, end_time, True))
    
    # 동반자 예약 추가
    for companion in companions:
        engine.execute(query, (room_id, companion.student_id, start_time, end_time, False))


def fetch_companions(room_number: int, start_time: datetime, end_time: datetime) -> List[dict]:
    """
    특정 예약에 속한 동반 이용자 정보를 조회합니다.
    """
    query = """
    SELECT u.student_id, u.name
    FROM Studyroom sr
    JOIN User u ON sr.student_id = u.student_id
    WHERE sr.room_number = %s
    AND sr.start_time = %s
    AND sr.end_time = %s
    AND sr.is_leader = FALSE
    """
    params = (room_number, start_time, end_time)
    
    result = engine.execute(query, params)
    
    companions = []
    for row in result:
        companions.append({
            "student_id": row["student_id"],
            "name": row["name"]
        })
    
    return companions

def fetch_future_reservations(student_id: int) -> List[dict]:
    """
    주어진 student_id의 미래 예약 내역을 DB에서 조회합니다.
    """
    query = """
    SELECT sr.room_number, sr.start_time, sr.end_time, sr.is_leader, u.student_id, u.name
    FROM Studyroom sr
    JOIN User u ON sr.student_id = u.student_id
    WHERE sr.student_id = %s
    AND sr.start_time > NOW()
    ORDER BY sr.start_time DESC
    """
    params = (student_id,)
    
    result = engine.execute(query, params)
    
    reservations = []
    for row in result:
        if row["is_leader"]:  # 대표자일 경우
            reservations.append({
                "room_number": row["room_number"],
                "startDate": row["start_time"].isoformat(),
                "endDate": row["end_time"].isoformat(),
                "leader": {"student_id": row["student_id"], "name": row["name"]},
                "companionData": fetch_companions(row["room_number"], row["start_time"], row["end_time"])
            })
    
    return reservations


def is_reservation_exists(student_id: int, room_number: int, start_time: datetime, end_time: datetime) -> bool:
    """
    예약이 존재하는지 확인하는 함수.
    """
    query = """
    SELECT COUNT(*)
    FROM Studyroom
    WHERE student_id = %s
    AND room_number = %s
    AND start_time = %s
    AND end_time = %s
    """
    params = (student_id, room_number, start_time, end_time)
    result = engine.execute(query, params).scalar()
    return result > 0


def update_reservation_in_db(student_id: int, room_number: int, start_time: datetime, end_time: datetime, companions: List[CompanionData]):
    """
    예약 내용을 수정하는 함수.
    """
    # 기존 예약 삭제
    delete_query = """
    DELETE FROM Studyroom
    WHERE student_id = %s
    AND room_number = %s
    AND start_time = %s
    AND end_time = %s
    """
    engine.execute(delete_query, (student_id, room_number, start_time, end_time))

    # 새로운 예약 삽입
    insert_query = """
    INSERT INTO Studyroom (room_number, student_id, start_time, end_time, is_leader)
    VALUES (%s, %s, %s, %s, %s)
    """
    # 대표자 예약
    engine.execute(insert_query, (room_number, student_id, start_time, end_time, True))

    # 동반자 예약
    for companion in companions:
        engine.execute(insert_query, (room_number, companion.student_id, start_time, end_time, False))
        

def delete_reservation_in_db(student_id: int, start_time: datetime, end_time: datetime):
    """
    예약 내용을 취소하는 함수.
    """
    query = """
    DELETE FROM Studyroom
    WHERE start_time = %s
    AND end_time = %s
    AND room_number = (
        SELECT room_number
        FROM Studyroom
        WHERE student_id = %s
        AND start_time = %s
        AND end_time = %s
        AND is_leader = TRUE
    )
    """
    params = (start_time, end_time, student_id, start_time, end_time)
    engine.execute(query, params)

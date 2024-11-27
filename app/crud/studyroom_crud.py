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
    SELECT start_time, end_time FROM Studyroom
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
    query = text("""
    SELECT COUNT(*) 
    FROM Studyroom
    WHERE room_number = :room_id
    AND (start_time < :end_time AND end_time > :start_time)
    """)
    with Session(engine) as session:
        result = session.execute(query, {
            "room_id": room_id,
            "end_time": end_time,
            "start_time": start_time
        }).scalar()
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
    query = text("""
    INSERT INTO Studyroom (room_number, student_id, start_time, end_time, is_leader)
    VALUES (:room_id, :student_id, :start_time, :end_time, :is_leader)
    """)
    with Session(engine) as session:
        # 대표자 추가
        session.execute(query, {
            "room_id": room_id,
            "student_id": leader_id,
            "start_time": start_time,
            "end_time": end_time,
            "is_leader": True
        })

        # 동반자 추가
        for companion in companions:
            session.execute(query, {
                "room_id": room_id,
                "student_id": companion.student_id,
                "start_time": start_time,
                "end_time": end_time,
                "is_leader": False
            })

        # 트랜잭션 커밋
        session.commit()


def fetch_companions(room_number: int, start_time: datetime, end_time: datetime) -> List[dict]:
    """
    특정 예약에 속한 동반 이용자 정보를 조회합니다.
    """
    query = text("""
    SELECT u.student_id, u.name
    FROM Studyroom sr
    JOIN User u ON sr.student_id = u.student_id
    WHERE sr.room_number = :room_number
    AND sr.start_time = :start_time
    AND sr.end_time = :end_time
    AND sr.is_leader = FALSE
    """)
    
    with Session(engine) as session:
        result = session.execute(query, {
            "room_number": room_number,
            "start_time": start_time,
            "end_time": end_time
        }).mappings().fetchall()

    companions = [
        {"student_id": row["student_id"], "name": row["name"]}
        for row in result
    ]
    return companions

def fetch_future_reservations(student_id: int) -> List[dict]:
    """
    주어진 student_id의 미래 예약 내역을 DB에서 조회합니다.
    """
    query = text("""
    SELECT sr.room_number, sr.start_time, sr.end_time, sr.is_leader, u.student_id, u.name
    FROM Studyroom sr
    JOIN User u ON sr.student_id = u.student_id
    WHERE sr.student_id = :student_id
    AND sr.start_time > NOW()
    ORDER BY sr.start_time DESC
    """)
    
    with Session(engine) as session:
        result = session.execute(query, {"student_id": student_id}).mappings().fetchall()
    
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
    query = text("""
    SELECT COUNT(*)
    FROM Studyroom
    WHERE student_id = :student_id
    AND room_number = :room_number
    AND start_time = :start_time
    AND end_time = :end_time
    """)
    
    with Session(engine) as session:
        result = session.execute(query, {
            "student_id": student_id,
            "room_number": room_number,
            "start_time": start_time,
            "end_time": end_time
        }).scalar()
    return result > 0


def update_reservation_in_db(
        student_id: int, 
        room_number: int, 
        start_time: datetime, 
        end_time: datetime,
        modified_start_time: datetime,
        modified_end_time: datetime, 
        companions: List[CompanionData]):
    """
    예약 내용을 수정하는 함수.
    """
    delete_query = text("""
    DELETE FROM Studyroom
    WHERE room_number = :room_number
    AND start_time = :start_time
    AND end_time = :end_time
    """)

    insert_query = text("""
    INSERT INTO Studyroom (room_number, student_id, start_time, end_time, is_leader)
    VALUES (:room_number, :student_id, :start_time, :end_time, :is_leader)
    """)

    with Session(engine) as session:
        # 기존 예약 삭제
        session.execute(delete_query, {
            "room_number": room_number,
            "start_time": start_time,
            "end_time": end_time
        })

        # 대표자 예약 추가
        session.execute(insert_query, {
            "room_number": room_number,
            "student_id": student_id,
            "start_time": modified_start_time,
            "end_time": modified_end_time,
            "is_leader": True
        })

        # 동반자 예약 추가
        for companion in companions:
            session.execute(insert_query, {
                "room_number": room_number,
                "student_id": companion.student_id,
                "start_time": modified_start_time,
                "end_time": modified_end_time,
                "is_leader": False
            })

        # 트랜잭션 커밋
        session.commit()


def delete_reservation_in_db(room_number: int, start_time: datetime, end_time: datetime):
    """
    예약 내용을 취소하는 함수.
    """
    query = text("""
    DELETE FROM Studyroom
    WHERE room_number = :room_number
    AND start_time = :start_time
    AND end_time = :end_time
    """)

    with Session(engine) as session:
        session.execute(query, {
            "room_number": room_number,
            "start_time": start_time,
            "end_time": end_time
        })
        session.commit()

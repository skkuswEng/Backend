from app.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import List

import pandas as pd

from ..schemas.studyroom.request import CompanionData

engine = Database().get_engine()

# 스터디룸 상태 확인
def get_room_time(data: dict):
    query = """
    SELECT time FROM Studyroom
    WHERE room_number = %s
    AND time >= %s
    AND time <= %s
    """

    params = (data["room_number"], data["start_time"], data["end_time"])

    time_df = pd.read_sql(query, engine, params=params)

    # 예약된 time column을 Python datetime 객체로 변환하여 return
    return time_df["time"].tolist()

# 예약 중복 확인
def check_duplicate_time(data: dict):
    check_query = """
    SELECT COUNT(*) AS count
    FROM Studyroom
    WHERE room_number = %s
    AND time >= %s
    AND time < %s
    """

    params = (data["room_number"], data["start_time"], data["end_time"])

    count_df = pd.read_sql(check_query, engine, params=params)
    return count_df['count'].iloc[0]

# 스터디룸 예약
def create_room_reservation(
        room_id: int, 
        start_time: datetime, 
        end_time: datetime, 
        companions: List[CompanionData]
) -> List[datetime]:
    query = """
    INSERT INTO Studyroom (room_number, time, student_id)
    VALUES (:room_id, :time, :student_id)
    """
    reservation_ids = []
    current_time = start_time
    

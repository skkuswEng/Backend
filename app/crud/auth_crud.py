from app.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text

import pandas as pd

from app.utils.functions import hash_password
from datetime import datetime, timedelta
engine = Database().get_engine()

def registerAuthTokenDB( student_id: str, token: str ):
    with Session(engine) as session:
        try:
            # 여러 기기 가능성 고려, 한명이 여러 토큰 가질 수 있음.
            registerToken_query = """
                INSERT INTO FCMToken( student_id, fcm_token) VALUES(
                    :student_id, :token
                );
            """
            session.execute(
                text(registerToken_query),
                {"student_id": student_id, 
                 "token": token }
            )
            session.commit()
            return {
                "result": True,
                "message" : "Token Accepted"
            }
        except Exception as e:
            session.rollback()
            return{
                "result": False,
                "error": f"토큰 등록 중 에러 발생: {str(e)}"
            }

def searchStudentToken( student_id: str ):
    query = """
        SELECT *
        FROM FCMToken
        WHERE student_id = %s
    """
    
    params = (student_id,)
    token_df = pd.
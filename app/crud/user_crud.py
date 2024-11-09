from app.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text

import pandas as pd

engine = Database().get_engine()

# 로그인 관련 정보, DB에서 확인 및 Dataframe 보내기
# 유저가 DB에 없다면 빈 DataFrame을 보낼 것임
def user_login(id: str, password: str):
    query = """
    SELECT * FROM sweng.user
    WHERE id = %s and  password = %s;
    """

    params = (id, password)
    user_df = pd.read_sql(query, engine, params=params)
    return user_df



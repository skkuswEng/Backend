from app.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text

import pandas as pd

engine = Database().get_engine()

# 로그인 관련 정보, DB에서 확인 및 Dataframe 보내기
# 유저가 DB에 없다면 빈 DataFrame을 보낼 것임
def user_login(id: str, password: str):
    query = """
    SELECT * FROM user
    WHERE id = %s and password = %s;
    """

    params = (id, password)
    user_df = pd.read_sql(query, engine, params=params)
    return user_df

# 회원가입
# 이미 회원가입 한 유저인지 확인
def check_duplicate_user(id: str):
    query = """
    SELECT * FROM user
    WHERE id = %s
    """

    params = (id, )
    user_df = pd.read_sql(query, engine, params=params)

    return user_df

# 일단 is_admin은 무조건 False로 박아버리긔 ~
# SHA-256
def user_signup(user_data: dict):
    # 이미 회원가입 되어 있는 유저이면 오류 발생
    # 아이디 Front로 넘겨서 가입되어 있는 아이디 보내주는 것 좋다고 봄(추후 해보자)
    if check_duplicate_user(user_data["student_id"]).empty:
        return False

    try:
        with Session(engine) as session:
            session.execute(
                text(
                    """
                    INSERT INTO user VALUES (:id, :password, :name,
                     :is_admin, :email);
                    """
                ),
                {
                    "id": user_data["student_id"], "password": user_data["password"],
                    "name": user_data["student_name"], "is_admin": False, "email": user_data["email"]
                }
            )

            session.commit()
    except Exception as e:
        print("Error Occurred: ", e)
        session.rollback()
        return False
    return True

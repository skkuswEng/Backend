from app.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text

import pandas as pd

from app.utils.functions import hash_password
engine = Database().get_engine()

# 로그인 관련 정보, DB에서 확인 및 Dataframe 보내기
# 유저가 DB에 없다면 빈 DataFrame을 보낼 것임
def user_login(id: str, password: str):
    query = """
    SELECT * FROM User
    WHERE id = %s and password = %s;
    """

    params = (id, password)
    user_df = pd.read_sql(query, engine, params=params)
    return user_df

# 회원가입
# 이미 회원가입 한 유저인지 확인
def check_duplicate_user(id: str):
    query = """
    SELECT * FROM User
    WHERE id = %s
    """

    params = (id, )
    user_df = pd.read_sql(query, engine, params=params)

    return user_df

# 일단 is_admin은 무조건 False로 박아버리긔 ~
def user_signup(user_data: dict):
    # 이미 회원가입 되어 있는 유저이면 오류 발생
    # 아이디 Front로 넘겨서 가입되어 있는 아이디 보내주는 것 좋다고 봄(추후 해보자)
    if check_duplicate_user(user_data["student_id"]).empty:
        return {
            "result": False,
            "error": "이미 회원가입 되어있는 학번입니다"
        }
    
    # 비밀번호 해시화
    # 추후 시간 있을 시 salt도 추가해서 보안성 더욱 올리기
    hashed_password = hash_password(user_data["password"])

    try:
        with Session(engine) as session:
            session.execute(
                text(
                    """
                    INSERT INTO User VALUES (:id, :password, :name,
                     :is_admin, :email);
                    """
                ),
                {
                    "id": user_data["student_id"], "password": hashed_password,
                    "name": user_data["student_name"], "is_admin": False, "email": user_data["email"]
                }
            )

            session.commit()
    except Exception as e:
        print("Error Occurred: ", e)
        session.rollback()
        return {
            "result": False,
            "error": str(e)
        }
    return {
        "result": True,
        "error": None
    }

# 회원탈퇴
def user_unregister(user_data: dict):
    # 학번으로 사용자 조회
    query_user_exists = """
    SELECT * FROM User
    Where student_id = %s;
    """

    params = (user_data["student_id"], )
    user_df = pd.read_sql(query_user_exists, engine, params=params)

    if user_df.empty:
        # 학번으로 조회된 유저가 없음
        return {
            "result": False,
            "error": "없는 유저입니다"
        }

    # 학번과 비밀번호로 사용자 조회
    query_password_match = """
    SELECT * FROM User
    WHERE student_id = %s AND password = %s;
    """
    params_password_match = (user_data["student_id"], user_data["password"])
    user_df_password = pd.read_sql(query_password_match, engine, params=params_password_match)

    if user_df_password.empty:
        # 비밀번호가 틀림
        return {
            "result": False,
            "error": "비밀번호가 틀립니다."
        }
    
    # 사용자 삭제
    with Session(engine) as session:
        try:
            delete_query = """
            DELETE FROM User WHERE student_id = :student_id;
            """
            session.execute(
                text(delete_query),
                {"student_id": user_data["student_id"]}
            )
            session.commit()
        except Exception as e:
            session.rollback()  # 롤백하여 트랜잭션 취소
            return {
                "result": False,
                "error": f"회원탈퇴 중 에러 발생: {str(e)}"
            }

        return {
            "result": True,
            "message": "회원탈퇴 성공"
        }

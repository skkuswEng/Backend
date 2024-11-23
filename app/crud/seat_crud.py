from app.database import Database
from sqlalchemy.orm import Session
from sqlalchemy import text

import pandas as pd

from app.utils.functions import hash_password
engine = Database().get_engine()

def getSeatData():
    query = """
        SELET *
        FROM Seat;
    """
    seat_df = pd.read_sql(query, enginge )
    return seat_df

def getSelectedSeatData(seat_number: int ):
    query = """
        SELET * 
        FROM Seat
        WHERE seat_number = %d;
    """
    params = (seat_number)
    seat_df = pd.read_sql( query, engine, params=params )

    return seat_df
    
    
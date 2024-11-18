from pydantic import BaseModel

class ResponseModel(BaseModel):
    class Config:
        orm_mode=True

class RequestModel(BaseModel):
    class Config:
        orm_mode=True
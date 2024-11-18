from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# Custom exceptions
class UserError(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)
    pass

# Exception handlers
async def exception_handler(request: Request, exc: UserError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail or "이건 예상 못한 에러인데...?"},
    )

# Register all handlers in a single function
def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(UserError, exception_handler)

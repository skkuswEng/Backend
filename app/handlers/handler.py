from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# Custom exceptions
class LoginError(HTTPException):
    pass

# Exception handlers
async def login_exception_handler(request: Request, exc: LoginError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )

# Register all handlers in a single function
def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(LoginError, login_exception_handler)

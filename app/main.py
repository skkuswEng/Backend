from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles

from .secure.cors import setup_cors 

from .handlers.handler import register_exception_handlers

from .routers.user_router import router as user_router
from .routers.studyroom_router import router as studyroom_router
from .routers.seat_router import router as seat_router 
from .routers.auth_router import router as auth_router
app = FastAPI()

# CORS 설정
setup_cors(app)

# Favicon Static
# Get rid of favicon.ico 404 Not Found error
app.mount("/static", StaticFiles(directory="static"), name="static")

# handlers
register_exception_handlers(app)

# routers
app.include_router(user_router)
app.include_router(studyroom_router)
app.include_router(seat_router)
app.include_router(auth_router)


# root router for testing
@app.get('/')
async def home(request: Request):
    domain = request.headers.get("host")
    return {"message": f"Hello from {domain}"}

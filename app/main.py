from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles

from .handlers.handler import register_exception_handlers

from .routers.user_router import router as user_router

app = FastAPI()

# Favicon Static
# Get rid of favicon.ico 404 Not Found error
app.mount("/static", StaticFiles(directory="static"), name="static")

# handlers
register_exception_handlers(app)

# routers
app.include_router(user_router)

# root router for testing
@app.get('/')
async def home(request: Request):
    domain = request.headers.get("host")
    return {"message": f"Hello from {domain}"}

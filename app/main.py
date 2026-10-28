#Точка входа приложения FastAPI.

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import db
from app.models import User
from app.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):    
    """Управляет подключением к БД при запуске и остановке приложения."""
    db.connect(reuse_if_open=True)
    db.create_tables([User], safe=True)

    yield

    if not db.is_closed():
        db.close()

app = FastAPI(
    title="Auth API",
    description="API for user authentication and management",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)

@app.get("/")
def root():
    """Возвращает сообщение, подтверждающее работу API."""
    return {"message": "Auth API is running"}

import logging
import sys
from fastapi import FastAPI
from app.routers import items
from app.config import Settings

settings = Settings()
app = FastAPI(
    title=settings.app_name,
    description="Лабораторная работа по FastAPI",
    version="1.0.0",
    contact={
        "name": "Студент",
        "email": settings.admin_email,
    }
)
app.include_router(items.router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)
logger = logging.getLogger(__name__)


@app.get("/")
def read_root():
    logger.info("Обращение к корневому каталогу (/)")
    return {"message": "Hello, FastAPI!"}


@app.get("/info")
def get_info():
    logger.info("Запрос конфигурации приложения (/info)")
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_page": settings.items_per_page
    }

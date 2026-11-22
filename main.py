import logging
from fastapi import FastAPI
from app.routers import items
from app.config import Settings

# Настройка логирования с выводом в файл и консоль
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.FileHandler("logs.log", encoding="utf-8"), logging.StreamHandler()],
    force=True
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации приложения из .env
settings = Settings()

# Создание экземпляра приложения и подключение роутера
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


# Обработка корневого GET-запроса
@app.get("/")
def read_root():
    logger.info("Обращение к корневому каталогу (/)")
    return {"message": "Hello, FastAPI!"}


# Возврат текущих настроек приложения
@app.get("/info")
def get_info():
    logger.info("Запрос конфигурации приложения (/info)")
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_page": settings.items_per_page
    }

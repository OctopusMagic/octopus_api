from fastapi import FastAPI
from loguru import logger

from app.config import openapi_config
from app.initializer import init


app = FastAPI(
    title=openapi_config.name,
    description=openapi_config.description,
    version=openapi_config.version,
)

logger.info("Initializing app")
init(app)
logger.info("App initialized")

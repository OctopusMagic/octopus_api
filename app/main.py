from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import openapi_config
from app.initializer import init


logger.add("octopus_api.log", rotation="00:00")

app = FastAPI(
    title=openapi_config.name,
    description=openapi_config.description,
    version=openapi_config.version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://dashboard.octopus.local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Initializing app")
init(app)
logger.info("App initialized")

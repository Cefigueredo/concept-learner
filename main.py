import logging

import fastapi
from fastapi import status
from fastapi.middleware import cors

from api.api_v1 import api_routers
from core import config

logger = logging.getLogger()
logger.setLevel(logging.INFO)


app = fastapi.FastAPI()

logger.warning(f"{config.settings.CORS_ORIGIN=}")

app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=config.settings.CORS_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_description="Health check",
)
def get_health_check() -> dict:
    """
    Checks the health of the API.

    Returns:
        A helth check message.
    """
    return {"message": "OK"}


app_v1 = fastapi.FastAPI(
    title=config.settings.PROJECT_NAME,
    version=config.settings.PROJECT_VERSION,
    description=config.settings.PROJECT_DESCRIPTION,
    contact=config.settings.PROJECT_CONTACT,
)

app_v1.include_router(api_routers.api_router)

app.mount("/v1", app_v1)

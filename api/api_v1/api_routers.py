from fastapi import APIRouter

from api.api_v1.routers import concept

api_router = APIRouter()

api_router.include_router(concept.router)

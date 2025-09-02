from fastapi import APIRouter

from app.api.api_v1.endpoints import cryptocurrencies

api_router = APIRouter()

api_router.include_router(
    cryptocurrencies.router, 
    prefix="/cryptocurrencies", 
    tags=["cryptocurrencies"]
)
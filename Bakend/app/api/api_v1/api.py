from fastapi import APIRouter

from app.api.api_v1.endpoints import cryptocurrencies, auth, users, risk, trading, market, advanced_trading

api_router = APIRouter()

api_router.include_router(
    cryptocurrencies.router, prefix="/cryptocurrencies", tags=["cryptocurrencies"]
)

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

api_router.include_router(users.router, prefix="/users", tags=["users"])

api_router.include_router(risk.router, prefix="/risk", tags=["risk-assessment"])

api_router.include_router(trading.router, prefix="/trading", tags=["trading"])

api_router.include_router(market.router, prefix="/market", tags=["market-data"])

api_router.include_router(advanced_trading.router, prefix="/advanced", tags=["advanced-trading"])

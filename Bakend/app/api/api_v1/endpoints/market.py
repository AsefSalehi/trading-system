from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, require_role
from app.db.database import get_sync_db
from app.models.user import User, UserRole
from app.services.market_data_service import market_data_service
from app.services.binance_service import binance_service


router = APIRouter()


@router.get("/overview")
def get_market_overview(
    *,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get comprehensive market overview with real-time data"""
    try:
        overview = market_data_service.get_market_overview(db)
        return overview
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market overview: {str(e)}"
        )


@router.get("/price/{symbol}")
def get_real_time_price(
    *,
    symbol: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get real-time price for a cryptocurrency"""
    try:
        price = market_data_service.get_real_time_price(symbol.upper())
        if price is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Price not found for {symbol}"
            )
        
        return {
            "symbol": symbol.upper(),
            "price": float(price),
            "source": "Binance API",
            "timestamp": market_data_service.binance_service.last_update.get(
                binance_service.get_symbol_from_crypto(symbol.upper())
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get price for {symbol}: {str(e)}"
        )


@router.get("/prices")
def get_multiple_prices(
    *,
    symbols: str = Query(..., description="Comma-separated list of symbols (e.g., BTC,ETH,ADA)"),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get real-time prices for multiple cryptocurrencies"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        prices = market_data_service.get_real_time_prices(symbol_list)
        
        result = []
        for symbol in symbol_list:
            price = prices.get(symbol)
            if price is not None:
                result.append({
                    "symbol": symbol,
                    "price": float(price),
                    "source": "Binance API"
                })
        
        return {
            "prices": result,
            "total_symbols": len(result),
            "requested_symbols": len(symbol_list),
            "timestamp": market_data_service.binance_service.last_update
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get prices: {str(e)}"
        )


@router.get("/ticker/{symbol}")
def get_24h_ticker(
    *,
    symbol: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get 24h ticker statistics for a cryptocurrency"""
    try:
        ticker = market_data_service.get_24h_ticker(symbol.upper())
        if ticker is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticker not found for {symbol}"
            )
        
        return {
            "symbol": ticker['symbol'],
            "price": float(ticker['price']),
            "price_change": float(ticker['price_change']),
            "price_change_percent": float(ticker['price_change_percent']),
            "high_price": float(ticker['high_price']),
            "low_price": float(ticker['low_price']),
            "volume": float(ticker['volume']),
            "quote_volume": float(ticker['quote_volume']),
            "open_price": float(ticker['open_price']),
            "prev_close_price": float(ticker['prev_close_price']),
            "count": ticker['count'],
            "last_update": ticker['last_update'],
            "source": "Binance API"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ticker for {symbol}: {str(e)}"
        )


@router.get("/historical/{symbol}")
def get_historical_data(
    *,
    symbol: str,
    interval: str = Query("1h", description="Kline interval (1m, 5m, 1h, 1d, etc.)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of data points"),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get historical price data for a cryptocurrency"""
    try:
        historical_data = market_data_service.get_historical_data(
            symbol.upper(), interval, limit
        )
        
        if not historical_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Historical data not found for {symbol}"
            )
        
        # Convert to JSON-serializable format
        result = []
        for data_point in historical_data:
            result.append({
                "timestamp": data_point['timestamp'].isoformat(),
                "open": float(data_point['open']),
                "high": float(data_point['high']),
                "low": float(data_point['low']),
                "close": float(data_point['close']),
                "volume": float(data_point['volume']),
                "quote_volume": float(data_point['quote_volume'])
            })
        
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "data": result,
            "count": len(result),
            "source": "Binance API"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get historical data for {symbol}: {str(e)}"
        )


@router.post("/sync")
def sync_market_data(
    *,
    db: Session = Depends(get_sync_db),
    symbols: Optional[str] = Query(None, description="Comma-separated symbols to sync (optional)"),
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> Any:
    """Sync market data from Binance (Admin only)"""
    try:
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        result = market_data_service.sync_cryptocurrency_data(db, symbol_list)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync market data: {str(e)}"
        )


@router.get("/status")
def get_market_status(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get market and API connection status"""
    try:
        status_info = market_data_service.test_binance_connection()
        return status_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market status: {str(e)}"
        )


@router.post("/start-realtime")
def start_real_time_updates(
    *,
    symbols: Optional[str] = Query(None, description="Comma-separated symbols for real-time updates"),
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> Any:
    """Start real-time price updates via WebSocket (Admin only)"""
    try:
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        market_data_service.start_real_time_updates(symbol_list)
        
        return {
            "status": "success",
            "message": "Real-time updates started",
            "symbols": symbol_list or market_data_service.supported_symbols
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start real-time updates: {str(e)}"
        )


@router.post("/stop-realtime")
def stop_real_time_updates(
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> Any:
    """Stop real-time price updates (Admin only)"""
    try:
        market_data_service.stop_real_time_updates()
        
        return {
            "status": "success",
            "message": "Real-time updates stopped"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop real-time updates: {str(e)}"
        )


@router.get("/top")
def get_top_cryptocurrencies(
    *,
    limit: int = Query(20, ge=1, le=100, description="Number of top cryptocurrencies"),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get top cryptocurrencies by volume from Binance"""
    try:
        top_cryptos = binance_service.get_top_cryptocurrencies(limit)
        
        # Convert to JSON-serializable format
        result = []
        for crypto in top_cryptos:
            result.append({
                "symbol": crypto['symbol'],
                "name": crypto['name'],
                "price": float(crypto['price']),
                "price_change_24h": float(crypto['price_change_24h']),
                "price_change_percentage_24h": float(crypto['price_change_percentage_24h']),
                "volume_24h": float(crypto['volume_24h']),
                "quote_volume_24h": float(crypto['quote_volume_24h']),
                "high_24h": float(crypto['high_24h']),
                "low_24h": float(crypto['low_24h']),
                "market_cap_rank": crypto['market_cap_rank'],
                "last_updated": crypto['last_updated'].isoformat()
            })
        
        return {
            "cryptocurrencies": result,
            "count": len(result),
            "source": "Binance API",
            "last_updated": result[0]['last_updated'] if result else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top cryptocurrencies: {str(e)}"
        )
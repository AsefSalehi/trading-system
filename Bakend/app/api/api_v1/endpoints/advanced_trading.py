"""
Advanced Trading Endpoints
API endpoints for all advanced trading features
"""

from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from decimal import Decimal
import json
import asyncio

from app.core.auth import get_current_active_user, require_role
from app.db.database import get_sync_db
from app.models.user import User, UserRole
from app.models.wallet import OrderType, OrderStatus, TransactionType
from app.services.order_execution_service import order_execution_service
from app.services.risk_management_service import risk_management_service
from app.services.realtime_service import realtime_service
from app.services.multi_exchange_service import multi_exchange_service
from app.schemas.trading import OrderRequest, OrderResponse, RiskMetricsResponse, ArbitrageResponse
from app.core.logging import logger


router = APIRouter()


# ============================================================================
# ADVANCED ORDER TYPES
# ============================================================================

@router.post("/orders/limit", response_model=OrderResponse)
def place_limit_order(
    *,
    db: Session = Depends(get_sync_db),
    order_request: OrderRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Place a limit order"""
    try:
        # Get user's wallet
        from app.services.trading_service import trading_service
        wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found. Create a wallet first."
            )

        # Validate trade with risk management
        is_valid, message = risk_management_service.validate_trade(
            db=db,
            wallet_id=wallet.id,
            symbol=order_request.symbol.upper(),
            transaction_type=TransactionType(order_request.side.lower()),
            amount=Decimal(str(order_request.amount))
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Risk management check failed: {message}"
            )

        # Place limit order
        order = order_execution_service.place_limit_order(
            db=db,
            wallet_id=wallet.id,
            symbol=order_request.symbol.upper(),
            transaction_type=TransactionType(order_request.side.lower()),
            quantity=Decimal(str(order_request.quantity)),
            limit_price=Decimal(str(order_request.price))
        )

        return {
            "order_id": order.id,
            "status": order.status.value,
            "order_type": order.order_type.value,
            "symbol": order.symbol,
            "side": order.transaction_type.value,
            "quantity": float(order.quantity),
            "price": float(order.price),
            "created_at": order.created_at.isoformat()
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place limit order: {str(e)}"
        )


@router.post("/orders/stop-loss", response_model=OrderResponse)
def place_stop_loss_order(
    *,
    db: Session = Depends(get_sync_db),
    symbol: str,
    quantity: float,
    stop_price: float,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Place a stop-loss order"""
    try:
        from app.services.trading_service import trading_service
        wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found. Create a wallet first."
            )

        order = order_execution_service.place_stop_loss_order(
            db=db,
            wallet_id=wallet.id,
            symbol=symbol.upper(),
            quantity=Decimal(str(quantity)),
            stop_price=Decimal(str(stop_price))
        )

        return {
            "order_id": order.id,
            "status": order.status.value,
            "order_type": order.order_type.value,
            "symbol": order.symbol,
            "side": order.transaction_type.value,
            "quantity": float(order.quantity),
            "stop_price": float(order.stop_price),
            "created_at": order.created_at.isoformat()
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place stop-loss order: {str(e)}"
        )


@router.post("/orders/take-profit", response_model=OrderResponse)
def place_take_profit_order(
    *,
    db: Session = Depends(get_sync_db),
    symbol: str,
    quantity: float,
    target_price: float,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Place a take-profit order"""
    try:
        from app.services.trading_service import trading_service
        wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found. Create a wallet first."
            )

        order = order_execution_service.place_take_profit_order(
            db=db,
            wallet_id=wallet.id,
            symbol=symbol.upper(),
            quantity=Decimal(str(quantity)),
            target_price=Decimal(str(target_price))
        )

        return {
            "order_id": order.id,
            "status": order.status.value,
            "order_type": order.order_type.value,
            "symbol": order.symbol,
            "side": order.transaction_type.value,
            "quantity": float(order.quantity),
            "target_price": float(order.trigger_price),
            "created_at": order.created_at.isoformat()
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place take-profit order: {str(e)}"
        )


@router.get("/orders", response_model=List[OrderResponse])
def get_orders(
    *,
    db: Session = Depends(get_sync_db),
    status_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get user's orders"""
    try:
        status_enum = OrderStatus(status_filter) if status_filter else None
        orders = order_execution_service.get_user_orders(db, current_user.id, status_enum)

        return [
            {
                "order_id": order.id,
                "status": order.status.value,
                "order_type": order.order_type.value,
                "symbol": order.symbol,
                "side": order.transaction_type.value,
                "quantity": float(order.quantity),
                "price": float(order.price) if order.price else None,
                "stop_price": float(order.stop_price) if order.stop_price else None,
                "executed_price": float(order.executed_price) if order.executed_price else None,
                "created_at": order.created_at.isoformat(),
                "executed_at": order.executed_at.isoformat() if order.executed_at else None
            }
            for order in orders
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get orders: {str(e)}"
        )


@router.delete("/orders/{order_id}")
def cancel_order(
    *,
    db: Session = Depends(get_sync_db),
    order_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Cancel a pending order"""
    try:
        success = order_execution_service.cancel_order(db, order_id, current_user.id)

        if success:
            return {"message": "Order cancelled successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or cannot be cancelled"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel order: {str(e)}"
        )


# ============================================================================
# RISK MANAGEMENT
# ============================================================================

@router.get("/risk/metrics", response_model=RiskMetricsResponse)
def get_risk_metrics(
    *,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get comprehensive risk metrics"""
    try:
        from app.services.trading_service import trading_service
        wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found. Create a wallet first."
            )

        metrics = risk_management_service.calculate_risk_metrics(db, wallet.id)
        recommendations = risk_management_service.get_risk_recommendations(db, wallet.id)

        return {
            "total_portfolio_value": float(metrics.total_portfolio_value),
            "cash_percentage": float(metrics.cash_percentage),
            "largest_position_percentage": float(metrics.largest_position_percentage),
            "daily_pnl_percentage": float(metrics.daily_pnl_percentage),
            "total_pnl_percentage": float(metrics.total_pnl_percentage),
            "concentration_risk_score": float(metrics.concentration_risk_score),
            "overall_risk_score": float(metrics.risk_score),
            "recommendations": recommendations
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk metrics: {str(e)}"
        )


@router.get("/risk/emergency-check")
def emergency_risk_check(
    *,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Perform emergency risk check"""
    try:
        from app.services.trading_service import trading_service
        wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found. Create a wallet first."
            )

        emergency_status = risk_management_service.emergency_risk_check(db, wallet.id)

        return emergency_status

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform emergency risk check: {str(e)}"
        )


# ============================================================================
# MULTI-EXCHANGE & ARBITRAGE
# ============================================================================

@router.get("/exchanges/prices/{symbol}")
async def get_exchange_prices(symbol: str) -> Any:
    """Get prices from all exchanges for a symbol"""
    try:
        prices = multi_exchange_service.get_exchange_prices(symbol.upper())

        return {
            "symbol": symbol.upper(),
            "prices": {exchange: price.to_dict() for exchange, price in prices.items()},
            "count": len(prices)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get exchange prices: {str(e)}"
        )


@router.get("/exchanges/best-price/{symbol}")
async def get_best_price(symbol: str, side: str = Query(..., regex="^(buy|sell)$")) -> Any:
    """Get best price across all exchanges"""
    try:
        best_price = await multi_exchange_service.get_best_price(symbol.upper(), side)

        if best_price:
            return {
                "symbol": symbol.upper(),
                "side": side,
                "best_exchange": best_price[0],
                "best_price": float(best_price[1])
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No price data available for {symbol}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get best price: {str(e)}"
        )


@router.get("/arbitrage/opportunities", response_model=List[ArbitrageResponse])
def get_arbitrage_opportunities(
    min_profit: Optional[float] = Query(None, description="Minimum profit percentage")
) -> Any:
    """Get current arbitrage opportunities"""
    try:
        min_profit_decimal = Decimal(str(min_profit)) if min_profit else None
        opportunities = multi_exchange_service.get_arbitrage_opportunities(min_profit_decimal)

        return [
            {
                "symbol": opp.symbol,
                "buy_exchange": opp.buy_exchange,
                "sell_exchange": opp.sell_exchange,
                "buy_price": float(opp.buy_price),
                "sell_price": float(opp.sell_price),
                "profit_percentage": float(opp.profit_percentage),
                "profit_amount": float(opp.profit_amount),
                "max_volume": float(opp.max_volume),
                "timestamp": opp.timestamp.isoformat()
            }
            for opp in opportunities
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get arbitrage opportunities: {str(e)}"
        )


@router.get("/exchanges/order-books/{symbol}")
async def get_order_books(symbol: str) -> Any:
    """Get order books from all exchanges"""
    try:
        order_books = await multi_exchange_service.get_order_books(symbol.upper())

        return {
            "symbol": symbol.upper(),
            "order_books": order_books
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get order books: {str(e)}"
        )


@router.get("/exchanges/market-summary")
def get_market_summary() -> Any:
    """Get market summary across all exchanges"""
    try:
        summary = multi_exchange_service.get_market_summary()
        return summary

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market summary: {str(e)}"
        )


# ============================================================================
# REAL-TIME FEATURES
# ============================================================================

@router.websocket("/ws/prices")
async def websocket_price_feed(websocket: WebSocket, symbols: str, user_id: int):
    """WebSocket endpoint for real-time price feeds"""
    await websocket.accept()

    try:
        symbol_list = symbols.upper().split(",")
        await realtime_service.subscribe_to_price_feed(websocket, user_id, symbol_list)

        # Keep connection alive
        while True:
            try:
                # Wait for client messages (ping/pong, etc.)
                await websocket.receive_text()
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await realtime_service.websocket_manager.disconnect(websocket, user_id)


@router.websocket("/ws/orderbook")
async def websocket_order_book(websocket: WebSocket, symbols: str, user_id: int):
    """WebSocket endpoint for real-time order book feeds"""
    await websocket.accept()

    try:
        symbol_list = symbols.upper().split(",")
        await realtime_service.subscribe_to_order_book(websocket, user_id, symbol_list)

        # Keep connection alive
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await realtime_service.websocket_manager.disconnect(websocket, user_id)


@router.post("/alerts/price")
def create_price_alert(
    *,
    symbol: str,
    condition: str = Query(..., regex="^(above|below)$"),
    threshold: float,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create a price alert"""
    try:
        alert_id = realtime_service.create_price_alert(
            user_id=current_user.id,
            symbol=symbol.upper(),
            condition=condition,
            threshold=Decimal(str(threshold))
        )

        return {
            "alert_id": alert_id,
            "message": f"Price alert created for {symbol} {condition} ${threshold}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create price alert: {str(e)}"
        )


@router.get("/orderbook/{symbol}")
def get_live_order_book(symbol: str) -> Any:
    """Get live order book for symbol"""
    try:
        order_book = realtime_service.get_order_book(symbol.upper())

        if order_book:
            return order_book
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order book not available for {symbol}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get order book: {str(e)}"
        )


@router.get("/price-history/{symbol}")
def get_price_history(
    symbol: str,
    limit: int = Query(100, ge=1, le=1000)
) -> Any:
    """Get price history for symbol"""
    try:
        history = realtime_service.get_price_history(symbol.upper(), limit)

        return {
            "symbol": symbol.upper(),
            "history": history,
            "count": len(history)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get price history: {str(e)}"
        )


# ============================================================================
# SYSTEM CONTROL
# ============================================================================

@router.post("/system/start-advanced-features")
async def start_advanced_features(
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> Any:
    """Start all advanced trading features (Admin only)"""
    try:
        # Start order execution monitoring
        asyncio.create_task(order_execution_service.start_order_monitoring())

        # Start real-time services
        await realtime_service.start()

        # Start multi-exchange monitoring
        await multi_exchange_service.start_monitoring()

        return {
            "message": "Advanced trading features started successfully",
            "features": [
                "Order execution monitoring",
                "Real-time price feeds",
                "Multi-exchange monitoring",
                "Arbitrage detection"
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start advanced features: {str(e)}"
        )


@router.post("/system/stop-advanced-features")
def stop_advanced_features(
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> Any:
    """Stop all advanced trading features (Admin only)"""
    try:
        order_execution_service.stop_order_monitoring()
        realtime_service.stop()
        multi_exchange_service.stop_monitoring()

        return {"message": "Advanced trading features stopped successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop advanced features: {str(e)}"
        )

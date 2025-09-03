from datetime import datetime, timedelta
from typing import List, Optional
from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.logging import logger
from app.db.database import SessionLocal
from app.services.trading_service import trading_service
from app.services.market_data_service import market_data_service
from app.models.wallet import Wallet
from app.models.cryptocurrency import Cryptocurrency
import random


@celery_app.task(bind=True, name="app.tasks.trading_tasks.sync_real_market_prices")
def sync_real_market_prices(self) -> dict:
    """
    Background task to sync real market prices from Binance
    """
    try:
        logger.info("Starting market price simulation task")

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Simulating market movements", "progress": 10}
            )

        import asyncio
        result = asyncio.run(_simulate_market_prices_async())

        logger.info(f"Market price simulation completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in simulate_market_prices task: {e}")
        if current_task:
            current_task.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise


async def _simulate_market_prices_async() -> dict:
    """Async helper function for real market price sync from Binance"""
    try:
        db = SessionLocal()

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Syncing real market data from Binance", "progress": 30}
            )

        # Sync real market data from Binance
        sync_result = market_data_service.sync_cryptocurrency_data(db)

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Updating portfolio values with real prices", "progress": 70}
            )

        # Update all portfolio values with real prices
        portfolio_result = trading_service.simulate_market_movement(db)

        db.close()

        return {
            "status": "success",
            "binance_sync": sync_result,
            "portfolio_updates": portfolio_result,
            "data_source": "Binance API",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        if 'db' in locals():
            db.close()
        raise e


@celery_app.task(bind=True, name="app.tasks.trading_tasks.update_portfolio_values")
def update_portfolio_values(self) -> dict:
    """
    Background task to update all portfolio values
    """
    try:
        logger.info("Starting portfolio values update task")

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Updating portfolio values", "progress": 50}
            )

        import asyncio
        result = asyncio.run(_update_portfolio_values_async())

        logger.info(f"Portfolio values update completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in update_portfolio_values task: {e}")
        if current_task:
            current_task.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise


async def _update_portfolio_values_async() -> dict:
    """Async helper function for portfolio values update"""
    try:
        db = SessionLocal()

        result = trading_service.simulate_market_movement(db)

        db.close()

        return result

    except Exception as e:
        if 'db' in locals():
            db.close()
        raise e


@celery_app.task(bind=True, name="app.tasks.trading_tasks.generate_trading_signals")
def generate_trading_signals(self) -> dict:
    """
    Background task to generate automated trading signals
    """
    try:
        logger.info("Starting trading signals generation task")

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Analyzing market conditions", "progress": 30}
            )

        import asyncio
        result = asyncio.run(_generate_trading_signals_async())

        logger.info(f"Trading signals generation completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in generate_trading_signals task: {e}")
        if current_task:
            current_task.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise


async def _generate_trading_signals_async() -> dict:
    """Async helper function for trading signals generation"""
    try:
        db = SessionLocal()

        # Get cryptocurrencies with recent price data
        cryptos = db.query(Cryptocurrency).filter(
            Cryptocurrency.is_active == True,
            Cryptocurrency.current_price.isnot(None)
        ).limit(20).all()

        signals = []

        for crypto in cryptos:
            # Simple signal generation based on price change
            price_change = float(crypto.price_change_percentage_24h or 0)

            signal = None
            confidence = 0

            if price_change < -5:  # Strong downward movement
                signal = "BUY"  # Buy the dip
                confidence = min(abs(price_change) * 10, 100)
            elif price_change > 5:  # Strong upward movement
                signal = "SELL"  # Take profits
                confidence = min(price_change * 10, 100)

            if signal:
                signals.append({
                    "symbol": crypto.symbol,
                    "signal": signal,
                    "confidence": confidence,
                    "current_price": float(crypto.current_price),
                    "price_change_24h": price_change,
                    "reason": f"Price {'dropped' if signal == 'BUY' else 'increased'} by {abs(price_change):.2f}%"
                })

        db.close()

        return {
            "status": "success",
            "signals_generated": len(signals),
            "signals": signals,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        if 'db' in locals():
            db.close()
        raise e


@celery_app.task(bind=True, name="app.tasks.trading_tasks.calculate_portfolio_metrics")
def calculate_portfolio_metrics(self) -> dict:
    """
    Background task to calculate advanced portfolio metrics
    """
    try:
        logger.info("Starting portfolio metrics calculation task")

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Calculating portfolio metrics", "progress": 50}
            )

        import asyncio
        result = asyncio.run(_calculate_portfolio_metrics_async())

        logger.info(f"Portfolio metrics calculation completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in calculate_portfolio_metrics task: {e}")
        if current_task:
            current_task.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise


async def _calculate_portfolio_metrics_async() -> dict:
    """Async helper function for portfolio metrics calculation"""
    try:
        db = SessionLocal()

        # Get all active wallets
        wallets = db.query(Wallet).filter(Wallet.is_active == True).all()

        metrics_summary = {
            "total_wallets": len(wallets),
            "total_portfolio_value": 0,
            "total_pnl": 0,
            "profitable_wallets": 0,
            "losing_wallets": 0,
            "average_win_rate": 0,
            "total_trades": 0
        }

        total_win_rate = 0

        for wallet in wallets:
            # Update portfolio values
            portfolio_data = trading_service.update_portfolio_values(db, wallet.id)

            metrics_summary["total_portfolio_value"] += portfolio_data["total_portfolio_value"]
            metrics_summary["total_pnl"] += portfolio_data["total_pnl"]
            metrics_summary["total_trades"] += wallet.total_trades

            if portfolio_data["total_pnl"] > 0:
                metrics_summary["profitable_wallets"] += 1
            else:
                metrics_summary["losing_wallets"] += 1

            total_win_rate += wallet.win_rate

        if len(wallets) > 0:
            metrics_summary["average_win_rate"] = total_win_rate / len(wallets)

        db.close()

        return {
            "status": "success",
            "metrics": metrics_summary,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        if 'db' in locals():
            db.close()
        raise e

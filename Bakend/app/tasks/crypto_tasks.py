from datetime import datetime, timedelta
from typing import Optional
from celery import current_task
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.logging import logger
from app.db.database import AsyncSessionLocal
from app.services.cryptocurrency_service import cryptocurrency_service
from app.models.cryptocurrency import PriceHistory
from app.core.cache import invalidate_cache_pattern


@celery_app.task(bind=True, name="app.tasks.crypto_tasks.sync_cryptocurrency_data")
def sync_cryptocurrency_data(
    self, 
    limit: int = 100, 
    provider: str = "coingecko"
) -> dict:
    """
    Background task to sync cryptocurrency data from external APIs
    
    Args:
        limit: Number of cryptocurrencies to fetch
        provider: Data provider to use ("coingecko" or "coinmarketcap")
    
    Returns:
        Dict with task results
    """
    try:
        logger.info(f"Starting crypto data sync task - Limit: {limit}, Provider: {provider}")
        
        # Update task state
        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Fetching data from external API", "progress": 10}
            )
        
        # Run the async function in sync context
        import asyncio
        result = asyncio.run(_sync_crypto_data_async(limit, provider))
        
        # Invalidate cache after successful sync
        asyncio.run(invalidate_cache_pattern("crypto_listings:*"))
        
        logger.info(f"Crypto data sync completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in sync_cryptocurrency_data task: {e}")
        if current_task:
            current_task.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise


async def _sync_crypto_data_async(limit: int, provider: str) -> dict:
    """Async helper function for crypto data sync"""
    async with AsyncSessionLocal() as db:
        try:
            cryptocurrencies = await cryptocurrency_service.fetch_and_store_listings(
                db=db,
                limit=limit,
                provider=provider
            )
            
            return {
                "status": "success",
                "processed_count": len(cryptocurrencies),
                "provider": provider,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await db.rollback()
            raise e


@celery_app.task(bind=True, name="app.tasks.crypto_tasks.sync_single_cryptocurrency")
def sync_single_cryptocurrency(self, symbol: str, provider: str = "coingecko") -> dict:
    """
    Background task to sync a single cryptocurrency
    
    Args:
        symbol: Cryptocurrency symbol to sync
        provider: Data provider to use
    
    Returns:
        Dict with task results
    """
    try:
        logger.info(f"Starting single crypto sync task for {symbol}")
        
        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": f"Fetching data for {symbol}", "progress": 50}
            )
        
        import asyncio
        result = asyncio.run(_sync_single_crypto_async(symbol, provider))
        
        # Invalidate specific cache
        asyncio.run(invalidate_cache_pattern(f"crypto_listings:*{symbol}*"))
        
        logger.info(f"Single crypto sync completed for {symbol}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in sync_single_cryptocurrency task for {symbol}: {e}")
        if current_task:
            current_task.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise


async def _sync_single_crypto_async(symbol: str, provider: str) -> dict:
    """Async helper function for single crypto sync"""
    async with AsyncSessionLocal() as db:
        try:
            # Get existing crypto or create new one
            crypto = await cryptocurrency_service.get_cryptocurrency_by_symbol(db, symbol)
            
            if not crypto:
                return {
                    "status": "not_found",
                    "symbol": symbol,
                    "message": f"Cryptocurrency {symbol} not found",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # For now, we'll need to implement individual crypto fetching
            # This is a simplified version
            return {
                "status": "success",
                "symbol": symbol,
                "provider": provider,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await db.rollback()
            raise e


@celery_app.task(bind=True, name="app.tasks.crypto_tasks.cleanup_old_price_history")
def cleanup_old_price_history(self, days_to_keep: int = 365) -> dict:
    """
    Background task to cleanup old price history records
    
    Args:
        days_to_keep: Number of days of history to keep
    
    Returns:
        Dict with cleanup results
    """
    try:
        logger.info(f"Starting price history cleanup task - keeping {days_to_keep} days")
        
        if current_task:
            current_task.update_state(
                state="PROGRESS", 
                meta={"status": "Cleaning up old price history", "progress": 50}
            )
        
        import asyncio
        result = asyncio.run(_cleanup_price_history_async(days_to_keep))
        
        logger.info(f"Price history cleanup completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_price_history task: {e}")
        if current_task:
            current_task.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise


async def _cleanup_price_history_async(days_to_keep: int) -> dict:
    """Async helper function for price history cleanup"""
    async with AsyncSessionLocal() as db:
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old price history records
            stmt = delete(PriceHistory).where(PriceHistory.timestamp < cutoff_date)
            result = await db.execute(stmt)
            
            deleted_count = result.rowcount
            await db.commit()
            
            return {
                "status": "success",
                "deleted_count": deleted_count,
                "cutoff_date": cutoff_date.isoformat(),
                "days_kept": days_to_keep,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await db.rollback()
            raise e


@celery_app.task(bind=True, name="app.tasks.crypto_tasks.generate_market_report")
def generate_market_report(self) -> dict:
    """
    Background task to generate market analysis report
    
    Returns:
        Dict with report data
    """
    try:
        logger.info("Starting market report generation task")
        
        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Generating market report", "progress": 50}
            )
        
        import asyncio
        result = asyncio.run(_generate_market_report_async())
        
        logger.info("Market report generation completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_market_report task: {e}")
        if current_task:
            current_task.update_state(
                state="FAILURE",
                meta={"error": str(e)}
            )
        raise


async def _generate_market_report_async() -> dict:
    """Async helper function for market report generation"""
    async with AsyncSessionLocal() as db:
        try:
            # Get top cryptocurrencies by market cap
            top_cryptos = await cryptocurrency_service.get_cryptocurrencies(
                db=db,
                limit=10,
                sort_by="market_cap",
                order="desc"
            )
            
            # Calculate basic market stats
            total_market_cap = sum(
                crypto.market_cap for crypto in top_cryptos 
                if crypto.market_cap
            )
            
            avg_24h_change = sum(
                crypto.price_change_percentage_24h for crypto in top_cryptos 
                if crypto.price_change_percentage_24h
            ) / len(top_cryptos) if top_cryptos else 0
            
            return {
                "status": "success",
                "total_cryptocurrencies": len(top_cryptos),
                "total_market_cap": float(total_market_cap),
                "average_24h_change": float(avg_24h_change),
                "top_10_symbols": [crypto.symbol for crypto in top_cryptos],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise e
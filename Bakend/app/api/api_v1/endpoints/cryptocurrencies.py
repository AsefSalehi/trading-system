from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.db.database import get_db
from app.services.cryptocurrency_service import cryptocurrency_service
from app.schemas.cryptocurrency import (
    Cryptocurrency,
    CryptocurrencyList,
    PriceHistory,
    PriceHistoryList,
    DataUpdateResponse,
    ErrorResponse,
)
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/",
    response_model=CryptocurrencyList,
    summary="List cryptocurrencies",
    description="Get a paginated list of cryptocurrencies with optional filtering and sorting",
)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def list_cryptocurrencies(
    request,  # Required for rate limiting
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    sort_by: str = Query("market_cap_rank", description="Field to sort by"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    symbol_filter: Optional[str] = Query(
        None, description="Filter by symbol (partial match)"
    ),
    min_market_cap: Optional[float] = Query(
        None, ge=0, description="Minimum market cap filter"
    ),
    max_market_cap: Optional[float] = Query(
        None, ge=0, description="Maximum market cap filter"
    ),
    min_volume: Optional[float] = Query(
        None, ge=0, description="Minimum volume filter"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a paginated list of cryptocurrencies with optional filtering and sorting.

    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return (1-1000)
    - **sort_by**: Field to sort by (market_cap_rank, market_cap, total_volume, etc.)
    - **order**: Sort order (asc or desc)
    - **symbol_filter**: Filter by cryptocurrency symbol (partial match)
    - **min_market_cap**: Minimum market cap filter
    - **max_market_cap**: Maximum market cap filter
    - **min_volume**: Minimum 24h volume filter
    """
    try:
        cryptocurrencies = await cryptocurrency_service.get_cryptocurrencies(
            db=db,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            order=order,
            symbol_filter=symbol_filter,
            min_market_cap=min_market_cap,
            max_market_cap=max_market_cap,
            min_volume=min_volume,
        )

        # Calculate pagination info
        total = len(cryptocurrencies)  # Note: This is a simplified approach
        page = (skip // limit) + 1
        has_next = len(cryptocurrencies) == limit
        has_prev = skip > 0

        return CryptocurrencyList(
            items=cryptocurrencies,
            total=total,
            page=page,
            per_page=limit,
            has_next=has_next,
            has_prev=has_prev,
        )

    except Exception as e:
        logger.error(f"Error listing cryptocurrencies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching cryptocurrencies",
        )


@router.get(
    "/{symbol}",
    response_model=Cryptocurrency,
    summary="Get cryptocurrency by symbol",
    description="Retrieve detailed information for a specific cryptocurrency by its symbol",
)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def get_cryptocurrency(
    request,  # Required for rate limiting
    symbol: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information for a specific cryptocurrency by symbol.

    - **symbol**: Cryptocurrency symbol (e.g., BTC, ETH)
    """
    try:
        cryptocurrency = await cryptocurrency_service.get_cryptocurrency_by_symbol(
            db, symbol
        )

        if not cryptocurrency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cryptocurrency with symbol '{symbol}' not found",
            )

        return cryptocurrency

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cryptocurrency {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching cryptocurrency",
        )


@router.get(
    "/{symbol}/history",
    response_model=PriceHistoryList,
    summary="Get price history",
    description="Retrieve price history for a specific cryptocurrency",
)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def get_price_history(
    request,  # Required for rate limiting
    symbol: str,
    start_date: Optional[datetime] = Query(
        None, description="Start date for price history"
    ),
    end_date: Optional[datetime] = Query(
        None, description="End date for price history"
    ),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get price history for a specific cryptocurrency.

    - **symbol**: Cryptocurrency symbol (e.g., BTC, ETH)
    - **start_date**: Start date for filtering (ISO format)
    - **end_date**: End date for filtering (ISO format)
    - **limit**: Maximum number of records to return
    """
    try:
        # Verify cryptocurrency exists
        cryptocurrency = await cryptocurrency_service.get_cryptocurrency_by_symbol(
            db, symbol
        )
        if not cryptocurrency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cryptocurrency with symbol '{symbol}' not found",
            )

        price_history = await cryptocurrency_service.get_price_history(
            db=db, symbol=symbol, start_date=start_date, end_date=end_date, limit=limit
        )

        return PriceHistoryList(
            symbol=symbol.upper(), items=price_history, total=len(price_history)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price history for {symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching price history",
        )


@router.post(
    "/sync",
    response_model=DataUpdateResponse,
    summary="Sync cryptocurrency data",
    description="Fetch and update cryptocurrency data from external APIs",
)
@limiter.limit("10/minute")  # More restrictive for data sync
async def sync_cryptocurrency_data(
    request,  # Required for rate limiting
    limit: int = Query(
        100, ge=1, le=1000, description="Number of cryptocurrencies to sync"
    ),
    provider: str = Query(
        "coingecko", pattern="^(coingecko|coinmarketcap)$", description="Data provider"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually trigger synchronization of cryptocurrency data from external APIs.

    - **limit**: Number of cryptocurrencies to fetch and update
    - **provider**: External API provider (coingecko or coinmarketcap)

    Note: This endpoint is rate-limited to prevent abuse.
    """
    try:
        start_time = datetime.utcnow()
        logger.info(f"Starting manual crypto data sync with {provider}, limit: {limit}")

        cryptocurrencies = await cryptocurrency_service.fetch_and_store_listings(
            db=db, limit=limit, provider=provider
        )

        updated_count = len(cryptocurrencies)

        logger.info(
            f"Completed crypto data sync: {updated_count} cryptocurrencies processed"
        )

        return DataUpdateResponse(
            message=f"Successfully synced {updated_count} cryptocurrencies from {provider}",
            updated_count=updated_count,
            created_count=0,  # This would need to be tracked separately
            timestamp=start_time,
        )

    except Exception as e:
        logger.error(f"Error syncing cryptocurrency data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while syncing cryptocurrency data",
        )


@router.get(
    "/top/{category}",
    response_model=List[Cryptocurrency],
    summary="Get top cryptocurrencies by category",
    description="Get top cryptocurrencies filtered by specific categories",
)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def get_top_cryptocurrencies(
    request,  # Required for rate limiting
    category: str,
    limit: int = Query(
        10, ge=1, le=100, description="Number of top cryptocurrencies to return"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Get top cryptocurrencies by specific categories.

    - **category**: Category to filter by (market_cap, volume, gainers, losers)
    - **limit**: Number of cryptocurrencies to return
    """
    try:
        valid_categories = ["market_cap", "volume", "gainers", "losers"]
        if category not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}",
            )

        # Map categories to sort parameters
        sort_mapping = {
            "market_cap": ("market_cap", "desc"),
            "volume": ("total_volume", "desc"),
            "gainers": ("price_change_percentage_24h", "desc"),
            "losers": ("price_change_percentage_24h", "asc"),
        }

        sort_by, order = sort_mapping[category]

        cryptocurrencies = await cryptocurrency_service.get_cryptocurrencies(
            db=db, skip=0, limit=limit, sort_by=sort_by, order=order
        )

        return cryptocurrencies

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting top cryptocurrencies for category {category}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching top cryptocurrencies",
        )

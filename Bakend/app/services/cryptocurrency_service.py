from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from datetime import datetime, timedelta

from app.models.cryptocurrency import Cryptocurrency, PriceHistory
from app.services.crypto_data_providers import CoinGeckoProvider, CoinMarketCapProvider
from app.core.logging import logger
from app.core.cache import cache


class CryptocurrencyService:
    """Service for managing cryptocurrency data"""

    def __init__(self):
        self.coingecko_provider = CoinGeckoProvider()
        self.coinmarketcap_provider = CoinMarketCapProvider()

    async def fetch_and_store_listings(
        self, db: AsyncSession, limit: int = 100, provider: str = "coingecko"
    ) -> List[Cryptocurrency]:
        """
        Fetch cryptocurrency listings from external API and store in database

        Args:
            db: Database session
            limit: Number of cryptocurrencies to fetch
            provider: Data provider ("coingecko" or "coinmarketcap")

        Returns:
            List of stored cryptocurrency objects
        """
        try:
            # Choose provider
            if provider == "coinmarketcap":
                data_provider = self.coinmarketcap_provider
            else:
                data_provider = self.coingecko_provider

            # Fetch data from external API
            logger.info(f"Fetching {limit} cryptocurrencies from {provider}")
            crypto_data = await data_provider.fetch_listings(limit=limit)

            if not crypto_data:
                logger.warning(f"No data received from {provider}")
                return []

            stored_cryptos = []

            for coin_data in crypto_data:
                try:
                    # Check if cryptocurrency already exists
                    stmt = select(Cryptocurrency).where(
                        Cryptocurrency.symbol == coin_data["symbol"]
                    )
                    result = await db.execute(stmt)
                    existing_crypto = result.scalar_one_or_none()

                    if existing_crypto:
                        # Update existing cryptocurrency
                        await self._update_cryptocurrency(
                            db, existing_crypto, coin_data
                        )
                        stored_cryptos.append(existing_crypto)
                    else:
                        # Create new cryptocurrency
                        new_crypto = await self._create_cryptocurrency(db, coin_data)
                        if new_crypto:
                            stored_cryptos.append(new_crypto)

                    # Store price history
                    await self._store_price_history(db, coin_data)

                except Exception as e:
                    logger.error(
                        f"Error processing coin {coin_data.get('symbol', 'unknown')}: {e}"
                    )
                    continue

            await db.commit()
            logger.info(
                f"Successfully processed {len(stored_cryptos)} cryptocurrencies"
            )
            return stored_cryptos

        except Exception as e:
            logger.error(f"Error in fetch_and_store_listings: {e}")
            await db.rollback()
            return []

    async def _create_cryptocurrency(
        self, db: AsyncSession, coin_data: Dict[str, Any]
    ) -> Optional[Cryptocurrency]:
        """Create new cryptocurrency record"""
        try:
            crypto = Cryptocurrency(
                symbol=coin_data["symbol"],
                name=coin_data["name"],
                slug=coin_data["slug"],
                current_price=coin_data.get("current_price"),
                market_cap=coin_data.get("market_cap"),
                market_cap_rank=coin_data.get("market_cap_rank"),
                total_volume=coin_data.get("total_volume"),
                circulating_supply=coin_data.get("circulating_supply"),
                total_supply=coin_data.get("total_supply"),
                max_supply=coin_data.get("max_supply"),
                price_change_24h=coin_data.get("price_change_24h"),
                price_change_percentage_24h=coin_data.get(
                    "price_change_percentage_24h"
                ),
                price_change_percentage_7d=coin_data.get("price_change_percentage_7d"),
                price_change_percentage_30d=coin_data.get(
                    "price_change_percentage_30d"
                ),
                ath=coin_data.get("ath"),
                ath_date=coin_data.get("ath_date"),
                atl=coin_data.get("atl"),
                atl_date=coin_data.get("atl_date"),
                description=coin_data.get("description", ""),
                website=coin_data.get("website", ""),
                whitepaper=coin_data.get("whitepaper", ""),
                image_url=coin_data.get("image_url", ""),
                is_active=True,
                last_updated=coin_data.get("last_updated", datetime.utcnow()),
            )

            db.add(crypto)
            await db.flush()  # Get the ID without committing
            return crypto

        except Exception as e:
            logger.error(f"Error creating cryptocurrency record: {e}")
            return None

    async def _update_cryptocurrency(
        self, db: AsyncSession, crypto: Cryptocurrency, coin_data: Dict[str, Any]
    ) -> None:
        """Update existing cryptocurrency record"""
        try:
            # Update fields that might change
            crypto.name = coin_data["name"]
            crypto.slug = coin_data["slug"]
            crypto.current_price = coin_data.get("current_price")
            crypto.market_cap = coin_data.get("market_cap")
            crypto.market_cap_rank = coin_data.get("market_cap_rank")
            crypto.total_volume = coin_data.get("total_volume")
            crypto.circulating_supply = coin_data.get("circulating_supply")
            crypto.total_supply = coin_data.get("total_supply")
            crypto.max_supply = coin_data.get("max_supply")
            crypto.price_change_24h = coin_data.get("price_change_24h")
            crypto.price_change_percentage_24h = coin_data.get(
                "price_change_percentage_24h"
            )
            crypto.price_change_percentage_7d = coin_data.get(
                "price_change_percentage_7d"
            )
            crypto.price_change_percentage_30d = coin_data.get(
                "price_change_percentage_30d"
            )

            # Update ATH/ATL if they exist and are more recent
            if coin_data.get("ath") and (
                not crypto.ath or coin_data["ath"] > crypto.ath
            ):
                crypto.ath = coin_data["ath"]
                crypto.ath_date = coin_data.get("ath_date")

            if coin_data.get("atl") and (
                not crypto.atl or coin_data["atl"] < crypto.atl
            ):
                crypto.atl = coin_data["atl"]
                crypto.atl_date = coin_data.get("atl_date")

            # Update metadata if provided
            if coin_data.get("description"):
                crypto.description = coin_data["description"]
            if coin_data.get("website"):
                crypto.website = coin_data["website"]
            if coin_data.get("whitepaper"):
                crypto.whitepaper = coin_data["whitepaper"]
            if coin_data.get("image_url"):
                crypto.image_url = coin_data["image_url"]

            crypto.last_updated = coin_data.get("last_updated", datetime.utcnow())

        except Exception as e:
            logger.error(f"Error updating cryptocurrency record: {e}")

    async def _store_price_history(
        self, db: AsyncSession, coin_data: Dict[str, Any]
    ) -> None:
        """Store price history record"""
        try:
            if not coin_data.get("current_price"):
                return

            # Get cryptocurrency ID
            stmt = select(Cryptocurrency.id).where(
                Cryptocurrency.symbol == coin_data["symbol"]
            )
            result = await db.execute(stmt)
            crypto_id = result.scalar_one_or_none()

            if not crypto_id:
                return

            # Create price history record
            price_history = PriceHistory(
                cryptocurrency_id=crypto_id,
                symbol=coin_data["symbol"],
                price=coin_data["current_price"],
                market_cap=coin_data.get("market_cap"),
                total_volume=coin_data.get("total_volume"),
                timestamp=coin_data.get("last_updated", datetime.utcnow()),
            )

            db.add(price_history)

        except Exception as e:
            logger.error(f"Error storing price history: {e}")

    @cache(expire=timedelta(minutes=5), key_prefix="crypto_listings")
    async def get_cryptocurrencies(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "market_cap_rank",
        order: str = "asc",
        symbol_filter: Optional[str] = None,
        min_market_cap: Optional[float] = None,
        max_market_cap: Optional[float] = None,
        min_volume: Optional[float] = None,
    ) -> List[Cryptocurrency]:
        """
        Get cryptocurrencies with filtering and sorting

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_by: Field to sort by
            order: Sort order ("asc" or "desc")
            symbol_filter: Filter by symbol (partial match)
            min_market_cap: Minimum market cap filter
            max_market_cap: Maximum market cap filter
            min_volume: Minimum volume filter

        Returns:
            List of cryptocurrency objects
        """
        try:
            # Build query
            stmt = select(Cryptocurrency).where(Cryptocurrency.is_active == True)

            # Apply filters
            if symbol_filter:
                stmt = stmt.where(
                    Cryptocurrency.symbol.ilike(f"%{symbol_filter.upper()}%")
                )

            if min_market_cap is not None:
                stmt = stmt.where(Cryptocurrency.market_cap >= min_market_cap)

            if max_market_cap is not None:
                stmt = stmt.where(Cryptocurrency.market_cap <= max_market_cap)

            if min_volume is not None:
                stmt = stmt.where(Cryptocurrency.total_volume >= min_volume)

            # Apply sorting
            sort_column = getattr(
                Cryptocurrency, sort_by, Cryptocurrency.market_cap_rank
            )
            if order == "desc":
                stmt = stmt.order_by(sort_column.desc())
            else:
                stmt = stmt.order_by(sort_column.asc())

            # Apply pagination
            stmt = stmt.offset(skip).limit(limit)

            result = await db.execute(stmt)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting cryptocurrencies: {e}")
            return []

    async def get_cryptocurrency_by_symbol(
        self, db: AsyncSession, symbol: str
    ) -> Optional[Cryptocurrency]:
        """Get cryptocurrency by symbol"""
        try:
            stmt = select(Cryptocurrency).where(
                and_(
                    Cryptocurrency.symbol == symbol.upper(),
                    Cryptocurrency.is_active == True,
                )
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting cryptocurrency by symbol {symbol}: {e}")
            return None

    async def get_price_history(
        self,
        db: AsyncSession,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[PriceHistory]:
        """Get price history for a cryptocurrency"""
        try:
            stmt = select(PriceHistory).where(PriceHistory.symbol == symbol.upper())

            if start_date:
                stmt = stmt.where(PriceHistory.timestamp >= start_date)

            if end_date:
                stmt = stmt.where(PriceHistory.timestamp <= end_date)

            stmt = stmt.order_by(PriceHistory.timestamp.desc()).limit(limit)

            result = await db.execute(stmt)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting price history for {symbol}: {e}")
            return []


# Global service instance
cryptocurrency_service = CryptocurrencyService()

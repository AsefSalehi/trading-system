from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
from decimal import Decimal
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger


class CryptoDataProvider(ABC):
    """Abstract base class for cryptocurrency data providers"""

    @abstractmethod
    async def fetch_listings(
        self, limit: int = 100, sort: str = "market_cap"
    ) -> List[Dict[str, Any]]:
        """Fetch cryptocurrency listings"""
        pass

    @abstractmethod
    async def fetch_coin_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data for a specific cryptocurrency"""
        pass


class CoinGeckoProvider(CryptoDataProvider):
    """CoinGecko API provider for cryptocurrency data"""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = settings.COINGECKO_API_KEY

    async def fetch_cryptocurrency_listings(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Alias for fetch_listings for backward compatibility"""
        return await self.fetch_listings(limit=limit)

    async def fetch_listings(
        self, limit: int = 100, sort: str = "market_cap_desc"
    ) -> List[Dict[str, Any]]:
        """Fetch cryptocurrency listings from CoinGecko"""
        try:
            # Try the public API first (no auth required for basic data)
            url = f"{self.base_url}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": sort,
                "per_page": min(limit, 10),  # Reduced limit for public API
                "page": 1,
                "sparkline": False,
            }

            headers = {
                "User-Agent": "TradingSystem/1.0"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Fetched {len(data)} coins from CoinGecko")
                    return self._normalize_listings_data(data)
                else:
                    logger.warning(f"CoinGecko API returned {response.status_code}, using fallback data")
                    return self._get_fallback_data(limit)

        except Exception as e:
            logger.warning(f"Error fetching from CoinGecko: {e}, using fallback data")
            return self._get_fallback_data(limit)

    def _get_fallback_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Provide fallback cryptocurrency data when API is unavailable"""
        fallback_data = [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "slug": "bitcoin",
                "current_price": Decimal("43250.00"),
                "market_cap": Decimal("847500000000"),
                "market_cap_rank": 1,
                "total_volume": Decimal("15200000000"),
                "circulating_supply": Decimal("19600000"),
                "total_supply": Decimal("19600000"),
                "max_supply": Decimal("21000000"),
                "price_change_24h": Decimal("1250.00"),
                "price_change_percentage_24h": Decimal("2.98"),
                "price_change_percentage_7d": Decimal("5.42"),
                "price_change_percentage_30d": Decimal("-1.23"),
                "last_updated": datetime.utcnow(),
            },
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "slug": "ethereum",
                "current_price": Decimal("2650.00"),
                "market_cap": Decimal("318600000000"),
                "market_cap_rank": 2,
                "total_volume": Decimal("8900000000"),
                "circulating_supply": Decimal("120200000"),
                "total_supply": Decimal("120200000"),
                "max_supply": None,
                "price_change_24h": Decimal("85.50"),
                "price_change_percentage_24h": Decimal("3.34"),
                "price_change_percentage_7d": Decimal("7.12"),
                "price_change_percentage_30d": Decimal("2.45"),
                "last_updated": datetime.utcnow(),
            },
            {
                "symbol": "BNB",
                "name": "BNB",
                "slug": "binancecoin",
                "current_price": Decimal("315.80"),
                "market_cap": Decimal("47200000000"),
                "market_cap_rank": 3,
                "total_volume": Decimal("1200000000"),
                "circulating_supply": Decimal("149500000"),
                "total_supply": Decimal("149500000"),
                "max_supply": Decimal("200000000"),
                "price_change_24h": Decimal("8.20"),
                "price_change_percentage_24h": Decimal("2.67"),
                "price_change_percentage_7d": Decimal("4.89"),
                "price_change_percentage_30d": Decimal("1.12"),
                "last_updated": datetime.utcnow(),
            },
            {
                "symbol": "SOL",
                "name": "Solana",
                "slug": "solana",
                "current_price": Decimal("98.45"),
                "market_cap": Decimal("43800000000"),
                "market_cap_rank": 4,
                "total_volume": Decimal("2100000000"),
                "circulating_supply": Decimal("444800000"),
                "total_supply": Decimal("580000000"),
                "max_supply": None,
                "price_change_24h": Decimal("3.25"),
                "price_change_percentage_24h": Decimal("3.42"),
                "price_change_percentage_7d": Decimal("8.76"),
                "price_change_percentage_30d": Decimal("15.23"),
                "last_updated": datetime.utcnow(),
            },
            {
                "symbol": "XRP",
                "name": "XRP",
                "slug": "ripple",
                "current_price": Decimal("0.5234"),
                "market_cap": Decimal("28900000000"),
                "market_cap_rank": 5,
                "total_volume": Decimal("1050000000"),
                "circulating_supply": Decimal("55200000000"),
                "total_supply": Decimal("99900000000"),
                "max_supply": Decimal("100000000000"),
                "price_change_24h": Decimal("0.0123"),
                "price_change_percentage_24h": Decimal("2.41"),
                "price_change_percentage_7d": Decimal("1.89"),
                "price_change_percentage_30d": Decimal("-3.45"),
                "last_updated": datetime.utcnow(),
            }
        ]

        logger.info(f"Using fallback data: {len(fallback_data[:limit])} cryptocurrencies")
        return fallback_data[:limit]

    async def fetch_coin_data(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed data for a specific cryptocurrency"""
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                "localization": False,
                "tickers": False,
                "market_data": True,
                "community_data": False,
                "developer_data": False,
                "sparkline": False,
            }

            headers = {}
            if self.api_key:
                headers["x-cg-demo-api-key"] = self.api_key

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()
                return self._normalize_coin_data(data)

        except Exception as e:
            logger.error(f"Error fetching coin data for {coin_id}: {e}")
            return None

    def _normalize_listings_data(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """Normalize CoinGecko listings data to our format"""
        normalized = []

        for coin in data:
            try:
                normalized_coin = {
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name", ""),
                    "slug": coin.get("id", ""),
                    "current_price": (
                        Decimal(str(coin.get("current_price", 0)))
                        if coin.get("current_price")
                        else None
                    ),
                    "market_cap": (
                        Decimal(str(coin.get("market_cap", 0)))
                        if coin.get("market_cap")
                        else None
                    ),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "total_volume": (
                        Decimal(str(coin.get("total_volume", 0)))
                        if coin.get("total_volume")
                        else None
                    ),
                    "circulating_supply": (
                        Decimal(str(coin.get("circulating_supply", 0)))
                        if coin.get("circulating_supply")
                        else None
                    ),
                    "total_supply": (
                        Decimal(str(coin.get("total_supply", 0)))
                        if coin.get("total_supply")
                        else None
                    ),
                    "max_supply": (
                        Decimal(str(coin.get("max_supply", 0)))
                        if coin.get("max_supply")
                        else None
                    ),
                    "price_change_24h": (
                        Decimal(str(coin.get("price_change_24h", 0)))
                        if coin.get("price_change_24h")
                        else None
                    ),
                    "price_change_percentage_24h": (
                        Decimal(str(coin.get("price_change_percentage_24h", 0)))
                        if coin.get("price_change_percentage_24h")
                        else None
                    ),
                    "price_change_percentage_7d": (
                        Decimal(
                            str(coin.get("price_change_percentage_7d_in_currency", 0))
                        )
                        if coin.get("price_change_percentage_7d_in_currency")
                        else None
                    ),
                    "price_change_percentage_30d": (
                        Decimal(
                            str(coin.get("price_change_percentage_30d_in_currency", 0))
                        )
                        if coin.get("price_change_percentage_30d_in_currency")
                        else None
                    ),
                    "ath": (
                        Decimal(str(coin.get("ath", 0))) if coin.get("ath") else None
                    ),
                    "ath_date": (
                        datetime.fromisoformat(
                            coin.get("ath_date", "").replace("Z", "+00:00")
                        )
                        if coin.get("ath_date")
                        else None
                    ),
                    "atl": (
                        Decimal(str(coin.get("atl", 0))) if coin.get("atl") else None
                    ),
                    "atl_date": (
                        datetime.fromisoformat(
                            coin.get("atl_date", "").replace("Z", "+00:00")
                        )
                        if coin.get("atl_date")
                        else None
                    ),
                    "image_url": coin.get("image", ""),
                    "last_updated": (
                        datetime.fromisoformat(
                            coin.get("last_updated", "").replace("Z", "+00:00")
                        )
                        if coin.get("last_updated")
                        else datetime.utcnow()
                    ),
                }
                normalized.append(normalized_coin)
            except Exception as e:
                logger.error(
                    f"Error normalizing coin data for {coin.get('id', 'unknown')}: {e}"
                )
                continue

        return normalized

    def _normalize_coin_data(self, data: Dict) -> Dict[str, Any]:
        """Normalize CoinGecko coin data to our format"""
        try:
            market_data = data.get("market_data", {})

            return {
                "symbol": data.get("symbol", "").upper(),
                "name": data.get("name", ""),
                "slug": data.get("id", ""),
                "description": data.get("description", {}).get("en", ""),
                "website": (
                    data.get("links", {}).get("homepage", [""])[0]
                    if data.get("links", {}).get("homepage")
                    else ""
                ),
                "whitepaper": data.get("links", {}).get("whitepaper", ""),
                "current_price": (
                    Decimal(str(market_data.get("current_price", {}).get("usd", 0)))
                    if market_data.get("current_price", {}).get("usd")
                    else None
                ),
                "market_cap": (
                    Decimal(str(market_data.get("market_cap", {}).get("usd", 0)))
                    if market_data.get("market_cap", {}).get("usd")
                    else None
                ),
                "market_cap_rank": market_data.get("market_cap_rank"),
                "total_volume": (
                    Decimal(str(market_data.get("total_volume", {}).get("usd", 0)))
                    if market_data.get("total_volume", {}).get("usd")
                    else None
                ),
                "circulating_supply": (
                    Decimal(str(market_data.get("circulating_supply", 0)))
                    if market_data.get("circulating_supply")
                    else None
                ),
                "total_supply": (
                    Decimal(str(market_data.get("total_supply", 0)))
                    if market_data.get("total_supply")
                    else None
                ),
                "max_supply": (
                    Decimal(str(market_data.get("max_supply", 0)))
                    if market_data.get("max_supply")
                    else None
                ),
                "image_url": data.get("image", {}).get("large", ""),
                "last_updated": (
                    datetime.fromisoformat(
                        market_data.get("last_updated", "").replace("Z", "+00:00")
                    )
                    if market_data.get("last_updated")
                    else datetime.utcnow()
                ),
            }
        except Exception as e:
            logger.error(f"Error normalizing detailed coin data: {e}")
            return {}


class CoinMarketCapProvider(CryptoDataProvider):
    """CoinMarketCap API provider for cryptocurrency data"""

    def __init__(self):
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.api_key = settings.COINMARKETCAP_API_KEY

    async def fetch_listings(
        self, limit: int = 100, sort: str = "market_cap"
    ) -> List[Dict[str, Any]]:
        """Fetch cryptocurrency listings from CoinMarketCap"""
        if not self.api_key:
            logger.warning("CoinMarketCap API key not configured")
            return []

        try:
            url = f"{self.base_url}/cryptocurrency/listings/latest"
            params = {
                "limit": min(limit, 5000),  # CMC max is 5000
                "sort": sort,
                "convert": "USD",
            }

            headers = {"X-CMC_PRO_API_KEY": self.api_key, "Accept": "application/json"}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()
                coins = data.get("data", [])
                logger.info(f"Fetched {len(coins)} coins from CoinMarketCap")

                return self._normalize_listings_data(coins)

        except Exception as e:
            logger.error(f"Error fetching listings from CoinMarketCap: {e}")
            return []

    async def fetch_coin_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch data for a specific cryptocurrency by symbol"""
        if not self.api_key:
            logger.warning("CoinMarketCap API key not configured")
            return None

        try:
            url = f"{self.base_url}/cryptocurrency/quotes/latest"
            params = {"symbol": symbol.upper(), "convert": "USD"}

            headers = {"X-CMC_PRO_API_KEY": self.api_key, "Accept": "application/json"}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()
                coin_data = data.get("data", {}).get(symbol.upper())

                if coin_data:
                    return self._normalize_coin_data(coin_data)
                return None

        except Exception as e:
            logger.error(f"Error fetching coin data for {symbol}: {e}")
            return None

    def _normalize_listings_data(self, data: List[Dict]) -> List[Dict[str, Any]]:
        """Normalize CoinMarketCap listings data to our format"""
        normalized = []

        for coin in data:
            try:
                quote = coin.get("quote", {}).get("USD", {})

                normalized_coin = {
                    "symbol": coin.get("symbol", ""),
                    "name": coin.get("name", ""),
                    "slug": coin.get("slug", ""),
                    "current_price": (
                        Decimal(str(quote.get("price", 0)))
                        if quote.get("price")
                        else None
                    ),
                    "market_cap": (
                        Decimal(str(quote.get("market_cap", 0)))
                        if quote.get("market_cap")
                        else None
                    ),
                    "market_cap_rank": coin.get("cmc_rank"),
                    "total_volume": (
                        Decimal(str(quote.get("volume_24h", 0)))
                        if quote.get("volume_24h")
                        else None
                    ),
                    "circulating_supply": (
                        Decimal(str(coin.get("circulating_supply", 0)))
                        if coin.get("circulating_supply")
                        else None
                    ),
                    "total_supply": (
                        Decimal(str(coin.get("total_supply", 0)))
                        if coin.get("total_supply")
                        else None
                    ),
                    "max_supply": (
                        Decimal(str(coin.get("max_supply", 0)))
                        if coin.get("max_supply")
                        else None
                    ),
                    "price_change_24h": (
                        Decimal(str(quote.get("percent_change_24h", 0)))
                        if quote.get("percent_change_24h")
                        else None
                    ),
                    "price_change_percentage_24h": (
                        Decimal(str(quote.get("percent_change_24h", 0)))
                        if quote.get("percent_change_24h")
                        else None
                    ),
                    "price_change_percentage_7d": (
                        Decimal(str(quote.get("percent_change_7d", 0)))
                        if quote.get("percent_change_7d")
                        else None
                    ),
                    "price_change_percentage_30d": (
                        Decimal(str(quote.get("percent_change_30d", 0)))
                        if quote.get("percent_change_30d")
                        else None
                    ),
                    "last_updated": (
                        datetime.fromisoformat(
                            quote.get("last_updated", "").replace("Z", "+00:00")
                        )
                        if quote.get("last_updated")
                        else datetime.utcnow()
                    ),
                }
                normalized.append(normalized_coin)
            except Exception as e:
                logger.error(
                    f"Error normalizing coin data for {coin.get('symbol', 'unknown')}: {e}"
                )
                continue

        return normalized

    def _normalize_coin_data(self, data: Dict) -> Dict[str, Any]:
        """Normalize CoinMarketCap coin data to our format"""
        try:
            quote = data.get("quote", {}).get("USD", {})

            return {
                "symbol": data.get("symbol", ""),
                "name": data.get("name", ""),
                "slug": data.get("slug", ""),
                "current_price": (
                    Decimal(str(quote.get("price", 0))) if quote.get("price") else None
                ),
                "market_cap": (
                    Decimal(str(quote.get("market_cap", 0)))
                    if quote.get("market_cap")
                    else None
                ),
                "market_cap_rank": data.get("cmc_rank"),
                "total_volume": (
                    Decimal(str(quote.get("volume_24h", 0)))
                    if quote.get("volume_24h")
                    else None
                ),
                "circulating_supply": (
                    Decimal(str(data.get("circulating_supply", 0)))
                    if data.get("circulating_supply")
                    else None
                ),
                "total_supply": (
                    Decimal(str(data.get("total_supply", 0)))
                    if data.get("total_supply")
                    else None
                ),
                "max_supply": (
                    Decimal(str(data.get("max_supply", 0)))
                    if data.get("max_supply")
                    else None
                ),
                "last_updated": (
                    datetime.fromisoformat(
                        quote.get("last_updated", "").replace("Z", "+00:00")
                    )
                    if quote.get("last_updated")
                    else datetime.utcnow()
                ),
            }
        except Exception as e:
            logger.error(f"Error normalizing detailed coin data: {e}")
            return {}

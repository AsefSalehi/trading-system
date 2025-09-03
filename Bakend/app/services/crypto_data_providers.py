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

    async def fetch_listings(
        self, limit: int = 100, sort: str = "market_cap_desc"
    ) -> List[Dict[str, Any]]:
        """Fetch cryptocurrency listings from CoinGecko"""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": sort,
                "per_page": min(limit, 250),  # CoinGecko max is 250
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h,7d,30d",
            }

            headers = {}
            if self.api_key:
                headers["x-cg-demo-api-key"] = self.api_key

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                data = response.json()
                logger.info(f"Fetched {len(data)} coins from CoinGecko")

                return self._normalize_listings_data(data)

        except Exception as e:
            logger.error(f"Error fetching listings from CoinGecko: {e}")
            return []

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

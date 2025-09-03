import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal
from datetime import datetime

from app.services.crypto_data_providers import CoinGeckoProvider, CoinMarketCapProvider


class TestCoinGeckoProvider:
    """Test cases for CoinGecko data provider"""

    @pytest.fixture
    def provider(self):
        return CoinGeckoProvider()

    @pytest.mark.asyncio
    async def test_fetch_listings_success(self, provider):
        """Test successful listings fetch from CoinGecko"""
        mock_response_data = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0,
                "market_cap": 850000000000,
                "market_cap_rank": 1,
                "total_volume": 25000000000,
                "circulating_supply": 19000000,
                "total_supply": 21000000,
                "max_supply": 21000000,
                "price_change_24h": 1200.0,
                "price_change_percentage_24h": 2.75,
                "ath": 69000.0,
                "ath_date": "2021-11-10T14:24:11.849Z",
                "atl": 67.81,
                "atl_date": "2013-07-06T00:00:00.000Z",
                "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
                "last_updated": "2024-01-01T12:00:00.000Z",
            }
        ]

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.fetch_listings(limit=1)

            assert len(result) == 1
            crypto = result[0]
            assert crypto["symbol"] == "BTC"
            assert crypto["name"] == "Bitcoin"
            assert crypto["current_price"] == Decimal("45000.0")
            assert crypto["market_cap_rank"] == 1

    @pytest.mark.asyncio
    async def test_fetch_listings_api_error(self, provider):
        """Test handling of API errors during listings fetch"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("API Error")
            )

            result = await provider.fetch_listings()
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_coin_data_success(self, provider):
        """Test successful individual coin data fetch"""
        mock_response_data = {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "description": {"en": "Bitcoin is the first successful internet money"},
            "links": {
                "homepage": ["https://bitcoin.org"],
                "whitepaper": "https://bitcoin.org/bitcoin.pdf",
            },
            "image": {
                "large": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"
            },
            "market_data": {
                "current_price": {"usd": 45000.0},
                "market_cap": {"usd": 850000000000},
                "market_cap_rank": 1,
                "total_volume": {"usd": 25000000000},
                "circulating_supply": 19000000,
                "total_supply": 21000000,
                "max_supply": 21000000,
                "last_updated": "2024-01-01T12:00:00.000Z",
            },
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.fetch_coin_data("bitcoin")

            assert result["symbol"] == "BTC"
            assert result["name"] == "Bitcoin"
            assert (
                result["description"]
                == "Bitcoin is the first successful internet money"
            )
            assert result["website"] == "https://bitcoin.org"

    def test_normalize_listings_data(self, provider):
        """Test data normalization for listings"""
        raw_data = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 45000.0,
                "market_cap": 850000000000,
                "market_cap_rank": 1,
                "last_updated": "2024-01-01T12:00:00.000Z",
            }
        ]

        result = provider._normalize_listings_data(raw_data)

        assert len(result) == 1
        crypto = result[0]
        assert crypto["symbol"] == "BTC"
        assert crypto["current_price"] == Decimal("45000.0")
        assert isinstance(crypto["last_updated"], datetime)


class TestCoinMarketCapProvider:
    """Test cases for CoinMarketCap data provider"""

    @pytest.fixture
    def provider(self):
        with patch.object(CoinMarketCapProvider, "__init__", lambda x: None):
            provider = CoinMarketCapProvider()
            provider.base_url = "https://pro-api.coinmarketcap.com/v1"
            provider.api_key = "test_api_key"
            return provider

    @pytest.mark.asyncio
    async def test_fetch_listings_no_api_key(self):
        """Test listings fetch without API key"""
        provider = CoinMarketCapProvider()
        provider.api_key = None

        result = await provider.fetch_listings()
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_listings_success(self, provider):
        """Test successful listings fetch from CoinMarketCap"""
        mock_response_data = {
            "data": [
                {
                    "id": 1,
                    "symbol": "BTC",
                    "name": "Bitcoin",
                    "slug": "bitcoin",
                    "cmc_rank": 1,
                    "circulating_supply": 19000000,
                    "total_supply": 21000000,
                    "max_supply": 21000000,
                    "quote": {
                        "USD": {
                            "price": 45000.0,
                            "market_cap": 850000000000,
                            "volume_24h": 25000000000,
                            "percent_change_24h": 2.75,
                            "percent_change_7d": 5.2,
                            "percent_change_30d": -3.1,
                            "last_updated": "2024-01-01T12:00:00.000Z",
                        }
                    },
                }
            ]
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.fetch_listings(limit=1)

            assert len(result) == 1
            crypto = result[0]
            assert crypto["symbol"] == "BTC"
            assert crypto["name"] == "Bitcoin"
            assert crypto["current_price"] == Decimal("45000.0")
            assert crypto["market_cap_rank"] == 1

    def test_normalize_coin_data(self, provider):
        """Test data normalization for individual coin"""
        raw_data = {
            "symbol": "BTC",
            "name": "Bitcoin",
            "slug": "bitcoin",
            "cmc_rank": 1,
            "circulating_supply": 19000000,
            "quote": {
                "USD": {
                    "price": 45000.0,
                    "market_cap": 850000000000,
                    "last_updated": "2024-01-01T12:00:00.000Z",
                }
            },
        }

        result = provider._normalize_coin_data(raw_data)

        assert result["symbol"] == "BTC"
        assert result["current_price"] == Decimal("45000.0")
        assert isinstance(result["last_updated"], datetime)


class TestDataProviderErrorHandling:
    """Test error handling across providers"""

    @pytest.mark.asyncio
    async def test_coingecko_network_error(self):
        """Test CoinGecko provider handles network errors gracefully"""
        provider = CoinGeckoProvider()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Network timeout")
            )

            result = await provider.fetch_listings()
            assert result == []

    @pytest.mark.asyncio
    async def test_coinmarketcap_http_error(self):
        """Test CoinMarketCap provider handles HTTP errors gracefully"""
        provider = CoinMarketCapProvider()
        provider.api_key = "test_key"

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("HTTP 401")

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await provider.fetch_listings()
            assert result == []

    def test_data_normalization_missing_fields(self):
        """Test data normalization handles missing fields gracefully"""
        provider = CoinGeckoProvider()

        # Data with missing fields
        raw_data = [{"id": "test", "symbol": "test"}]

        result = provider._normalize_listings_data(raw_data)

        assert len(result) == 1
        crypto = result[0]
        assert crypto["symbol"] == "TEST"
        assert crypto["current_price"] is None
        assert crypto["market_cap"] is None

    def test_invalid_datetime_handling(self):
        """Test handling of invalid datetime strings"""
        provider = CoinGeckoProvider()

        raw_data = [
            {
                "id": "test",
                "symbol": "test",
                "name": "Test",
                "last_updated": "invalid-date",
            }
        ]

        result = provider._normalize_listings_data(raw_data)

        assert len(result) == 1
        # Should use current time as fallback
        assert isinstance(result[0]["last_updated"], datetime)

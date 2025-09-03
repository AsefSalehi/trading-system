import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.cryptocurrency_service import CryptocurrencyService
from app.models.cryptocurrency import Cryptocurrency


class TestCryptocurrencyService:
    """Test cases for cryptocurrency service"""

    @pytest.fixture
    def service(self):
        return CryptocurrencyService()

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        session = Mock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.add = Mock()
        session.flush = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session

    @pytest.fixture
    def sample_crypto_data(self):
        """Sample cryptocurrency data for testing"""
        return {
            "symbol": "BTC",
            "name": "Bitcoin",
            "slug": "bitcoin",
            "current_price": Decimal("45000.0"),
            "market_cap": Decimal("850000000000"),
            "market_cap_rank": 1,
            "total_volume": Decimal("25000000000"),
            "circulating_supply": Decimal("19000000"),
            "last_updated": datetime.utcnow(),
        }

    @pytest.mark.asyncio
    async def test_fetch_and_store_listings_success(
        self, service, mock_db_session, sample_crypto_data
    ):
        """Test successful fetch and store of cryptocurrency listings"""
        # Mock provider to return sample data
        with patch.object(service.coingecko_provider, "fetch_listings") as mock_fetch:
            mock_fetch.return_value = [sample_crypto_data]

            # Mock database queries
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None  # No existing crypto
            mock_db_session.execute.return_value = mock_result

            result = await service.fetch_and_store_listings(
                db=mock_db_session, limit=1, provider="coingecko"
            )

            # Verify provider was called
            mock_fetch.assert_called_once_with(limit=1)

            # Verify database operations
            mock_db_session.add.assert_called()
            mock_db_session.commit.assert_called_once()

            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_fetch_and_store_listings_update_existing(
        self, service, mock_db_session, sample_crypto_data
    ):
        """Test updating existing cryptocurrency"""
        # Create existing crypto mock
        existing_crypto = Cryptocurrency(
            id=1,
            symbol="BTC",
            name="Bitcoin",
            slug="bitcoin",
            current_price=Decimal("44000.0"),  # Different price
            market_cap_rank=1,
        )

        with patch.object(service.coingecko_provider, "fetch_listings") as mock_fetch:
            mock_fetch.return_value = [sample_crypto_data]

            # Mock database to return existing crypto
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = existing_crypto
            mock_db_session.execute.return_value = mock_result

            result = await service.fetch_and_store_listings(db=mock_db_session, limit=1)

            # Verify crypto was updated
            assert existing_crypto.current_price == sample_crypto_data["current_price"]
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_and_store_listings_provider_error(
        self, service, mock_db_session
    ):
        """Test handling of provider errors"""
        with patch.object(service.coingecko_provider, "fetch_listings") as mock_fetch:
            mock_fetch.return_value = []  # Empty result simulating error

            result = await service.fetch_and_store_listings(db=mock_db_session, limit=1)

            assert result == []
            # Should not call commit on empty result
            mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_cryptocurrencies_with_filters(self, service, mock_db_session):
        """Test getting cryptocurrencies with various filters"""
        # Mock database result
        mock_cryptos = [
            Mock(spec=Cryptocurrency, symbol="BTC", market_cap=Decimal("850000000000")),
            Mock(spec=Cryptocurrency, symbol="ETH", market_cap=Decimal("400000000000")),
        ]

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_cryptos
        mock_db_session.execute.return_value = mock_result

        result = await service.get_cryptocurrencies(
            db=mock_db_session,
            skip=0,
            limit=10,
            symbol_filter="BT",
            min_market_cap=100000000000,
        )

        assert len(result) == 2
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cryptocurrency_by_symbol_found(self, service, mock_db_session):
        """Test getting cryptocurrency by symbol when found"""
        mock_crypto = Mock(spec=Cryptocurrency, symbol="BTC")

        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_crypto
        mock_db_session.execute.return_value = mock_result

        result = await service.get_cryptocurrency_by_symbol(mock_db_session, "BTC")

        assert result == mock_crypto

    @pytest.mark.asyncio
    async def test_get_cryptocurrency_by_symbol_not_found(
        self, service, mock_db_session
    ):
        """Test getting cryptocurrency by symbol when not found"""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await service.get_cryptocurrency_by_symbol(mock_db_session, "UNKNOWN")

        assert result is None

    @pytest.mark.asyncio
    async def test_create_cryptocurrency_success(
        self, service, mock_db_session, sample_crypto_data
    ):
        """Test successful cryptocurrency creation"""
        result = await service._create_cryptocurrency(
            mock_db_session, sample_crypto_data
        )

        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()

        assert result is not None
        assert result.symbol == "BTC"
        assert result.current_price == sample_crypto_data["current_price"]

    @pytest.mark.asyncio
    async def test_update_cryptocurrency(self, service, sample_crypto_data):
        """Test cryptocurrency update"""
        existing_crypto = Cryptocurrency(
            id=1,
            symbol="BTC",
            name="Bitcoin",
            slug="bitcoin",
            current_price=Decimal("44000.0"),
            market_cap_rank=1,
        )

        await service._update_cryptocurrency(
            Mock(), existing_crypto, sample_crypto_data
        )

        assert existing_crypto.current_price == sample_crypto_data["current_price"]
        assert existing_crypto.market_cap == sample_crypto_data["market_cap"]

    @pytest.mark.asyncio
    async def test_store_price_history(
        self, service, mock_db_session, sample_crypto_data
    ):
        """Test storing price history"""
        # Mock crypto ID lookup
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = 1
        mock_db_session.execute.return_value = mock_result

        await service._store_price_history(mock_db_session, sample_crypto_data)

        mock_db_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_price_history(self, service, mock_db_session):
        """Test getting price history"""
        from app.models.cryptocurrency import PriceHistory

        mock_history = [
            Mock(spec=PriceHistory, symbol="BTC", price=Decimal("45000")),
            Mock(spec=PriceHistory, symbol="BTC", price=Decimal("44500")),
        ]

        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_history
        mock_db_session.execute.return_value = mock_result

        result = await service.get_price_history(mock_db_session, "BTC")

        assert len(result) == 2
        assert all(h.symbol == "BTC" for h in result)

    @pytest.mark.asyncio
    async def test_database_error_handling(
        self, service, mock_db_session, sample_crypto_data
    ):
        """Test handling of database errors"""
        # Mock database error
        mock_db_session.execute.side_effect = Exception("Database error")

        result = await service.get_cryptocurrencies(mock_db_session)

        assert result == []

    @pytest.mark.asyncio
    async def test_rollback_on_error(self, service, mock_db_session):
        """Test database rollback on error"""
        with patch.object(service.coingecko_provider, "fetch_listings") as mock_fetch:
            mock_fetch.side_effect = Exception("Provider error")

            result = await service.fetch_and_store_listings(mock_db_session)

            assert result == []
            mock_db_session.rollback.assert_called_once()


class TestCryptocurrencyServiceCaching:
    """Test caching behavior of cryptocurrency service"""

    @pytest.fixture
    def service(self):
        return CryptocurrencyService()

    @pytest.mark.asyncio
    @patch("app.core.cache.redis_client")
    async def test_cache_hit(self, mock_redis, service):
        """Test cache hit scenario"""
        # Mock cache hit
        cached_data = [{"symbol": "BTC", "name": "Bitcoin"}]
        mock_redis.get.return_value = cached_data

        mock_db_session = Mock(spec=AsyncSession)

        # This would normally hit cache if implemented properly
        result = await service.get_cryptocurrencies(mock_db_session)

        # Note: Actual cache testing would require proper cache implementation
        # This is a placeholder for cache testing structure

    @pytest.mark.asyncio
    @patch("app.core.cache.redis_client")
    async def test_cache_miss(self, mock_redis, service):
        """Test cache miss scenario"""
        # Mock cache miss
        mock_redis.get.return_value = None

        mock_db_session = Mock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result

        result = await service.get_cryptocurrencies(mock_db_session)

        # Should call database when cache misses
        mock_db_session.execute.assert_called_once()

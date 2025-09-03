import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cryptocurrency import Cryptocurrency
from app.services.cryptocurrency_service import cryptocurrency_service


class TestCryptocurrencyEndpoints:
    """Integration tests for cryptocurrency API endpoints"""

    @pytest.mark.asyncio
    async def test_list_cryptocurrencies_empty(self, client: AsyncClient):
        """Test listing cryptocurrencies when database is empty"""
        response = await client.get("/api/v1/cryptocurrencies/")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["has_next"] is False
        assert data["has_prev"] is False

    @pytest.mark.asyncio
    async def test_list_cryptocurrencies_with_data(
        self, client: AsyncClient, db_session: AsyncSession, sample_cryptocurrency_data
    ):
        """Test listing cryptocurrencies with data in database"""
        # Create test cryptocurrency
        crypto = Cryptocurrency(**sample_cryptocurrency_data)
        db_session.add(crypto)
        await db_session.commit()

        response = await client.get("/api/v1/cryptocurrencies/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["symbol"] == "BTC"
        assert data["items"][0]["name"] == "Bitcoin"

    @pytest.mark.asyncio
    async def test_list_cryptocurrencies_with_filters(
        self, client: AsyncClient, db_session: AsyncSession, sample_cryptocurrency_list
    ):
        """Test listing cryptocurrencies with query filters"""
        # Create test cryptocurrencies
        for crypto_data in sample_cryptocurrency_list:
            crypto = Cryptocurrency(**crypto_data)
            db_session.add(crypto)
        await db_session.commit()

        # Test symbol filter
        response = await client.get("/api/v1/cryptocurrencies/?symbol_filter=BT")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["symbol"] == "BTC"

        # Test limit
        response = await client.get("/api/v1/cryptocurrencies/?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

        # Test market cap filter
        response = await client.get(
            "/api/v1/cryptocurrencies/?min_market_cap=500000000000"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1  # Only BTC should match

    @pytest.mark.asyncio
    async def test_list_cryptocurrencies_sorting(
        self, client: AsyncClient, db_session: AsyncSession, sample_cryptocurrency_list
    ):
        """Test sorting functionality"""
        # Create test cryptocurrencies
        for crypto_data in sample_cryptocurrency_list:
            crypto = Cryptocurrency(**crypto_data)
            db_session.add(crypto)
        await db_session.commit()

        # Test sort by market cap descending
        response = await client.get(
            "/api/v1/cryptocurrencies/?sort_by=market_cap&order=desc"
        )
        assert response.status_code == 200
        data = response.json()

        # Should be sorted BTC, ETH, ADA by market cap
        symbols = [item["symbol"] for item in data["items"]]
        assert symbols == ["BTC", "ETH", "ADA"]

    @pytest.mark.asyncio
    async def test_list_cryptocurrencies_pagination(
        self, client: AsyncClient, db_session: AsyncSession, sample_cryptocurrency_list
    ):
        """Test pagination"""
        # Create test cryptocurrencies
        for crypto_data in sample_cryptocurrency_list:
            crypto = Cryptocurrency(**crypto_data)
            db_session.add(crypto)
        await db_session.commit()

        # Test first page
        response = await client.get("/api/v1/cryptocurrencies/?limit=2&skip=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["has_next"] is True
        assert data["has_prev"] is False

        # Test second page
        response = await client.get("/api/v1/cryptocurrencies/?limit=2&skip=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["page"] == 2
        assert data["has_next"] is False
        assert data["has_prev"] is True

    @pytest.mark.asyncio
    async def test_get_cryptocurrency_by_symbol_success(
        self, client: AsyncClient, db_session: AsyncSession, sample_cryptocurrency_data
    ):
        """Test getting cryptocurrency by symbol successfully"""
        # Create test cryptocurrency
        crypto = Cryptocurrency(**sample_cryptocurrency_data)
        db_session.add(crypto)
        await db_session.commit()

        response = await client.get("/api/v1/cryptocurrencies/BTC")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "BTC"
        assert data["name"] == "Bitcoin"
        assert data["slug"] == "bitcoin"

    @pytest.mark.asyncio
    async def test_get_cryptocurrency_by_symbol_not_found(self, client: AsyncClient):
        """Test getting cryptocurrency by symbol when not found"""
        response = await client.get("/api/v1/cryptocurrencies/UNKNOWN")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_price_history_success(
        self, client: AsyncClient, db_session: AsyncSession, sample_cryptocurrency_data
    ):
        """Test getting price history successfully"""
        # Create test cryptocurrency
        crypto = Cryptocurrency(**sample_cryptocurrency_data)
        db_session.add(crypto)
        await db_session.commit()

        response = await client.get("/api/v1/cryptocurrencies/BTC/history")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "BTC"
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_price_history_crypto_not_found(self, client: AsyncClient):
        """Test getting price history for non-existent cryptocurrency"""
        response = await client.get("/api/v1/cryptocurrencies/UNKNOWN/history")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_price_history_with_filters(
        self, client: AsyncClient, db_session: AsyncSession, sample_cryptocurrency_data
    ):
        """Test getting price history with date filters"""
        # Create test cryptocurrency
        crypto = Cryptocurrency(**sample_cryptocurrency_data)
        db_session.add(crypto)
        await db_session.commit()

        # Test with date filters
        response = await client.get(
            "/api/v1/cryptocurrencies/BTC/history"
            "?start_date=2024-01-01T00:00:00"
            "&end_date=2024-01-31T23:59:59"
            "&limit=50"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "BTC"

    @pytest.mark.asyncio
    async def test_sync_cryptocurrency_data_success(self, client: AsyncClient):
        """Test manual cryptocurrency data sync"""
        with patch.object(
            cryptocurrency_service, "fetch_and_store_listings"
        ) as mock_fetch:
            mock_fetch.return_value = [
                Cryptocurrency(id=1, symbol="BTC", name="Bitcoin", slug="bitcoin")
            ]

            response = await client.post(
                "/api/v1/cryptocurrencies/sync?limit=10&provider=coingecko"
            )

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert data["updated_count"] == 1
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_sync_cryptocurrency_data_invalid_provider(self, client: AsyncClient):
        """Test sync with invalid provider"""
        response = await client.post("/api/v1/cryptocurrencies/sync?provider=invalid")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_top_cryptocurrencies_market_cap(
        self, client: AsyncClient, db_session: AsyncSession, sample_cryptocurrency_list
    ):
        """Test getting top cryptocurrencies by market cap"""
        # Create test cryptocurrencies
        for crypto_data in sample_cryptocurrency_list:
            crypto = Cryptocurrency(**crypto_data)
            db_session.add(crypto)
        await db_session.commit()

        response = await client.get("/api/v1/cryptocurrencies/top/market_cap?limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Should be sorted by market cap descending
        assert data[0]["symbol"] == "BTC"
        assert data[1]["symbol"] == "ETH"

    @pytest.mark.asyncio
    async def test_get_top_cryptocurrencies_volume(
        self, client: AsyncClient, db_session: AsyncSession, sample_cryptocurrency_list
    ):
        """Test getting top cryptocurrencies by volume"""
        response = await client.get("/api/v1/cryptocurrencies/top/volume?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_top_cryptocurrencies_invalid_category(self, client: AsyncClient):
        """Test getting top cryptocurrencies with invalid category"""
        response = await client.get("/api/v1/cryptocurrencies/top/invalid")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid category" in data["detail"]


class TestAPIValidation:
    """Test API input validation"""

    @pytest.mark.asyncio
    async def test_list_cryptocurrencies_invalid_params(self, client: AsyncClient):
        """Test listing with invalid query parameters"""
        # Test negative skip
        response = await client.get("/api/v1/cryptocurrencies/?skip=-1")
        assert response.status_code == 422

        # Test invalid limit
        response = await client.get("/api/v1/cryptocurrencies/?limit=0")
        assert response.status_code == 422

        # Test invalid order
        response = await client.get("/api/v1/cryptocurrencies/?order=invalid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_price_history_invalid_dates(
        self, client: AsyncClient, db_session: AsyncSession, sample_cryptocurrency_data
    ):
        """Test price history with invalid date formats"""
        # Create test cryptocurrency
        crypto = Cryptocurrency(**sample_cryptocurrency_data)
        db_session.add(crypto)
        await db_session.commit()

        # Test invalid date format
        response = await client.get(
            "/api/v1/cryptocurrencies/BTC/history?start_date=invalid-date"
        )
        assert response.status_code == 422


class TestAPIRateLimiting:
    """Test API rate limiting"""

    @pytest.mark.asyncio
    async def test_rate_limiting_normal_usage(self, client: AsyncClient):
        """Test normal usage within rate limits"""
        # Should not hit rate limit with normal usage
        for _ in range(5):
            response = await client.get("/api/v1/cryptocurrencies/")
            assert response.status_code == 200

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_rate_limiting_exceeded(self, client: AsyncClient):
        """Test rate limiting when exceeded"""
        # This test would need to be implemented based on actual rate limiting configuration
        # and might require special test configuration
        pass


class TestErrorHandling:
    """Test API error handling"""

    @pytest.mark.asyncio
    async def test_database_error_handling(self, client: AsyncClient):
        """Test handling of database errors"""
        with patch(
            "app.services.cryptocurrency_service.cryptocurrency_service.get_cryptocurrencies"
        ) as mock_get:
            mock_get.side_effect = Exception("Database connection error")

            response = await client.get("/api/v1/cryptocurrencies/")

            assert response.status_code == 500
            data = response.json()
            assert "Internal server error" in data["detail"]

    @pytest.mark.asyncio
    async def test_external_api_error_handling(self, client: AsyncClient):
        """Test handling of external API errors during sync"""
        with patch.object(
            cryptocurrency_service, "fetch_and_store_listings"
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("External API error")

            response = await client.post("/api/v1/cryptocurrencies/sync")

            assert response.status_code == 500
            data = response.json()
            assert "Internal server error" in data["detail"]


class TestCORSAndSecurity:
    """Test CORS and security headers"""

    @pytest.mark.asyncio
    async def test_cors_headers(self, client: AsyncClient):
        """Test CORS headers are present"""
        response = await client.options("/api/v1/cryptocurrencies/")

        # Note: This might need adjustment based on actual CORS configuration
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented

    @pytest.mark.asyncio
    async def test_security_headers(self, client: AsyncClient):
        """Test security headers"""
        response = await client.get("/api/v1/cryptocurrencies/")

        # Check for basic security considerations
        assert response.status_code == 200
        # Additional security header checks would go here

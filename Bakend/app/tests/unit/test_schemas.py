import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError

from app.schemas.cryptocurrency import (
    CryptocurrencyBase,
    CryptocurrencyCreate,
    CryptocurrencyUpdate,
    Cryptocurrency,
    CryptocurrencyList,
    PriceHistory,
    CryptocurrencyQueryParams,
    ErrorResponse,
)


class TestCryptocurrencySchemas:
    """Test cases for cryptocurrency Pydantic schemas"""

    def test_cryptocurrency_base_valid(self):
        """Test valid CryptocurrencyBase creation"""
        data = {"symbol": "BTC", "name": "Bitcoin", "slug": "bitcoin"}

        crypto = CryptocurrencyBase(**data)

        assert crypto.symbol == "BTC"
        assert crypto.name == "Bitcoin"
        assert crypto.slug == "bitcoin"

    def test_cryptocurrency_base_missing_required(self):
        """Test CryptocurrencyBase with missing required fields"""
        data = {
            "symbol": "BTC"
            # Missing name and slug
        }

        with pytest.raises(ValidationError) as exc_info:
            CryptocurrencyBase(**data)

        errors = exc_info.value.errors()
        error_fields = [error["loc"][0] for error in errors]
        assert "name" in error_fields
        assert "slug" in error_fields

    def test_cryptocurrency_create_with_optional_fields(self):
        """Test CryptocurrencyCreate with optional fields"""
        data = {
            "symbol": "BTC",
            "name": "Bitcoin",
            "slug": "bitcoin",
            "current_price": "45000.50",
            "market_cap": "850000000000.75",
            "market_cap_rank": 1,
            "description": "Digital currency",
            "website": "https://bitcoin.org",
        }

        crypto = CryptocurrencyCreate(**data)

        assert crypto.current_price == Decimal("45000.50")
        assert crypto.market_cap == Decimal("850000000000.75")
        assert crypto.market_cap_rank == 1
        assert crypto.description == "Digital currency"
        assert crypto.website == "https://bitcoin.org"

    def test_cryptocurrency_create_none_values(self):
        """Test CryptocurrencyCreate with None values for optional fields"""
        data = {
            "symbol": "BTC",
            "name": "Bitcoin",
            "slug": "bitcoin",
            "current_price": None,
            "market_cap": None,
        }

        crypto = CryptocurrencyCreate(**data)

        assert crypto.current_price is None
        assert crypto.market_cap is None

    def test_cryptocurrency_update_partial(self):
        """Test CryptocurrencyUpdate with partial data"""
        data = {"current_price": "46000.00", "market_cap_rank": 2}

        crypto_update = CryptocurrencyUpdate(**data)

        assert crypto_update.current_price == Decimal("46000.00")
        assert crypto_update.market_cap_rank == 2
        assert crypto_update.name is None  # Not provided

    def test_cryptocurrency_full_schema(self):
        """Test full Cryptocurrency schema"""
        data = {
            "id": 1,
            "symbol": "BTC",
            "name": "Bitcoin",
            "slug": "bitcoin",
            "current_price": "45000.00",
            "market_cap": "850000000000",
            "market_cap_rank": 1,
            "total_volume": "25000000000",
            "price_change_percentage_24h": "2.75",
            "ath": "69000.00",
            "ath_date": "2021-11-10T14:24:11.849000",
            "is_active": True,
            "last_updated": "2024-01-01T12:00:00",
            "created_at": "2024-01-01T10:00:00",
        }

        crypto = Cryptocurrency(**data)

        assert crypto.id == 1
        assert crypto.symbol == "BTC"
        assert crypto.current_price == Decimal("45000.00")
        assert crypto.price_change_percentage_24h == Decimal("2.75")
        assert crypto.is_active is True
        assert isinstance(crypto.last_updated, datetime)

    def test_cryptocurrency_list_schema(self):
        """Test CryptocurrencyList schema"""
        crypto_data = {
            "id": 1,
            "symbol": "BTC",
            "name": "Bitcoin",
            "slug": "bitcoin",
            "is_active": True,
            "last_updated": "2024-01-01T12:00:00",
            "created_at": "2024-01-01T10:00:00",
        }

        data = {
            "items": [crypto_data],
            "total": 1,
            "page": 1,
            "per_page": 100,
            "has_next": False,
            "has_prev": False,
        }

        crypto_list = CryptocurrencyList(**data)

        assert len(crypto_list.items) == 1
        assert crypto_list.total == 1
        assert crypto_list.page == 1
        assert crypto_list.has_next is False

    def test_price_history_schema(self):
        """Test PriceHistory schema"""
        data = {
            "id": 1,
            "cryptocurrency_id": 1,
            "symbol": "BTC",
            "price": "45000.00",
            "market_cap": "850000000000",
            "total_volume": "25000000000",
            "timestamp": "2024-01-01T12:00:00",
            "created_at": "2024-01-01T12:00:00",
        }

        price_history = PriceHistory(**data)

        assert price_history.id == 1
        assert price_history.symbol == "BTC"
        assert price_history.price == Decimal("45000.00")
        assert isinstance(price_history.timestamp, datetime)

    def test_cryptocurrency_query_params_defaults(self):
        """Test CryptocurrencyQueryParams with default values"""
        params = CryptocurrencyQueryParams()

        assert params.skip == 0
        assert params.limit == 100
        assert params.sort_by == "market_cap_rank"
        assert params.order == "asc"
        assert params.symbol_filter is None

    def test_cryptocurrency_query_params_validation(self):
        """Test CryptocurrencyQueryParams validation"""
        # Test valid params
        valid_data = {
            "skip": 10,
            "limit": 50,
            "sort_by": "market_cap",
            "order": "desc",
            "symbol_filter": "BTC",
            "min_market_cap": 1000000000,
        }

        params = CryptocurrencyQueryParams(**valid_data)

        assert params.skip == 10
        assert params.limit == 50
        assert params.order == "desc"
        assert params.min_market_cap == 1000000000

    def test_cryptocurrency_query_params_invalid_order(self):
        """Test CryptocurrencyQueryParams with invalid order"""
        data = {"order": "invalid"}

        with pytest.raises(ValidationError) as exc_info:
            CryptocurrencyQueryParams(**data)

        errors = exc_info.value.errors()
        assert any("order" in str(error) for error in errors)

    def test_cryptocurrency_query_params_negative_values(self):
        """Test CryptocurrencyQueryParams with negative values"""
        data = {"skip": -1, "limit": 0, "min_market_cap": -100}

        with pytest.raises(ValidationError) as exc_info:
            CryptocurrencyQueryParams(**data)

        errors = exc_info.value.errors()
        error_fields = [error["loc"][0] for error in errors]
        assert "skip" in error_fields
        assert "limit" in error_fields
        assert "min_market_cap" in error_fields

    def test_error_response_schema(self):
        """Test ErrorResponse schema"""
        data = {
            "detail": "Cryptocurrency not found",
            "errors": [
                {
                    "type": "not_found",
                    "msg": "Symbol 'UNKNOWN' not found",
                    "input": "UNKNOWN",
                }
            ],
        }

        error_response = ErrorResponse(**data)

        assert error_response.detail == "Cryptocurrency not found"
        assert len(error_response.errors) == 1
        assert error_response.errors[0].type == "not_found"


class TestSchemaFieldValidation:
    """Test specific field validation in schemas"""

    def test_decimal_field_conversion(self):
        """Test automatic conversion to Decimal"""
        data = {
            "symbol": "BTC",
            "name": "Bitcoin",
            "slug": "bitcoin",
            "current_price": 45000,  # Integer
            "market_cap": "850000000000.50",  # String
        }

        crypto = CryptocurrencyCreate(**data)

        assert crypto.current_price == Decimal("45000")
        assert crypto.market_cap == Decimal("850000000000.50")

    def test_datetime_field_parsing(self):
        """Test datetime field parsing"""
        data = {
            "id": 1,
            "symbol": "BTC",
            "name": "Bitcoin",
            "slug": "bitcoin",
            "is_active": True,
            "last_updated": "2024-01-01T12:00:00.000Z",
            "created_at": datetime(2024, 1, 1, 10, 0, 0),
        }

        crypto = Cryptocurrency(**data)

        assert isinstance(crypto.last_updated, datetime)
        assert isinstance(crypto.created_at, datetime)

    def test_boolean_field_validation(self):
        """Test boolean field validation"""
        data = {"is_active": "true"}  # String should be converted

        crypto_update = CryptocurrencyUpdate(**data)

        assert crypto_update.is_active is True

    def test_string_field_trimming(self):
        """Test string field handling"""
        data = {"symbol": " BTC ", "name": " Bitcoin ", "slug": " bitcoin "}

        crypto = CryptocurrencyBase(**data)

        # Note: Pydantic doesn't auto-trim by default
        # This test shows current behavior
        assert crypto.symbol == " BTC "
        assert crypto.name == " Bitcoin "

    def test_url_field_validation(self):
        """Test URL field validation"""
        data = {
            "symbol": "BTC",
            "name": "Bitcoin",
            "slug": "bitcoin",
            "website": "https://bitcoin.org",
            "whitepaper": "https://bitcoin.org/bitcoin.pdf",
            "image_url": "https://bitcoin.org/img/logo.png",
        }

        crypto = CryptocurrencyCreate(**data)

        assert crypto.website == "https://bitcoin.org"
        assert crypto.whitepaper == "https://bitcoin.org/bitcoin.pdf"
        assert crypto.image_url == "https://bitcoin.org/img/logo.png"

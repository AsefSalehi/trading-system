from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CryptocurrencyBase(BaseModel):
    """Base schema for cryptocurrency data"""
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC)")
    name: str = Field(..., description="Full name of the cryptocurrency")
    slug: str = Field(..., description="URL-friendly identifier")


class CryptocurrencyCreate(CryptocurrencyBase):
    """Schema for creating a cryptocurrency"""
    current_price: Optional[Decimal] = Field(None, description="Current price in USD")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    market_cap_rank: Optional[int] = Field(None, description="Market cap ranking")
    total_volume: Optional[Decimal] = Field(None, description="24h trading volume")
    circulating_supply: Optional[Decimal] = Field(None, description="Circulating supply")
    total_supply: Optional[Decimal] = Field(None, description="Total supply")
    max_supply: Optional[Decimal] = Field(None, description="Maximum supply")
    description: Optional[str] = Field(None, description="Cryptocurrency description")
    website: Optional[str] = Field(None, description="Official website URL")
    whitepaper: Optional[str] = Field(None, description="Whitepaper URL")
    image_url: Optional[str] = Field(None, description="Logo image URL")


class CryptocurrencyUpdate(BaseModel):
    """Schema for updating a cryptocurrency"""
    name: Optional[str] = None
    current_price: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    market_cap_rank: Optional[int] = None
    total_volume: Optional[Decimal] = None
    circulating_supply: Optional[Decimal] = None
    total_supply: Optional[Decimal] = None
    max_supply: Optional[Decimal] = None
    description: Optional[str] = None
    website: Optional[str] = None
    whitepaper: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class Cryptocurrency(CryptocurrencyBase):
    """Complete cryptocurrency schema for API responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Unique identifier")
    current_price: Optional[Decimal] = Field(None, description="Current price in USD")
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    market_cap_rank: Optional[int] = Field(None, description="Market cap ranking")
    total_volume: Optional[Decimal] = Field(None, description="24h trading volume")
    circulating_supply: Optional[Decimal] = Field(None, description="Circulating supply")
    total_supply: Optional[Decimal] = Field(None, description="Total supply")
    max_supply: Optional[Decimal] = Field(None, description="Maximum supply")
    
    # Price changes
    price_change_24h: Optional[Decimal] = Field(None, description="24h price change")
    price_change_percentage_24h: Optional[Decimal] = Field(None, description="24h price change percentage")
    price_change_percentage_7d: Optional[Decimal] = Field(None, description="7d price change percentage")
    price_change_percentage_30d: Optional[Decimal] = Field(None, description="30d price change percentage")
    
    # All-time highs and lows
    ath: Optional[Decimal] = Field(None, description="All-time high price")
    ath_date: Optional[datetime] = Field(None, description="All-time high date")
    atl: Optional[Decimal] = Field(None, description="All-time low price")
    atl_date: Optional[datetime] = Field(None, description="All-time low date")
    
    # Metadata
    description: Optional[str] = Field(None, description="Cryptocurrency description")
    website: Optional[str] = Field(None, description="Official website URL")
    whitepaper: Optional[str] = Field(None, description="Whitepaper URL")
    image_url: Optional[str] = Field(None, description="Logo image URL")
    
    # Status and timestamps
    is_active: bool = Field(..., description="Whether the cryptocurrency is active")
    last_updated: datetime = Field(..., description="Last update timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")


class CryptocurrencyList(BaseModel):
    """Schema for paginated cryptocurrency listings"""
    items: List[Cryptocurrency] = Field(..., description="List of cryptocurrencies")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


class PriceHistoryBase(BaseModel):
    """Base schema for price history"""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    price: Decimal = Field(..., description="Price at the time")
    timestamp: datetime = Field(..., description="Timestamp of the price record")


class PriceHistory(PriceHistoryBase):
    """Complete price history schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Unique identifier")
    cryptocurrency_id: int = Field(..., description="Associated cryptocurrency ID")
    market_cap: Optional[Decimal] = Field(None, description="Market cap at the time")
    total_volume: Optional[Decimal] = Field(None, description="Trading volume at the time")
    created_at: datetime = Field(..., description="Record creation timestamp")


class PriceHistoryList(BaseModel):
    """Schema for price history listings"""
    symbol: str = Field(..., description="Cryptocurrency symbol")
    items: List[PriceHistory] = Field(..., description="List of price history records")
    total: int = Field(..., description="Total number of records")


# Query parameter schemas
class CryptocurrencyQueryParams(BaseModel):
    """Query parameters for cryptocurrency listings"""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")
    sort_by: str = Field("market_cap_rank", description="Field to sort by")
    order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")
    symbol_filter: Optional[str] = Field(None, description="Filter by symbol (partial match)")
    min_market_cap: Optional[float] = Field(None, ge=0, description="Minimum market cap filter")
    max_market_cap: Optional[float] = Field(None, ge=0, description="Maximum market cap filter")
    min_volume: Optional[float] = Field(None, ge=0, description="Minimum volume filter")


class PriceHistoryQueryParams(BaseModel):
    """Query parameters for price history"""
    start_date: Optional[datetime] = Field(None, description="Start date for price history")
    end_date: Optional[datetime] = Field(None, description="End date for price history")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")


# Error schemas
class ErrorDetail(BaseModel):
    """Error detail schema"""
    type: str = Field(..., description="Error type")
    msg: str = Field(..., description="Error message")
    input: Optional[str] = Field(None, description="Invalid input")


class ErrorResponse(BaseModel):
    """API error response schema"""
    detail: str = Field(..., description="Error description")
    errors: Optional[List[ErrorDetail]] = Field(None, description="Validation errors")


# Success response schemas
class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str = Field(..., description="Success message")
    data: Optional[dict] = Field(None, description="Additional data")


class DataUpdateResponse(BaseModel):
    """Response for data update operations"""
    message: str = Field(..., description="Operation result message")
    updated_count: int = Field(..., description="Number of records updated")
    created_count: int = Field(..., description="Number of records created")
    timestamp: datetime = Field(..., description="Operation timestamp")
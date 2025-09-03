"""
Multi-Exchange Support & Arbitrage Detection Service
Production-grade multi-exchange integration with arbitrage opportunities
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json

from app.core.logging import logger
from app.core.config import settings


@dataclass
class ExchangePrice:
    """Price data from an exchange"""
    exchange: str
    symbol: str
    bid: Decimal
    ask: Decimal
    last_price: Decimal
    volume_24h: Decimal
    timestamp: datetime
    
    def to_dict(self):
        return {
            "exchange": self.exchange,
            "symbol": self.symbol,
            "bid": float(self.bid),
            "ask": float(self.ask),
            "last_price": float(self.last_price),
            "volume_24h": float(self.volume_24h),
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity between exchanges"""
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: Decimal
    sell_price: Decimal
    profit_percentage: Decimal
    profit_amount: Decimal  # Per unit
    max_volume: Decimal
    timestamp: datetime
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "buy_exchange": self.buy_exchange,
            "sell_exchange": self.sell_exchange,
            "buy_price": float(self.buy_price),
            "sell_price": float(self.sell_price),
            "profit_percentage": float(self.profit_percentage),
            "profit_amount": float(self.profit_amount),
            "max_volume": float(self.max_volume),
            "timestamp": self.timestamp.isoformat()
        }


class ExchangeConnector(ABC):
    """Abstract base class for exchange connectors"""
    
    def __init__(self, name: str):
        self.name = name
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Optional[ExchangePrice]:
        """Get ticker data for symbol"""
        pass
    
    @abstractmethod
    async def get_order_book(self, symbol: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Get order book data"""
        pass
    
    @abstractmethod
    def normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to exchange format"""
        pass


class BinanceConnector(ExchangeConnector):
    """Binance exchange connector"""
    
    def __init__(self):
        super().__init__("Binance")
        self.base_url = "https://api.binance.com/api/v3"
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert symbol to Binance format (e.g., BTC -> BTCUSDT)"""
        return f"{symbol}USDT"
    
    async def get_ticker(self, symbol: str) -> Optional[ExchangePrice]:
        """Get ticker from Binance"""
        try:
            binance_symbol = self.normalize_symbol(symbol)
            
            # Get 24hr ticker statistics
            ticker_url = f"{self.base_url}/ticker/24hr"
            params = {"symbol": binance_symbol}
            
            async with self.session.get(ticker_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return ExchangePrice(
                        exchange=self.name,
                        symbol=symbol,
                        bid=Decimal(data["bidPrice"]),
                        ask=Decimal(data["askPrice"]),
                        last_price=Decimal(data["lastPrice"]),
                        volume_24h=Decimal(data["volume"]),
                        timestamp=datetime.utcnow()
                    )
                else:
                    logger.warning(f"Binance API error for {symbol}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Binance ticker for {symbol}: {e}")
            return None
    
    async def get_order_book(self, symbol: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Get order book from Binance"""
        try:
            binance_symbol = self.normalize_symbol(symbol)
            
            url = f"{self.base_url}/depth"
            params = {"symbol": binance_symbol, "limit": limit}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "exchange": self.name,
                        "symbol": symbol,
                        "bids": [[Decimal(price), Decimal(qty)] for price, qty in data["bids"]],
                        "asks": [[Decimal(price), Decimal(qty)] for price, qty in data["asks"]],
                        "timestamp": datetime.utcnow()
                    }
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Binance order book for {symbol}: {e}")
            return None


class CoinbaseConnector(ExchangeConnector):
    """Coinbase Pro exchange connector"""
    
    def __init__(self):
        super().__init__("Coinbase")
        self.base_url = "https://api.exchange.coinbase.com"
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert symbol to Coinbase format (e.g., BTC -> BTC-USD)"""
        return f"{symbol}-USD"
    
    async def get_ticker(self, symbol: str) -> Optional[ExchangePrice]:
        """Get ticker from Coinbase"""
        try:
            coinbase_symbol = self.normalize_symbol(symbol)
            
            # Get ticker
            ticker_url = f"{self.base_url}/products/{coinbase_symbol}/ticker"
            
            async with self.session.get(ticker_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Get 24hr stats
                    stats_url = f"{self.base_url}/products/{coinbase_symbol}/stats"
                    async with self.session.get(stats_url) as stats_response:
                        if stats_response.status == 200:
                            stats_data = await stats_response.json()
                            volume_24h = Decimal(stats_data.get("volume", "0"))
                        else:
                            volume_24h = Decimal("0")
                    
                    return ExchangePrice(
                        exchange=self.name,
                        symbol=symbol,
                        bid=Decimal(data["bid"]),
                        ask=Decimal(data["ask"]),
                        last_price=Decimal(data["price"]),
                        volume_24h=volume_24h,
                        timestamp=datetime.utcnow()
                    )
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Coinbase ticker for {symbol}: {e}")
            return None
    
    async def get_order_book(self, symbol: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Get order book from Coinbase"""
        try:
            coinbase_symbol = self.normalize_symbol(symbol)
            
            url = f"{self.base_url}/products/{coinbase_symbol}/book"
            params = {"level": 2}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Limit the results
                    bids = [[Decimal(price), Decimal(qty)] for price, qty, _ in data["bids"][:limit]]
                    asks = [[Decimal(price), Decimal(qty)] for price, qty, _ in data["asks"][:limit]]
                    
                    return {
                        "exchange": self.name,
                        "symbol": symbol,
                        "bids": bids,
                        "asks": asks,
                        "timestamp": datetime.utcnow()
                    }
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Coinbase order book for {symbol}: {e}")
            return None


class KrakenConnector(ExchangeConnector):
    """Kraken exchange connector"""
    
    def __init__(self):
        super().__init__("Kraken")
        self.base_url = "https://api.kraken.com/0/public"
        # Kraken symbol mapping
        self.symbol_map = {
            "BTC": "XBTUSD",
            "ETH": "ETHUSD",
            "ADA": "ADAUSD",
            "DOT": "DOTUSD",
            "SOL": "SOLUSD"
        }
    
    def normalize_symbol(self, symbol: str) -> str:
        """Convert symbol to Kraken format"""
        return self.symbol_map.get(symbol, f"{symbol}USD")
    
    async def get_ticker(self, symbol: str) -> Optional[ExchangePrice]:
        """Get ticker from Kraken"""
        try:
            kraken_symbol = self.normalize_symbol(symbol)
            
            url = f"{self.base_url}/Ticker"
            params = {"pair": kraken_symbol}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("error"):
                        logger.warning(f"Kraken API error for {symbol}: {data['error']}")
                        return None
                    
                    ticker_data = data["result"][kraken_symbol]
                    
                    return ExchangePrice(
                        exchange=self.name,
                        symbol=symbol,
                        bid=Decimal(ticker_data["b"][0]),  # Best bid price
                        ask=Decimal(ticker_data["a"][0]),  # Best ask price
                        last_price=Decimal(ticker_data["c"][0]),  # Last trade price
                        volume_24h=Decimal(ticker_data["v"][1]),  # 24h volume
                        timestamp=datetime.utcnow()
                    )
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Kraken ticker for {symbol}: {e}")
            return None
    
    async def get_order_book(self, symbol: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Get order book from Kraken"""
        try:
            kraken_symbol = self.normalize_symbol(symbol)
            
            url = f"{self.base_url}/Depth"
            params = {"pair": kraken_symbol, "count": limit}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("error"):
                        return None
                    
                    book_data = data["result"][kraken_symbol]
                    
                    bids = [[Decimal(price), Decimal(qty)] for price, qty, _ in book_data["bids"]]
                    asks = [[Decimal(price), Decimal(qty)] for price, qty, _ in book_data["asks"]]
                    
                    return {
                        "exchange": self.name,
                        "symbol": symbol,
                        "bids": bids,
                        "asks": asks,
                        "timestamp": datetime.utcnow()
                    }
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching Kraken order book for {symbol}: {e}")
            return None


class MultiExchangeService:
    """Multi-exchange service with arbitrage detection"""
    
    def __init__(self):
        self.exchanges = {
            "Binance": BinanceConnector(),
            "Coinbase": CoinbaseConnector(),
            "Kraken": KrakenConnector()
        }
        self.price_cache: Dict[str, Dict[str, ExchangePrice]] = {}
        self.arbitrage_opportunities: List[ArbitrageOpportunity] = []
        self.min_profit_percentage = Decimal("0.5")  # Minimum 0.5% profit for arbitrage
        self.is_running = False
    
    async def start_monitoring(self):
        """Start multi-exchange monitoring"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting multi-exchange monitoring")
        
        # Start background tasks
        asyncio.create_task(self.price_monitoring_loop())
        asyncio.create_task(self.arbitrage_detection_loop())
    
    def stop_monitoring(self):
        """Stop multi-exchange monitoring"""
        self.is_running = False
        logger.info("Stopping multi-exchange monitoring")
    
    async def price_monitoring_loop(self):
        """Monitor prices across all exchanges"""
        symbols = ["BTC", "ETH", "ADA", "SOL", "DOT"]
        
        while self.is_running:
            try:
                await self.update_all_prices(symbols)
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Error in price monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def arbitrage_detection_loop(self):
        """Detect arbitrage opportunities"""
        while self.is_running:
            try:
                await self.detect_arbitrage_opportunities()
                await asyncio.sleep(3)  # Check every 3 seconds
            except Exception as e:
                logger.error(f"Error in arbitrage detection loop: {e}")
                await asyncio.sleep(5)
    
    async def update_all_prices(self, symbols: List[str]):
        """Update prices for all symbols across all exchanges"""
        tasks = []
        
        for exchange_name, connector in self.exchanges.items():
            for symbol in symbols:
                tasks.append(self.fetch_price_safe(connector, symbol))
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, ExchangePrice):
                if result.symbol not in self.price_cache:
                    self.price_cache[result.symbol] = {}
                self.price_cache[result.symbol][result.exchange] = result
    
    async def fetch_price_safe(self, connector: ExchangeConnector, symbol: str) -> Optional[ExchangePrice]:
        """Safely fetch price from exchange"""
        try:
            async with connector:
                return await connector.get_ticker(symbol)
        except Exception as e:
            logger.error(f"Error fetching price from {connector.name} for {symbol}: {e}")
            return None
    
    async def detect_arbitrage_opportunities(self):
        """Detect arbitrage opportunities across exchanges"""
        opportunities = []
        
        for symbol, exchange_prices in self.price_cache.items():
            if len(exchange_prices) < 2:
                continue  # Need at least 2 exchanges
            
            # Find best buy and sell prices
            best_buy = None  # Lowest ask price (where we can buy)
            best_sell = None  # Highest bid price (where we can sell)
            
            for exchange, price_data in exchange_prices.items():
                # Check if data is recent (within last 30 seconds)
                if (datetime.utcnow() - price_data.timestamp).seconds > 30:
                    continue
                
                if best_buy is None or price_data.ask < best_buy[1]:
                    best_buy = (exchange, price_data.ask)
                
                if best_sell is None or price_data.bid > best_sell[1]:
                    best_sell = (exchange, price_data.bid)
            
            # Check if arbitrage opportunity exists
            if (best_buy and best_sell and 
                best_buy[0] != best_sell[0] and  # Different exchanges
                best_sell[1] > best_buy[1]):     # Profit possible
                
                profit_amount = best_sell[1] - best_buy[1]
                profit_percentage = (profit_amount / best_buy[1]) * 100
                
                if profit_percentage >= self.min_profit_percentage:
                    # Calculate maximum volume (simplified)
                    max_volume = min(
                        exchange_prices[best_buy[0]].volume_24h * Decimal("0.01"),  # 1% of daily volume
                        exchange_prices[best_sell[0]].volume_24h * Decimal("0.01")
                    )
                    
                    opportunity = ArbitrageOpportunity(
                        symbol=symbol,
                        buy_exchange=best_buy[0],
                        sell_exchange=best_sell[0],
                        buy_price=best_buy[1],
                        sell_price=best_sell[1],
                        profit_percentage=profit_percentage,
                        profit_amount=profit_amount,
                        max_volume=max_volume,
                        timestamp=datetime.utcnow()
                    )
                    
                    opportunities.append(opportunity)
        
        # Update opportunities list
        self.arbitrage_opportunities = opportunities
        
        if opportunities:
            logger.info(f"Found {len(opportunities)} arbitrage opportunities")
            for opp in opportunities[:3]:  # Log top 3
                logger.info(f"Arbitrage: {opp.symbol} - Buy on {opp.buy_exchange} at ${opp.buy_price}, "
                          f"Sell on {opp.sell_exchange} at ${opp.sell_price} "
                          f"({opp.profit_percentage:.2f}% profit)")
    
    async def get_best_price(self, symbol: str, side: str) -> Optional[Tuple[str, Decimal]]:
        """Get best price across all exchanges"""
        if symbol not in self.price_cache:
            return None
        
        best_exchange = None
        best_price = None
        
        for exchange, price_data in self.price_cache[symbol].items():
            # Check if data is recent
            if (datetime.utcnow() - price_data.timestamp).seconds > 30:
                continue
            
            if side == "buy":  # Looking for lowest ask
                if best_price is None or price_data.ask < best_price:
                    best_price = price_data.ask
                    best_exchange = exchange
            else:  # Looking for highest bid
                if best_price is None or price_data.bid > best_price:
                    best_price = price_data.bid
                    best_exchange = exchange
        
        return (best_exchange, best_price) if best_exchange else None
    
    def get_arbitrage_opportunities(self, min_profit: Optional[Decimal] = None) -> List[ArbitrageOpportunity]:
        """Get current arbitrage opportunities"""
        if min_profit is None:
            return self.arbitrage_opportunities
        
        return [opp for opp in self.arbitrage_opportunities if opp.profit_percentage >= min_profit]
    
    def get_exchange_prices(self, symbol: str) -> Dict[str, ExchangePrice]:
        """Get prices from all exchanges for a symbol"""
        return self.price_cache.get(symbol, {})
    
    async def get_order_books(self, symbol: str) -> Dict[str, Dict[str, Any]]:
        """Get order books from all exchanges"""
        order_books = {}
        tasks = []
        
        for exchange_name, connector in self.exchanges.items():
            tasks.append(self.fetch_order_book_safe(connector, symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, dict):
                exchange_name = list(self.exchanges.keys())[i]
                order_books[exchange_name] = result
        
        return order_books
    
    async def fetch_order_book_safe(self, connector: ExchangeConnector, symbol: str) -> Optional[Dict[str, Any]]:
        """Safely fetch order book from exchange"""
        try:
            async with connector:
                return await connector.get_order_book(symbol)
        except Exception as e:
            logger.error(f"Error fetching order book from {connector.name} for {symbol}: {e}")
            return None
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get market summary across all exchanges"""
        summary = {
            "exchanges": list(self.exchanges.keys()),
            "symbols_tracked": list(self.price_cache.keys()),
            "arbitrage_opportunities": len(self.arbitrage_opportunities),
            "best_opportunities": [opp.to_dict() for opp in self.arbitrage_opportunities[:5]],
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return summary


# Global multi-exchange service instance
multi_exchange_service = MultiExchangeService()
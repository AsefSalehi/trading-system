"""
Real-time Trading Features Service
WebSocket feeds, live order book, and real-time alerts
"""

import asyncio
import json
import websockets
from typing import Dict, List, Optional, Set, Any, Callable
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

from app.core.logging import logger
from app.core.config import settings


@dataclass
class PriceUpdate:
    """Real-time price update"""
    symbol: str
    price: Decimal
    volume_24h: Decimal
    change_24h: Decimal
    timestamp: datetime

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "price": float(self.price),
            "volume_24h": float(self.volume_24h),
            "change_24h": float(self.change_24h),
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class OrderBookEntry:
    """Order book entry"""
    price: Decimal
    quantity: Decimal

    def to_dict(self):
        return {
            "price": float(self.price),
            "quantity": float(self.quantity)
        }


@dataclass
class OrderBook:
    """Live order book"""
    symbol: str
    bids: List[OrderBookEntry]  # Buy orders (highest price first)
    asks: List[OrderBookEntry]  # Sell orders (lowest price first)
    timestamp: datetime

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "bids": [bid.to_dict() for bid in self.bids],
            "asks": [ask.to_dict() for ask in self.asks],
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Alert:
    """Real-time alert"""
    id: str
    user_id: int
    alert_type: str  # 'price', 'volume', 'portfolio', 'risk'
    symbol: Optional[str]
    condition: str  # 'above', 'below', 'change'
    threshold: Decimal
    current_value: Decimal
    message: str
    timestamp: datetime

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "alert_type": self.alert_type,
            "symbol": self.symbol,
            "condition": self.condition,
            "threshold": float(self.threshold),
            "current_value": float(self.current_value),
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = defaultdict(set)
        self.user_connections: Dict[int, Set[websockets.WebSocketServerProtocol]] = defaultdict(set)

    async def connect(self, websocket: websockets.WebSocketServerProtocol, user_id: int, channels: List[str]):
        """Register a new WebSocket connection"""
        self.user_connections[user_id].add(websocket)

        for channel in channels:
            self.connections[channel].add(websocket)

        logger.info(f"WebSocket connected for user {user_id}, channels: {channels}")

    async def disconnect(self, websocket: websockets.WebSocketServerProtocol, user_id: int):
        """Unregister a WebSocket connection"""
        self.user_connections[user_id].discard(websocket)

        # Remove from all channels
        for channel_connections in self.connections.values():
            channel_connections.discard(websocket)

        logger.info(f"WebSocket disconnected for user {user_id}")

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """Broadcast message to all connections in a channel"""
        if channel not in self.connections:
            return

        message_str = json.dumps(message)
        disconnected = set()

        for websocket in self.connections[channel]:
            try:
                await websocket.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                disconnected.add(websocket)

        # Clean up disconnected connections
        for websocket in disconnected:
            self.connections[channel].discard(websocket)

    async def send_to_user(self, user_id: int, message: Dict[str, Any]):
        """Send message to specific user"""
        if user_id not in self.user_connections:
            return

        message_str = json.dumps(message)
        disconnected = set()

        for websocket in self.user_connections[user_id]:
            try:
                await websocket.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error sending WebSocket message to user {user_id}: {e}")
                disconnected.add(websocket)

        # Clean up disconnected connections
        for websocket in disconnected:
            self.user_connections[user_id].discard(websocket)


class OrderBookManager:
    """Manages live order books"""

    def __init__(self):
        self.order_books: Dict[str, OrderBook] = {}
        self.max_depth = 20  # Keep top 20 bids/asks

    def update_order_book(self, symbol: str, bids: List[OrderBookEntry], asks: List[OrderBookEntry]):
        """Update order book for symbol"""
        # Sort bids (highest price first) and asks (lowest price first)
        sorted_bids = sorted(bids, key=lambda x: x.price, reverse=True)[:self.max_depth]
        sorted_asks = sorted(asks, key=lambda x: x.price)[:self.max_depth]

        self.order_books[symbol] = OrderBook(
            symbol=symbol,
            bids=sorted_bids,
            asks=sorted_asks,
            timestamp=datetime.utcnow()
        )

    def get_order_book(self, symbol: str) -> Optional[OrderBook]:
        """Get order book for symbol"""
        return self.order_books.get(symbol)

    def get_best_bid_ask(self, symbol: str) -> Optional[Dict[str, Decimal]]:
        """Get best bid and ask prices"""
        order_book = self.order_books.get(symbol)
        if not order_book:
            return None

        best_bid = order_book.bids[0].price if order_book.bids else None
        best_ask = order_book.asks[0].price if order_book.asks else None

        return {
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": (best_ask - best_bid) if (best_bid and best_ask) else None
        }


class AlertManager:
    """Manages real-time alerts"""

    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.user_alerts: Dict[int, List[str]] = defaultdict(list)

    def create_price_alert(self, user_id: int, symbol: str, condition: str,
                          threshold: Decimal) -> str:
        """Create a price alert"""
        alert_id = f"price_{user_id}_{symbol}_{datetime.utcnow().timestamp()}"

        alert = Alert(
            id=alert_id,
            user_id=user_id,
            alert_type="price",
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            current_value=Decimal('0'),  # Will be updated
            message=f"{symbol} price {condition} ${threshold}",
            timestamp=datetime.utcnow()
        )

        self.active_alerts[alert_id] = alert
        self.user_alerts[user_id].append(alert_id)

        logger.info(f"Created price alert: {alert.message}")
        return alert_id

    def create_portfolio_alert(self, user_id: int, condition: str, threshold: Decimal) -> str:
        """Create a portfolio value alert"""
        alert_id = f"portfolio_{user_id}_{datetime.utcnow().timestamp()}"

        alert = Alert(
            id=alert_id,
            user_id=user_id,
            alert_type="portfolio",
            symbol=None,
            condition=condition,
            threshold=threshold,
            current_value=Decimal('0'),
            message=f"Portfolio value {condition} ${threshold}",
            timestamp=datetime.utcnow()
        )

        self.active_alerts[alert_id] = alert
        self.user_alerts[user_id].append(alert_id)

        return alert_id

    def check_price_alerts(self, symbol: str, current_price: Decimal) -> List[Alert]:
        """Check if any price alerts should be triggered"""
        triggered_alerts = []

        for alert in self.active_alerts.values():
            if alert.alert_type == "price" and alert.symbol == symbol:
                alert.current_value = current_price

                should_trigger = False
                if alert.condition == "above" and current_price >= alert.threshold:
                    should_trigger = True
                elif alert.condition == "below" and current_price <= alert.threshold:
                    should_trigger = True
                elif alert.condition == "change":
                    # For change alerts, threshold is percentage change
                    # This would need historical price to calculate
                    pass

                if should_trigger:
                    triggered_alerts.append(alert)

        return triggered_alerts

    def remove_alert(self, alert_id: str) -> bool:
        """Remove an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            del self.active_alerts[alert_id]

            if alert.user_id in self.user_alerts:
                self.user_alerts[alert.user_id].remove(alert_id)

            return True
        return False

    def get_user_alerts(self, user_id: int) -> List[Alert]:
        """Get all alerts for a user"""
        alert_ids = self.user_alerts.get(user_id, [])
        return [self.active_alerts[alert_id] for alert_id in alert_ids if alert_id in self.active_alerts]


class RealTimeService:
    """Main real-time service orchestrator"""

    def __init__(self):
        self.websocket_manager = WebSocketManager()
        self.order_book_manager = OrderBookManager()
        self.alert_manager = AlertManager()
        self.price_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.is_running = False

    async def start(self):
        """Start real-time services"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("Starting real-time services")

        # Start background tasks
        asyncio.create_task(self.price_feed_loop())
        asyncio.create_task(self.order_book_update_loop())
        asyncio.create_task(self.alert_check_loop())

    def stop(self):
        """Stop real-time services"""
        self.is_running = False
        logger.info("Stopping real-time services")

    async def price_feed_loop(self):
        """Main price feed loop"""
        while self.is_running:
            try:
                await self.update_prices()
                await asyncio.sleep(1)  # Update every second
            except Exception as e:
                logger.error(f"Error in price feed loop: {e}")
                await asyncio.sleep(5)

    async def order_book_update_loop(self):
        """Order book update loop"""
        while self.is_running:
            try:
                await self.update_order_books()
                await asyncio.sleep(0.5)  # Update every 500ms
            except Exception as e:
                logger.error(f"Error in order book loop: {e}")
                await asyncio.sleep(2)

    async def alert_check_loop(self):
        """Alert checking loop"""
        while self.is_running:
            try:
                await self.check_alerts()
                await asyncio.sleep(2)  # Check every 2 seconds
            except Exception as e:
                logger.error(f"Error in alert loop: {e}")
                await asyncio.sleep(5)

    async def update_prices(self):
        """Update real-time prices"""
        # Get prices from external APIs
        symbols = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'XRP', 'DOT', 'DOGE', 'AVAX', 'MATIC']

        for symbol in symbols:
            try:
                # Get price from Binance or other source
                price_data = await self.fetch_price_data(symbol)
                if price_data:
                    # Store in history
                    self.price_history[symbol].append(price_data)

                    # Broadcast to WebSocket subscribers
                    await self.websocket_manager.broadcast_to_channel(
                        f"price_{symbol}",
                        {
                            "type": "price_update",
                            "data": price_data.to_dict()
                        }
                    )

                    # Check price alerts
                    triggered_alerts = self.alert_manager.check_price_alerts(symbol, price_data.price)
                    for alert in triggered_alerts:
                        await self.send_alert(alert)
                        self.alert_manager.remove_alert(alert.id)

            except Exception as e:
                logger.error(f"Error updating price for {symbol}: {e}")

    async def update_order_books(self):
        """Update order books"""
        symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'ADA']

        for symbol in symbols:
            try:
                order_book_data = await self.fetch_order_book_data(symbol)
                if order_book_data:
                    self.order_book_manager.update_order_book(
                        symbol, order_book_data['bids'], order_book_data['asks']
                    )

                    # Broadcast to subscribers
                    order_book = self.order_book_manager.get_order_book(symbol)
                    if order_book:
                        await self.websocket_manager.broadcast_to_channel(
                            f"orderbook_{symbol}",
                            {
                                "type": "orderbook_update",
                                "data": order_book.to_dict()
                            }
                        )

            except Exception as e:
                logger.error(f"Error updating order book for {symbol}: {e}")

    async def check_alerts(self):
        """Check and trigger alerts"""
        # This would check portfolio alerts, risk alerts, etc.
        # For now, price alerts are checked in update_prices()
        pass

    async def fetch_price_data(self, symbol: str) -> Optional[PriceUpdate]:
        """Fetch real-time price data"""
        try:
            # In production, this would connect to real WebSocket feeds
            # For now, simulate with API calls
            from app.services.binance_service import binance_service

            price = binance_service.get_current_price(symbol)
            if price:
                return PriceUpdate(
                    symbol=symbol,
                    price=Decimal(str(price)),
                    volume_24h=Decimal('1000000'),  # Mock data
                    change_24h=Decimal('2.5'),      # Mock data
                    timestamp=datetime.utcnow()
                )

            return None

        except Exception as e:
            logger.error(f"Error fetching price data for {symbol}: {e}")
            return None

    async def fetch_order_book_data(self, symbol: str) -> Optional[Dict[str, List[OrderBookEntry]]]:
        """Fetch order book data"""
        try:
            # Mock order book data for demonstration
            # In production, this would come from real exchange APIs
            base_price = await self.get_current_price(symbol)
            if not base_price:
                return None

            bids = []
            asks = []

            # Generate mock order book
            for i in range(10):
                bid_price = base_price * (1 - (i + 1) * Decimal('0.001'))
                ask_price = base_price * (1 + (i + 1) * Decimal('0.001'))

                bids.append(OrderBookEntry(bid_price, Decimal('1.5') + Decimal(str(i * 0.1))))
                asks.append(OrderBookEntry(ask_price, Decimal('1.2') + Decimal(str(i * 0.15))))

            return {"bids": bids, "asks": asks}

        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            return None

    async def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current price for symbol"""
        if symbol in self.price_history and self.price_history[symbol]:
            return self.price_history[symbol][-1].price
        return None

    async def send_alert(self, alert: Alert):
        """Send alert to user"""
        await self.websocket_manager.send_to_user(
            alert.user_id,
            {
                "type": "alert",
                "data": alert.to_dict()
            }
        )

        logger.info(f"Sent alert to user {alert.user_id}: {alert.message}")

    # Public API methods

    async def subscribe_to_price_feed(self, websocket, user_id: int, symbols: List[str]):
        """Subscribe to price feeds"""
        channels = [f"price_{symbol}" for symbol in symbols]
        await self.websocket_manager.connect(websocket, user_id, channels)

    async def subscribe_to_order_book(self, websocket, user_id: int, symbols: List[str]):
        """Subscribe to order book feeds"""
        channels = [f"orderbook_{symbol}" for symbol in symbols]
        await self.websocket_manager.connect(websocket, user_id, channels)

    def create_price_alert(self, user_id: int, symbol: str, condition: str, threshold: Decimal) -> str:
        """Create a price alert"""
        return self.alert_manager.create_price_alert(user_id, symbol, condition, threshold)

    def get_order_book(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current order book"""
        order_book = self.order_book_manager.get_order_book(symbol)
        return order_book.to_dict() if order_book else None

    def get_price_history(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get price history"""
        if symbol not in self.price_history:
            return []

        history = list(self.price_history[symbol])[-limit:]
        return [price_update.to_dict() for price_update in history]


# Global real-time service instance
realtime_service = RealTimeService()

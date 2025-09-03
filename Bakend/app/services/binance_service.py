import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime, timedelta
import websocket
import threading
import time

from app.core.config import settings
from app.core.logging import logger

# Optional Binance imports
try:
    from binance import Client, ThreadedWebsocketManager
    from binance.exceptions import BinanceAPIException, BinanceOrderException
    BINANCE_AVAILABLE = True
    logger.info("Binance library is available")
except ImportError:
    logger.warning("Binance library not available - using mock data")
    BINANCE_AVAILABLE = False

    # Mock classes for when Binance is not available
    class Client:
        def __init__(self, *args, **kwargs):
            pass
        def ping(self):
            pass
        def get_symbol_ticker(self, symbol):
            return {'price': '50000.00'}
        def get_ticker(self, symbol=None):
            return {'lastPrice': '50000.00', 'priceChange': '1000.00', 'priceChangePercent': '2.00',
                   'highPrice': '51000.00', 'lowPrice': '49000.00', 'volume': '1000.00',
                   'quoteVolume': '50000000.00', 'openPrice': '49000.00', 'prevClosePrice': '49000.00',
                   'count': 1000}
        def get_all_tickers(self):
            return [{'symbol': 'BTCUSDT', 'price': '50000.00'}, {'symbol': 'ETHUSDT', 'price': '3000.00'}]
        def get_klines(self, symbol, interval, limit):
            return []
        def get_system_status(self):
            return {'status': 0, 'msg': 'normal'}
        def get_server_time(self):
            return {'serverTime': int(datetime.now().timestamp() * 1000)}

    class ThreadedWebsocketManager:
        def __init__(self):
            pass
        def start(self):
            pass
        def stop(self):
            pass
        def start_multiplex_socket(self, callback, streams):
            pass

    class BinanceAPIException(Exception):
        pass

    class BinanceOrderException(Exception):
        pass


class BinanceMarketDataService:
    """Service for fetching real-time market data from Binance"""

    def __init__(self):
        # Initialize Binance client (no API key needed for market data)
        self.client = None
        self.price_cache = {}
        self.last_update = {}
        self.websocket_manager = None
        self.is_connected = False
        self._client_initialized = False

        # Popular trading pairs
        self.trading_pairs = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
            'XRPUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'MATICUSDT',
            'LINKUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'FILUSDT',
            'TRXUSDT', 'ETCUSDT', 'XLMUSDT', 'VETUSDT', 'ICPUSDT'
        ]

    def get_symbol_from_crypto(self, symbol: str) -> str:
        """Convert crypto symbol to Binance trading pair"""
        symbol = symbol.upper()
        if symbol == 'BTC':
            return 'BTCUSDT'
        elif symbol == 'ETH':
            return 'ETHUSDT'
        elif symbol == 'BNB':
            return 'BNBUSDT'
        elif symbol == 'ADA':
            return 'ADAUSDT'
        elif symbol == 'SOL':
            return 'SOLUSDT'
        elif symbol == 'XRP':
            return 'XRPUSDT'
        elif symbol == 'DOT':
            return 'DOTUSDT'
        elif symbol == 'DOGE':
            return 'DOGEUSDT'
        elif symbol == 'AVAX':
            return 'AVAXUSDT'
        elif symbol == 'MATIC':
            return 'MATICUSDT'
        elif symbol == 'LINK':
            return 'LINKUSDT'
        elif symbol == 'LTC':
            return 'LTCUSDT'
        elif symbol == 'UNI':
            return 'UNIUSDT'
        elif symbol == 'ATOM':
            return 'ATOMUSDT'
        elif symbol == 'FIL':
            return 'FILUSDT'
        elif symbol == 'TRX':
            return 'TRXUSDT'
        elif symbol == 'ETC':
            return 'ETCUSDT'
        elif symbol == 'XLM':
            return 'XLMUSDT'
        elif symbol == 'VET':
            return 'VETUSDT'
        elif symbol == 'ICP':
            return 'ICPUSDT'
        else:
            return f'{symbol}USDT'  # Default format

    def _ensure_client(self):
        """Lazy initialization of Binance client"""
        if not self._client_initialized:
            try:
                if BINANCE_AVAILABLE:
                    self.client = Client()
                    logger.info("Binance client initialized successfully")
                else:
                    self.client = Client()  # Mock client
                    logger.info("Using mock Binance client (library not available)")
                self._client_initialized = True
            except Exception as e:
                logger.warning(f"Binance client initialization failed: {e}")
                self.client = Client()  # Use mock client as fallback
                self._client_initialized = True  # Mark as attempted

    def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current price for a cryptocurrency"""
        try:
            self._ensure_client()
            if not self.client:
                logger.warning(f"Binance client not available, returning mock price for {symbol}")
                # Return mock price for development
                return Decimal("50000.00") if symbol.upper() == 'BTC' else Decimal("3000.00")

            binance_symbol = self.get_symbol_from_crypto(symbol)

            # If Binance library is not available, return mock prices
            if not BINANCE_AVAILABLE:
                mock_prices = {
                    'BTC': Decimal("50000.00"),
                    'ETH': Decimal("3000.00"),
                    'BNB': Decimal("300.00"),
                    'ADA': Decimal("0.50"),
                    'SOL': Decimal("100.00")
                }
                return mock_prices.get(symbol.upper(), Decimal("100.00"))

            # Check cache first (if updated within last 30 seconds)
            if (binance_symbol in self.price_cache and
                binance_symbol in self.last_update and
                (datetime.now() - self.last_update[binance_symbol]).seconds < 30):
                return self.price_cache[binance_symbol]

            # Fetch from Binance API
            ticker = self.client.get_symbol_ticker(symbol=binance_symbol)
            price = Decimal(str(ticker['price']))

            # Update cache
            self.price_cache[binance_symbol] = price
            self.last_update[binance_symbol] = datetime.now()

            logger.info(f"Fetched real price for {symbol}: ${price}")
            return price

        except BinanceAPIException as e:
            logger.error(f"Binance API error for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_24h_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get 24h ticker statistics"""
        try:
            binance_symbol = self.get_symbol_from_crypto(symbol)
            ticker = self.client.get_ticker(symbol=binance_symbol)

            return {
                'symbol': symbol,
                'price': Decimal(str(ticker['lastPrice'])),
                'price_change': Decimal(str(ticker['priceChange'])),
                'price_change_percent': Decimal(str(ticker['priceChangePercent'])),
                'high_price': Decimal(str(ticker['highPrice'])),
                'low_price': Decimal(str(ticker['lowPrice'])),
                'volume': Decimal(str(ticker['volume'])),
                'quote_volume': Decimal(str(ticker['quoteVolume'])),
                'open_price': Decimal(str(ticker['openPrice'])),
                'prev_close_price': Decimal(str(ticker['prevClosePrice'])),
                'count': int(ticker['count']),
                'last_update': datetime.now()
            }

        except BinanceAPIException as e:
            logger.error(f"Binance API error for {symbol} ticker: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None

    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Decimal]:
        """Get current prices for multiple cryptocurrencies"""
        try:
            # Convert to Binance symbols
            binance_symbols = [self.get_symbol_from_crypto(symbol) for symbol in symbols]

            # Fetch all prices at once
            tickers = self.client.get_all_tickers()

            result = {}
            ticker_dict = {ticker['symbol']: Decimal(str(ticker['price'])) for ticker in tickers}

            for i, symbol in enumerate(symbols):
                binance_symbol = binance_symbols[i]
                if binance_symbol in ticker_dict:
                    result[symbol] = ticker_dict[binance_symbol]
                    # Update cache
                    self.price_cache[binance_symbol] = ticker_dict[binance_symbol]
                    self.last_update[binance_symbol] = datetime.now()

            logger.info(f"Fetched real prices for {len(result)} cryptocurrencies")
            return result

        except BinanceAPIException as e:
            logger.error(f"Binance API error for multiple prices: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching multiple prices: {e}")
            return {}

    def get_top_cryptocurrencies(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top cryptocurrencies by 24h volume"""
        try:
            # Get 24h tickers for all symbols
            tickers = self.client.get_ticker()

            # Filter USDT pairs and sort by volume
            usdt_tickers = [
                ticker for ticker in tickers
                if ticker['symbol'].endswith('USDT') and
                ticker['symbol'] in [self.get_symbol_from_crypto(pair.replace('USDT', '')) for pair in self.trading_pairs]
            ]

            # Sort by quote volume (USDT volume)
            usdt_tickers.sort(key=lambda x: float(x['quoteVolume']), reverse=True)

            result = []
            for ticker in usdt_tickers[:limit]:
                symbol = ticker['symbol'].replace('USDT', '')
                result.append({
                    'symbol': symbol,
                    'name': self._get_crypto_name(symbol),
                    'price': Decimal(str(ticker['lastPrice'])),
                    'price_change_24h': Decimal(str(ticker['priceChange'])),
                    'price_change_percentage_24h': Decimal(str(ticker['priceChangePercent'])),
                    'volume_24h': Decimal(str(ticker['volume'])),
                    'quote_volume_24h': Decimal(str(ticker['quoteVolume'])),
                    'high_24h': Decimal(str(ticker['highPrice'])),
                    'low_24h': Decimal(str(ticker['lowPrice'])),
                    'market_cap_rank': len(result) + 1,  # Approximate ranking
                    'last_updated': datetime.now()
                })

            logger.info(f"Fetched top {len(result)} cryptocurrencies from Binance")
            return result

        except BinanceAPIException as e:
            logger.error(f"Binance API error for top cryptos: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching top cryptocurrencies: {e}")
            return []

    def get_historical_prices(self, symbol: str, interval: str = '1h', limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical price data"""
        try:
            binance_symbol = self.get_symbol_from_crypto(symbol)

            # Get klines (candlestick data)
            klines = self.client.get_klines(
                symbol=binance_symbol,
                interval=interval,
                limit=limit
            )

            result = []
            for kline in klines:
                result.append({
                    'timestamp': datetime.fromtimestamp(kline[0] / 1000),
                    'open': Decimal(str(kline[1])),
                    'high': Decimal(str(kline[2])),
                    'low': Decimal(str(kline[3])),
                    'close': Decimal(str(kline[4])),
                    'volume': Decimal(str(kline[5])),
                    'quote_volume': Decimal(str(kline[7]))
                })

            logger.info(f"Fetched {len(result)} historical prices for {symbol}")
            return result

        except BinanceAPIException as e:
            logger.error(f"Binance API error for historical data {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return []

    def start_websocket_stream(self, symbols: List[str], callback=None):
        """Start real-time price stream via WebSocket"""
        try:
            if self.websocket_manager:
                self.websocket_manager.stop()

            self.websocket_manager = ThreadedWebsocketManager()
            self.websocket_manager.start()

            # Convert symbols to Binance format
            streams = [f"{self.get_symbol_from_crypto(symbol).lower()}@ticker" for symbol in symbols]

            def handle_socket_message(msg):
                try:
                    if msg['e'] == '24hrTicker':
                        symbol = msg['s'].replace('USDT', '')
                        price = Decimal(str(msg['c']))

                        # Update cache
                        self.price_cache[msg['s']] = price
                        self.last_update[msg['s']] = datetime.now()

                        if callback:
                            callback(symbol, price, msg)

                        logger.debug(f"WebSocket price update: {symbol} = ${price}")

                except Exception as e:
                    logger.error(f"Error processing WebSocket message: {e}")

            # Start multiple streams
            self.websocket_manager.start_multiplex_socket(
                callback=handle_socket_message,
                streams=streams
            )

            self.is_connected = True
            logger.info(f"Started WebSocket streams for {len(symbols)} symbols")

        except Exception as e:
            logger.error(f"Error starting WebSocket stream: {e}")
            self.is_connected = False

    def stop_websocket_stream(self):
        """Stop WebSocket stream"""
        try:
            if self.websocket_manager:
                self.websocket_manager.stop()
                self.websocket_manager = None
            self.is_connected = False
            logger.info("Stopped WebSocket streams")
        except Exception as e:
            logger.error(f"Error stopping WebSocket stream: {e}")

    def _get_crypto_name(self, symbol: str) -> str:
        """Get full name for cryptocurrency symbol"""
        names = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'BNB': 'Binance Coin',
            'ADA': 'Cardano',
            'SOL': 'Solana',
            'XRP': 'XRP',
            'DOT': 'Polkadot',
            'DOGE': 'Dogecoin',
            'AVAX': 'Avalanche',
            'MATIC': 'Polygon',
            'LINK': 'Chainlink',
            'LTC': 'Litecoin',
            'UNI': 'Uniswap',
            'ATOM': 'Cosmos',
            'FIL': 'Filecoin',
            'TRX': 'TRON',
            'ETC': 'Ethereum Classic',
            'XLM': 'Stellar',
            'VET': 'VeChain',
            'ICP': 'Internet Computer'
        }
        return names.get(symbol, symbol)

    def get_market_status(self) -> Dict[str, Any]:
        """Get Binance market status"""
        try:
            status = self.client.get_system_status()
            server_time = self.client.get_server_time()

            return {
                'status': status['status'],
                'message': status['msg'],
                'server_time': datetime.fromtimestamp(server_time['serverTime'] / 1000),
                'is_connected': self.is_connected,
                'cached_prices': len(self.price_cache),
                'last_cache_update': max(self.last_update.values()) if self.last_update else None
            }

        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'is_connected': False,
                'cached_prices': 0
            }

    def test_connection(self) -> bool:
        """Test connection to Binance API"""
        try:
            self._ensure_client()
            if not self.client:
                logger.warning("Binance client not available")
                return False
            self.client.ping()
            logger.info("Binance API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Binance API connection test failed: {e}")
            return False


# Global instance
binance_service = BinanceMarketDataService()

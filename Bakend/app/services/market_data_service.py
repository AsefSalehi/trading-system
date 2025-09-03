from typing import List, Dict, Optional, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.cryptocurrency import Cryptocurrency, PriceHistory
from app.services.binance_service import binance_service
from app.core.logging import logger


class MarketDataService:
    """Service for managing market data from Binance and other sources"""
    
    def __init__(self):
        self.supported_symbols = [
            'BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'XRP', 'DOT', 'DOGE', 
            'AVAX', 'MATIC', 'LINK', 'LTC', 'UNI', 'ATOM', 'FIL',
            'TRX', 'ETC', 'XLM', 'VET', 'ICP'
        ]
    
    def sync_cryptocurrency_data(self, db: Session, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Sync cryptocurrency data from Binance"""
        if symbols is None:
            symbols = self.supported_symbols
        
        try:
            logger.info(f"Starting Binance data sync for {len(symbols)} symbols")
            
            # Get real-time data from Binance
            binance_data = binance_service.get_top_cryptocurrencies(limit=len(symbols))
            
            updated_count = 0
            created_count = 0
            errors = []
            
            for crypto_data in binance_data:
                try:
                    symbol = crypto_data['symbol']
                    if symbol not in symbols:
                        continue
                    
                    # Find or create cryptocurrency record
                    crypto = db.query(Cryptocurrency).filter(
                        Cryptocurrency.symbol == symbol
                    ).first()
                    
                    if crypto:
                        # Update existing record
                        crypto.current_price = crypto_data['price']
                        crypto.price_change_24h = crypto_data['price_change_24h']
                        crypto.price_change_percentage_24h = crypto_data['price_change_percentage_24h']
                        crypto.total_volume = crypto_data['quote_volume_24h']
                        crypto.last_updated = datetime.utcnow()
                        updated_count += 1
                    else:
                        # Create new record
                        crypto = Cryptocurrency(
                            symbol=symbol,
                            name=crypto_data['name'],
                            slug=crypto_data['name'].lower().replace(' ', '-'),
                            current_price=crypto_data['price'],
                            price_change_24h=crypto_data['price_change_24h'],
                            price_change_percentage_24h=crypto_data['price_change_percentage_24h'],
                            total_volume=crypto_data['quote_volume_24h'],
                            market_cap_rank=crypto_data['market_cap_rank'],
                            is_active=True,
                            last_updated=datetime.utcnow()
                        )
                        db.add(crypto)
                        created_count += 1
                    
                    # Store price history
                    self._store_price_history(db, crypto, crypto_data)
                    
                except Exception as e:
                    error_msg = f"Error processing {crypto_data.get('symbol', 'unknown')}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            db.commit()
            
            result = {
                'status': 'success',
                'updated_count': updated_count,
                'created_count': created_count,
                'total_processed': updated_count + created_count,
                'errors': errors,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Binance sync completed: {result}")
            return result
            
        except Exception as e:
            db.rollback()
            error_msg = f"Binance sync failed: {str(e)}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'message': error_msg,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _store_price_history(self, db: Session, crypto: Cryptocurrency, crypto_data: Dict[str, Any]):
        """Store price history record"""
        try:
            # Check if we already have a recent price history entry (within last hour)
            recent_history = db.query(PriceHistory).filter(
                and_(
                    PriceHistory.cryptocurrency_id == crypto.id,
                    PriceHistory.timestamp >= datetime.utcnow() - timedelta(hours=1)
                )
            ).first()
            
            if not recent_history:
                price_history = PriceHistory(
                    cryptocurrency_id=crypto.id,
                    symbol=crypto.symbol,
                    price=crypto_data['price'],
                    total_volume=crypto_data.get('quote_volume_24h', 0),
                    timestamp=datetime.utcnow()
                )
                db.add(price_history)
                
        except Exception as e:
            logger.error(f"Error storing price history for {crypto.symbol}: {e}")
    
    def get_real_time_price(self, symbol: str) -> Optional[Decimal]:
        """Get real-time price for a symbol"""
        try:
            return binance_service.get_current_price(symbol)
        except Exception as e:
            logger.error(f"Error getting real-time price for {symbol}: {e}")
            return None
    
    def get_real_time_prices(self, symbols: List[str]) -> Dict[str, Decimal]:
        """Get real-time prices for multiple symbols"""
        try:
            return binance_service.get_multiple_prices(symbols)
        except Exception as e:
            logger.error(f"Error getting real-time prices: {e}")
            return {}
    
    def get_24h_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get 24h ticker data"""
        try:
            return binance_service.get_24h_ticker(symbol)
        except Exception as e:
            logger.error(f"Error getting 24h ticker for {symbol}: {e}")
            return None
    
    def get_market_overview(self, db: Session) -> Dict[str, Any]:
        """Get market overview with real-time data"""
        try:
            # Get top cryptocurrencies from database
            top_cryptos = db.query(Cryptocurrency).filter(
                Cryptocurrency.is_active == True
            ).order_by(Cryptocurrency.market_cap_rank).limit(20).all()
            
            # Get real-time prices
            symbols = [crypto.symbol for crypto in top_cryptos]
            real_time_prices = self.get_real_time_prices(symbols)
            
            market_data = []
            total_market_cap = Decimal('0')
            total_volume = Decimal('0')
            
            for crypto in top_cryptos:
                # Use real-time price if available
                current_price = real_time_prices.get(crypto.symbol, crypto.current_price or Decimal('0'))
                
                # Get 24h ticker data
                ticker_data = self.get_24h_ticker(crypto.symbol)
                
                if ticker_data:
                    price_change_24h = ticker_data['price_change_percent']
                    volume_24h = ticker_data['quote_volume']
                else:
                    price_change_24h = crypto.price_change_percentage_24h or Decimal('0')
                    volume_24h = crypto.total_volume or Decimal('0')
                
                # Estimate market cap (this would need circulating supply data)
                estimated_market_cap = current_price * Decimal('1000000')  # Placeholder
                
                market_data.append({
                    'symbol': crypto.symbol,
                    'name': crypto.name,
                    'current_price': float(current_price),
                    'price_change_24h': float(price_change_24h),
                    'volume_24h': float(volume_24h),
                    'market_cap': float(estimated_market_cap),
                    'market_cap_rank': crypto.market_cap_rank,
                    'last_updated': datetime.utcnow().isoformat()
                })
                
                total_volume += volume_24h
                total_market_cap += estimated_market_cap
            
            return {
                'cryptocurrencies': market_data,
                'total_market_cap': float(total_market_cap),
                'total_volume_24h': float(total_volume),
                'active_cryptocurrencies': len(market_data),
                'last_updated': datetime.utcnow().isoformat(),
                'data_source': 'Binance API'
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {
                'error': str(e),
                'cryptocurrencies': [],
                'total_market_cap': 0,
                'total_volume_24h': 0,
                'active_cryptocurrencies': 0
            }
    
    def start_real_time_updates(self, symbols: Optional[List[str]] = None):
        """Start real-time price updates via WebSocket"""
        if symbols is None:
            symbols = self.supported_symbols
        
        def price_update_callback(symbol: str, price: Decimal, data: Dict):
            logger.info(f"Real-time update: {symbol} = ${price}")
            # Here you could update database or trigger other actions
        
        try:
            binance_service.start_websocket_stream(symbols, price_update_callback)
            logger.info(f"Started real-time updates for {len(symbols)} symbols")
        except Exception as e:
            logger.error(f"Error starting real-time updates: {e}")
    
    def stop_real_time_updates(self):
        """Stop real-time price updates"""
        try:
            binance_service.stop_websocket_stream()
            logger.info("Stopped real-time updates")
        except Exception as e:
            logger.error(f"Error stopping real-time updates: {e}")
    
    def get_historical_data(self, symbol: str, interval: str = '1h', limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical price data"""
        try:
            return binance_service.get_historical_prices(symbol, interval, limit)
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return []
    
    def test_binance_connection(self) -> Dict[str, Any]:
        """Test connection to Binance API"""
        try:
            is_connected = binance_service.test_connection()
            market_status = binance_service.get_market_status()
            
            return {
                'binance_connected': is_connected,
                'market_status': market_status,
                'supported_symbols': len(self.supported_symbols),
                'test_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'binance_connected': False,
                'error': str(e),
                'test_timestamp': datetime.utcnow().isoformat()
            }


# Global instance
market_data_service = MarketDataService()
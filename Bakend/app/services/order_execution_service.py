"""
Advanced Order Execution Service
Handles limit orders, stop-loss, take-profit with production-grade accuracy
"""

import asyncio
from typing import List, Optional, Dict, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.wallet import Order, OrderType, OrderStatus, TransactionType, Wallet
from app.models.cryptocurrency import Cryptocurrency
from app.services.trading_service import trading_service
from app.services.cryptocurrency_service import cryptocurrency_service
from app.core.logging import logger


class OrderExecutionService:
    """Advanced order execution with limit, stop-loss, and take-profit orders"""
    
    def __init__(self):
        self.is_running = False
        self.execution_interval = 1.0  # Check orders every 1 second
        
    async def start_order_monitoring(self):
        """Start the order monitoring loop"""
        if self.is_running:
            return
            
        self.is_running = True
        logger.info("Starting advanced order execution monitoring")
        
        while self.is_running:
            try:
                await self.process_pending_orders()
                await asyncio.sleep(self.execution_interval)
            except Exception as e:
                logger.error(f"Error in order monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    def stop_order_monitoring(self):
        """Stop the order monitoring loop"""
        self.is_running = False
        logger.info("Stopping advanced order execution monitoring")
    
    async def process_pending_orders(self):
        """Process all pending orders"""
        from app.db.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Get all pending orders
            pending_orders = db.query(Order).filter(
                Order.status == OrderStatus.PENDING
            ).all()
            
            for order in pending_orders:
                try:
                    await self.check_and_execute_order(db, order)
                except Exception as e:
                    logger.error(f"Error processing order {order.id}: {e}")
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error in process_pending_orders: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def check_and_execute_order(self, db: Session, order: Order):
        """Check if order should be executed and execute if conditions are met"""
        # Get current price
        current_price = await self.get_current_price(order.symbol)
        if current_price is None:
            return
        
        should_execute = False
        execution_price = current_price
        
        if order.order_type == OrderType.LIMIT:
            should_execute = self.check_limit_order(order, current_price)
            execution_price = min(order.price, current_price) if order.transaction_type == TransactionType.BUY else max(order.price, current_price)
            
        elif order.order_type == OrderType.STOP_LOSS:
            should_execute = self.check_stop_loss_order(order, current_price)
            execution_price = current_price  # Execute at market price
            
        elif order.order_type == OrderType.TAKE_PROFIT:
            should_execute = self.check_take_profit_order(order, current_price)
            execution_price = current_price  # Execute at market price
        
        if should_execute:
            await self.execute_order(db, order, execution_price)
    
    def check_limit_order(self, order: Order, current_price: Decimal) -> bool:
        """Check if limit order should be executed"""
        if order.transaction_type == TransactionType.BUY:
            # Buy limit: execute when current price <= limit price
            return current_price <= order.price
        else:
            # Sell limit: execute when current price >= limit price
            return current_price >= order.price
    
    def check_stop_loss_order(self, order: Order, current_price: Decimal) -> bool:
        """Check if stop-loss order should be executed"""
        if order.transaction_type == TransactionType.SELL:
            # Stop-loss sell: execute when current price <= stop price
            return current_price <= order.stop_price
        else:
            # Stop-loss buy: execute when current price >= stop price
            return current_price >= order.stop_price
    
    def check_take_profit_order(self, order: Order, current_price: Decimal) -> bool:
        """Check if take-profit order should be executed"""
        if order.transaction_type == TransactionType.SELL:
            # Take-profit sell: execute when current price >= target price
            return current_price >= order.trigger_price
        else:
            # Take-profit buy: execute when current price <= target price
            return current_price <= order.trigger_price
    
    async def execute_order(self, db: Session, order: Order, execution_price: Decimal):
        """Execute the order at the given price"""
        try:
            logger.info(f"Executing {order.order_type.value} order {order.id} for {order.symbol} at ${execution_price}")
            
            # Execute the trade using trading service
            if order.transaction_type == TransactionType.BUY:
                result = trading_service.place_market_order(
                    db=db,
                    wallet_id=order.wallet_id,
                    symbol=order.symbol,
                    transaction_type=TransactionType.BUY,
                    amount=order.total_amount  # USD amount for buy
                )
            else:
                result = trading_service.place_market_order(
                    db=db,
                    wallet_id=order.wallet_id,
                    symbol=order.symbol,
                    transaction_type=TransactionType.SELL,
                    amount=order.quantity  # Quantity for sell
                )
            
            # Update order status
            order.status = OrderStatus.EXECUTED
            order.executed_price = execution_price
            order.executed_quantity = order.quantity
            order.executed_at = datetime.utcnow()
            
            logger.info(f"Successfully executed order {order.id}: {result}")
            
        except Exception as e:
            logger.error(f"Failed to execute order {order.id}: {e}")
            # Don't change order status on failure - will retry
    
    async def get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current price for symbol"""
        try:
            from app.services.binance_service import binance_service
            
            # Try Binance first
            price = binance_service.get_current_price(symbol)
            if price and price > 0:
                return Decimal(str(price))
            
            # Fallback to database
            from app.db.database import SessionLocal
            db = SessionLocal()
            try:
                crypto = db.query(Cryptocurrency).filter(
                    Cryptocurrency.symbol == symbol
                ).first()
                if crypto and crypto.current_price:
                    return crypto.current_price
            finally:
                db.close()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    def place_limit_order(self, db: Session, wallet_id: int, symbol: str,
                         transaction_type: TransactionType, quantity: Decimal,
                         limit_price: Decimal) -> Order:
        """Place a limit order"""
        
        # Calculate total amount
        total_amount = quantity * limit_price
        
        # Validate wallet has sufficient funds
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise ValueError("Wallet not found")
        
        if transaction_type == TransactionType.BUY:
            if wallet.usd_balance < total_amount:
                raise ValueError(f"Insufficient USD balance. Required: ${total_amount}, Available: ${wallet.usd_balance}")
        else:
            # Check if user has enough cryptocurrency
            from app.models.wallet import Holding
            holding = db.query(Holding).filter(
                and_(Holding.wallet_id == wallet_id, Holding.symbol == symbol)
            ).first()
            
            if not holding or holding.quantity < quantity:
                available = holding.quantity if holding else Decimal('0')
                raise ValueError(f"Insufficient {symbol}. Required: {quantity}, Available: {available}")
        
        # Get cryptocurrency info
        crypto = db.query(Cryptocurrency).filter(Cryptocurrency.symbol == symbol).first()
        if not crypto:
            raise ValueError(f"Cryptocurrency {symbol} not found")
        
        # Create limit order
        order = Order(
            wallet_id=wallet_id,
            cryptocurrency_id=crypto.id,
            order_type=OrderType.LIMIT,
            transaction_type=transaction_type,
            symbol=symbol,
            quantity=quantity,
            price=limit_price,
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        logger.info(f"Placed limit order: {transaction_type.value} {quantity} {symbol} at ${limit_price}")
        
        return order
    
    def place_stop_loss_order(self, db: Session, wallet_id: int, symbol: str,
                             quantity: Decimal, stop_price: Decimal) -> Order:
        """Place a stop-loss order (always sell)"""
        
        # Validate holding exists
        from app.models.wallet import Holding
        holding = db.query(Holding).filter(
            and_(Holding.wallet_id == wallet_id, Holding.symbol == symbol)
        ).first()
        
        if not holding or holding.quantity < quantity:
            available = holding.quantity if holding else Decimal('0')
            raise ValueError(f"Insufficient {symbol} for stop-loss. Required: {quantity}, Available: {available}")
        
        # Get cryptocurrency info
        crypto = db.query(Cryptocurrency).filter(Cryptocurrency.symbol == symbol).first()
        if not crypto:
            raise ValueError(f"Cryptocurrency {symbol} not found")
        
        # Create stop-loss order
        order = Order(
            wallet_id=wallet_id,
            cryptocurrency_id=crypto.id,
            order_type=OrderType.STOP_LOSS,
            transaction_type=TransactionType.SELL,
            symbol=symbol,
            quantity=quantity,
            stop_price=stop_price,
            total_amount=quantity * stop_price,  # Estimated
            status=OrderStatus.PENDING
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        logger.info(f"Placed stop-loss order: Sell {quantity} {symbol} when price <= ${stop_price}")
        
        return order
    
    def place_take_profit_order(self, db: Session, wallet_id: int, symbol: str,
                               quantity: Decimal, target_price: Decimal) -> Order:
        """Place a take-profit order (always sell)"""
        
        # Validate holding exists
        from app.models.wallet import Holding
        holding = db.query(Holding).filter(
            and_(Holding.wallet_id == wallet_id, Holding.symbol == symbol)
        ).first()
        
        if not holding or holding.quantity < quantity:
            available = holding.quantity if holding else Decimal('0')
            raise ValueError(f"Insufficient {symbol} for take-profit. Required: {quantity}, Available: {available}")
        
        # Get cryptocurrency info
        crypto = db.query(Cryptocurrency).filter(Cryptocurrency.symbol == symbol).first()
        if not crypto:
            raise ValueError(f"Cryptocurrency {symbol} not found")
        
        # Create take-profit order
        order = Order(
            wallet_id=wallet_id,
            cryptocurrency_id=crypto.id,
            order_type=OrderType.TAKE_PROFIT,
            transaction_type=TransactionType.SELL,
            symbol=symbol,
            quantity=quantity,
            trigger_price=target_price,
            total_amount=quantity * target_price,  # Estimated
            status=OrderStatus.PENDING
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        logger.info(f"Placed take-profit order: Sell {quantity} {symbol} when price >= ${target_price}")
        
        return order
    
    def cancel_order(self, db: Session, order_id: int, user_id: int) -> bool:
        """Cancel a pending order"""
        order = db.query(Order).join(Wallet).filter(
            and_(Order.id == order_id, Wallet.user_id == user_id, Order.status == OrderStatus.PENDING)
        ).first()
        
        if not order:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Cancelled order {order_id}")
        
        return True
    
    def get_user_orders(self, db: Session, user_id: int, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get user's orders"""
        query = db.query(Order).join(Wallet).filter(Wallet.user_id == user_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        return query.order_by(Order.created_at.desc()).all()


# Global order execution service instance
order_execution_service = OrderExecutionService()
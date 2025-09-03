from typing import List, Optional, Dict, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import random

from app.models.wallet import (
    Wallet, Holding, Transaction, Order, TradingSession,
    TransactionType, OrderType, OrderStatus
)
from app.models.user import User
from app.models.cryptocurrency import Cryptocurrency
from app.services.cryptocurrency_service import cryptocurrency_service
from app.services.binance_service import binance_service


class TradingService:
    """Service for trading operations and wallet management"""

    TRADING_FEE_PERCENTAGE = Decimal('0.001')  # 0.1% trading fee
    INITIAL_BALANCE = Decimal('10000.00')  # $10,000 starting balance

    def __init__(self):
        self.fee_percentage = self.TRADING_FEE_PERCENTAGE

    def create_wallet(self, db: Session, user_id: int) -> Wallet:
        """Create a new wallet for a user"""
        # Check if wallet already exists
        existing_wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if existing_wallet:
            return existing_wallet

        wallet = Wallet(
            user_id=user_id,
            usd_balance=self.INITIAL_BALANCE,
            total_portfolio_value=self.INITIAL_BALANCE
        )

        db.add(wallet)
        db.commit()
        db.refresh(wallet)

        # Create initial deposit transaction
        self.create_transaction(
            db=db,
            wallet_id=wallet.id,
            transaction_type=TransactionType.DEPOSIT,
            total_amount=self.INITIAL_BALANCE,
            notes="Initial wallet funding"
        )

        return wallet

    def get_wallet(self, db: Session, user_id: int) -> Optional[Wallet]:
        """Get user's wallet"""
        return db.query(Wallet).filter(Wallet.user_id == user_id).first()

    def place_market_order(self, db: Session, wallet_id: int, symbol: str,
                          transaction_type: TransactionType, amount: Decimal) -> Dict:
        """Place a market order (buy/sell immediately at current price)"""
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise ValueError("Wallet not found")

        crypto = db.query(Cryptocurrency).filter(Cryptocurrency.symbol == symbol).first()
        if not crypto:
            raise ValueError(f"Cryptocurrency {symbol} not found")

        # Get real-time price from Binance
        current_price = binance_service.get_current_price(symbol)
        if current_price is None or current_price <= 0:
            # Fallback to database price or fake price
            current_price = crypto.current_price or self._get_fake_price(symbol)

        if transaction_type == TransactionType.BUY:
            return self._execute_buy_order(db, wallet, crypto, amount, current_price)
        else:
            return self._execute_sell_order(db, wallet, crypto, amount, current_price)

    def _execute_buy_order(self, db: Session, wallet: Wallet, crypto: Cryptocurrency,
                          usd_amount: Decimal, price: Decimal) -> Dict:
        """Execute a buy order"""
        fee = usd_amount * self.fee_percentage
        net_amount = usd_amount - fee
        quantity = net_amount / price

        # Check if user has enough balance
        if wallet.usd_balance < usd_amount:
            raise ValueError(f"Insufficient balance. Available: ${wallet.usd_balance}, Required: ${usd_amount}")

        # Update wallet balance
        wallet.usd_balance -= usd_amount
        wallet.total_invested += net_amount

        # Update or create holding
        holding = db.query(Holding).filter(
            and_(Holding.wallet_id == wallet.id, Holding.symbol == crypto.symbol)
        ).first()

        if holding:
            # Update existing holding (average cost)
            total_cost = holding.total_cost + net_amount
            total_quantity = holding.quantity + quantity
            holding.average_buy_price = total_cost / total_quantity
            holding.quantity = total_quantity
            holding.total_cost = total_cost
        else:
            # Create new holding
            holding = Holding(
                wallet_id=wallet.id,
                cryptocurrency_id=crypto.id,
                symbol=crypto.symbol,
                quantity=quantity,
                average_buy_price=price,
                total_cost=net_amount
            )
            db.add(holding)

        # Create transaction record
        transaction = self.create_transaction(
            db=db,
            wallet_id=wallet.id,
            cryptocurrency_id=crypto.id,
            transaction_type=TransactionType.BUY,
            symbol=crypto.symbol,
            quantity=quantity,
            price=price,
            total_amount=usd_amount,
            fee=fee
        )

        # Update wallet stats
        wallet.total_trades += 1

        db.commit()

        return {
            "status": "success",
            "transaction_id": transaction.id,
            "symbol": crypto.symbol,
            "quantity": float(quantity),
            "price": float(price),
            "total_amount": float(usd_amount),
            "fee": float(fee),
            "remaining_balance": float(wallet.usd_balance)
        }

    def _execute_sell_order(self, db: Session, wallet: Wallet, crypto: Cryptocurrency,
                           quantity: Decimal, price: Decimal) -> Dict:
        """Execute a sell order"""
        # Find holding
        holding = db.query(Holding).filter(
            and_(Holding.wallet_id == wallet.id, Holding.symbol == crypto.symbol)
        ).first()

        if not holding or holding.quantity < quantity:
            available = holding.quantity if holding else 0
            raise ValueError(f"Insufficient {crypto.symbol}. Available: {available}, Required: {quantity}")

        gross_amount = quantity * price
        fee = gross_amount * self.fee_percentage
        net_amount = gross_amount - fee

        # Calculate P&L
        cost_basis = quantity * holding.average_buy_price
        realized_pnl = net_amount - cost_basis
        realized_pnl_percentage = (realized_pnl / cost_basis) * 100 if cost_basis > 0 else 0

        # Update wallet
        wallet.usd_balance += net_amount
        wallet.total_profit_loss += realized_pnl

        # Update holding
        holding.quantity -= quantity
        holding.total_cost -= cost_basis

        if holding.quantity <= 0:
            db.delete(holding)

        # Create transaction
        transaction = self.create_transaction(
            db=db,
            wallet_id=wallet.id,
            cryptocurrency_id=crypto.id,
            transaction_type=TransactionType.SELL,
            symbol=crypto.symbol,
            quantity=quantity,
            price=price,
            total_amount=gross_amount,
            fee=fee,
            realized_pnl=realized_pnl,
            realized_pnl_percentage=realized_pnl_percentage
        )

        # Update wallet stats
        wallet.total_trades += 1
        if realized_pnl > 0:
            wallet.winning_trades += 1
        else:
            wallet.losing_trades += 1

        wallet.win_rate = (wallet.winning_trades / wallet.total_trades) * 100 if wallet.total_trades > 0 else 0

        db.commit()

        return {
            "status": "success",
            "transaction_id": transaction.id,
            "symbol": crypto.symbol,
            "quantity": float(quantity),
            "price": float(price),
            "total_amount": float(gross_amount),
            "fee": float(fee),
            "realized_pnl": float(realized_pnl),
            "realized_pnl_percentage": float(realized_pnl_percentage),
            "remaining_balance": float(wallet.usd_balance)
        }

    def create_transaction(self, db: Session, wallet_id: int, transaction_type: TransactionType,
                          total_amount: Decimal, cryptocurrency_id: Optional[int] = None,
                          symbol: Optional[str] = None, quantity: Optional[Decimal] = None,
                          price: Optional[Decimal] = None, fee: Decimal = Decimal('0'),
                          realized_pnl: Optional[Decimal] = None,
                          realized_pnl_percentage: Optional[Decimal] = None,
                          notes: Optional[str] = None) -> Transaction:
        """Create a transaction record"""
        transaction = Transaction(
            wallet_id=wallet_id,
            cryptocurrency_id=cryptocurrency_id,
            transaction_type=transaction_type,
            symbol=symbol,
            quantity=quantity,
            price=price,
            total_amount=total_amount,
            fee=fee,
            realized_pnl=realized_pnl,
            realized_pnl_percentage=realized_pnl_percentage,
            notes=notes
        )

        db.add(transaction)
        return transaction

    def update_portfolio_values(self, db: Session, wallet_id: int) -> Dict:
        """Update portfolio values with current market prices"""
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise ValueError("Wallet not found")

        holdings = db.query(Holding).filter(Holding.wallet_id == wallet_id).all()

        total_portfolio_value = wallet.usd_balance
        total_unrealized_pnl = Decimal('0')

        for holding in holdings:
            # Get real-time price from Binance
            current_price = binance_service.get_current_price(holding.symbol)
            if current_price is None or current_price <= 0:
                # Fallback to fake price
                current_price = self._get_fake_price(holding.symbol)
            holding.current_price = current_price

            # Calculate current value and unrealized P&L
            current_value = holding.quantity * current_price
            holding.current_value = current_value
            holding.unrealized_pnl = current_value - holding.total_cost
            holding.unrealized_pnl_percentage = (holding.unrealized_pnl / holding.total_cost) * 100 if holding.total_cost > 0 else 0

            total_portfolio_value += current_value
            total_unrealized_pnl += holding.unrealized_pnl

        # Update wallet
        previous_value = wallet.total_portfolio_value
        wallet.total_portfolio_value = total_portfolio_value
        wallet.daily_pnl = total_portfolio_value - previous_value

        # Calculate max drawdown
        if total_portfolio_value < self.INITIAL_BALANCE:
            drawdown = ((self.INITIAL_BALANCE - total_portfolio_value) / self.INITIAL_BALANCE) * 100
            wallet.max_drawdown = max(wallet.max_drawdown, drawdown)

        db.commit()

        return {
            "total_portfolio_value": float(total_portfolio_value),
            "usd_balance": float(wallet.usd_balance),
            "total_unrealized_pnl": float(total_unrealized_pnl),
            "total_realized_pnl": float(wallet.total_profit_loss),
            "daily_pnl": float(wallet.daily_pnl),
            "total_pnl": float(wallet.total_profit_loss + total_unrealized_pnl),
            "total_pnl_percentage": float(((wallet.total_profit_loss + total_unrealized_pnl) / self.INITIAL_BALANCE) * 100),
            "max_drawdown": float(wallet.max_drawdown),
            "win_rate": float(wallet.win_rate)
        }

    def get_portfolio_summary(self, db: Session, wallet_id: int) -> Dict:
        """Get comprehensive portfolio summary"""
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise ValueError("Wallet not found")

        # Update values first
        portfolio_data = self.update_portfolio_values(db, wallet_id)

        # Get holdings
        holdings = db.query(Holding).filter(Holding.wallet_id == wallet_id).all()
        holdings_data = []

        for holding in holdings:
            holdings_data.append({
                "symbol": holding.symbol,
                "quantity": float(holding.quantity),
                "average_buy_price": float(holding.average_buy_price),
                "current_price": float(holding.current_price or 0),
                "total_cost": float(holding.total_cost),
                "current_value": float(holding.current_value or 0),
                "unrealized_pnl": float(holding.unrealized_pnl),
                "unrealized_pnl_percentage": float(holding.unrealized_pnl_percentage)
            })

        # Get recent transactions
        recent_transactions = db.query(Transaction).filter(
            Transaction.wallet_id == wallet_id
        ).order_by(desc(Transaction.created_at)).limit(10).all()

        transactions_data = []
        for tx in recent_transactions:
            transactions_data.append({
                "id": tx.id,
                "type": tx.transaction_type.value,
                "symbol": tx.symbol,
                "quantity": float(tx.quantity or 0),
                "price": float(tx.price or 0),
                "total_amount": float(tx.total_amount),
                "fee": float(tx.fee),
                "realized_pnl": float(tx.realized_pnl or 0),
                "created_at": tx.created_at.isoformat()
            })

        return {
            **portfolio_data,
            "holdings": holdings_data,
            "recent_transactions": transactions_data,
            "total_trades": wallet.total_trades,
            "winning_trades": wallet.winning_trades,
            "losing_trades": wallet.losing_trades
        }

    def _get_fake_price(self, symbol: str) -> Decimal:
        """Generate fake but realistic price for demo purposes"""
        # Base prices for popular cryptocurrencies
        base_prices = {
            'BTC': 45000,
            'ETH': 2800,
            'BNB': 320,
            'ADA': 0.45,
            'SOL': 95,
            'XRP': 0.52,
            'DOT': 6.8,
            'DOGE': 0.08,
            'AVAX': 18,
            'MATIC': 0.85
        }

        base_price = base_prices.get(symbol, 100)  # Default to $100

        # Add some random variation (-5% to +5%)
        variation = random.uniform(-0.05, 0.05)
        current_price = base_price * (1 + variation)

        return Decimal(str(round(current_price, 8)))

    def simulate_market_movement(self, db: Session) -> Dict:
        """Simulate market movement for all holdings"""
        wallets = db.query(Wallet).filter(Wallet.is_active == True).all()

        results = []
        for wallet in wallets:
            try:
                portfolio_data = self.update_portfolio_values(db, wallet.id)
                results.append({
                    "wallet_id": wallet.id,
                    "user_id": wallet.user_id,
                    **portfolio_data
                })
            except Exception as e:
                results.append({
                    "wallet_id": wallet.id,
                    "error": str(e)
                })

        return {
            "status": "success",
            "updated_wallets": len(results),
            "results": results
        }


# Global trading service instance
trading_service = TradingService()

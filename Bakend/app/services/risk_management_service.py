"""
Enhanced Risk Management Service
Production-grade risk controls with position sizing, loss limits, and concentration limits
"""

from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from dataclasses import dataclass

from app.models.wallet import Wallet, Holding, Transaction, TransactionType
from app.models.user import User
from app.core.logging import logger


@dataclass
class RiskLimits:
    """Risk limit configuration"""
    max_position_size_percentage: Decimal = Decimal('20.0')  # Max 20% of portfolio in one asset
    max_daily_loss_percentage: Decimal = Decimal('5.0')      # Max 5% daily loss
    max_total_loss_percentage: Decimal = Decimal('25.0')     # Max 25% total loss from initial
    max_leverage: Decimal = Decimal('1.0')                   # No leverage by default
    min_cash_reserve_percentage: Decimal = Decimal('10.0')   # Keep 10% in cash
    max_correlation_exposure: Decimal = Decimal('50.0')      # Max 50% in correlated assets


@dataclass
class RiskMetrics:
    """Current risk metrics"""
    total_portfolio_value: Decimal
    cash_percentage: Decimal
    largest_position_percentage: Decimal
    daily_pnl_percentage: Decimal
    total_pnl_percentage: Decimal
    concentration_risk_score: Decimal
    risk_score: Decimal  # Overall risk score 0-100


class RiskManagementService:
    """Advanced risk management with production-grade controls"""
    
    def __init__(self):
        self.default_limits = RiskLimits()
    
    def validate_trade(self, db: Session, wallet_id: int, symbol: str,
                      transaction_type: TransactionType, amount: Decimal) -> Tuple[bool, str]:
        """Validate if trade meets risk management criteria"""
        
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            return False, "Wallet not found"
        
        # Get user's risk limits (could be customized per user)
        risk_limits = self.get_user_risk_limits(db, wallet.user_id)
        
        # Check daily loss limit
        if not self.check_daily_loss_limit(db, wallet, risk_limits):
            return False, f"Daily loss limit exceeded ({risk_limits.max_daily_loss_percentage}%)"
        
        # Check total loss limit
        if not self.check_total_loss_limit(wallet, risk_limits):
            return False, f"Total loss limit exceeded ({risk_limits.max_total_loss_percentage}%)"
        
        # For buy orders, check position sizing and concentration
        if transaction_type == TransactionType.BUY:
            if not self.check_position_size_limit(db, wallet, symbol, amount, risk_limits):
                return False, f"Position size would exceed {risk_limits.max_position_size_percentage}% limit"
            
            if not self.check_cash_reserve_limit(wallet, amount, risk_limits):
                return False, f"Trade would violate minimum cash reserve ({risk_limits.min_cash_reserve_percentage}%)"
        
        # Check concentration risk
        if not self.check_concentration_risk(db, wallet, symbol, transaction_type, amount, risk_limits):
            return False, "Trade would create excessive concentration risk"
        
        return True, "Trade approved"
    
    def check_daily_loss_limit(self, db: Session, wallet: Wallet, limits: RiskLimits) -> bool:
        """Check if daily loss limit is exceeded"""
        today = datetime.utcnow().date()
        
        # Get today's transactions
        daily_transactions = db.query(Transaction).filter(
            and_(
                Transaction.wallet_id == wallet.id,
                func.date(Transaction.created_at) == today
            )
        ).all()
        
        # Calculate daily P&L
        daily_pnl = sum(tx.realized_pnl or Decimal('0') for tx in daily_transactions)
        daily_pnl_percentage = (daily_pnl / wallet.total_portfolio_value) * 100
        
        return daily_pnl_percentage >= -limits.max_daily_loss_percentage
    
    def check_total_loss_limit(self, wallet: Wallet, limits: RiskLimits) -> bool:
        """Check if total loss limit is exceeded"""
        initial_balance = Decimal('10000.00')  # Starting balance
        total_loss_percentage = ((initial_balance - wallet.total_portfolio_value) / initial_balance) * 100
        
        return total_loss_percentage <= limits.max_total_loss_percentage
    
    def check_position_size_limit(self, db: Session, wallet: Wallet, symbol: str,
                                 buy_amount: Decimal, limits: RiskLimits) -> bool:
        """Check if position size would exceed limits"""
        # Get current holding
        current_holding = db.query(Holding).filter(
            and_(Holding.wallet_id == wallet.id, Holding.symbol == symbol)
        ).first()
        
        current_value = current_holding.current_value if current_holding else Decimal('0')
        new_total_value = current_value + buy_amount
        
        # Calculate percentage of portfolio
        position_percentage = (new_total_value / wallet.total_portfolio_value) * 100
        
        return position_percentage <= limits.max_position_size_percentage
    
    def check_cash_reserve_limit(self, wallet: Wallet, buy_amount: Decimal, limits: RiskLimits) -> bool:
        """Check if trade would violate minimum cash reserve"""
        remaining_cash = wallet.usd_balance - buy_amount
        cash_percentage = (remaining_cash / wallet.total_portfolio_value) * 100
        
        return cash_percentage >= limits.min_cash_reserve_percentage
    
    def check_concentration_risk(self, db: Session, wallet: Wallet, symbol: str,
                               transaction_type: TransactionType, amount: Decimal,
                               limits: RiskLimits) -> bool:
        """Check concentration risk across correlated assets"""
        
        # Get all holdings
        holdings = db.query(Holding).filter(Holding.wallet_id == wallet.id).all()
        
        # Define correlation groups (simplified)
        correlation_groups = {
            'major_crypto': ['BTC', 'ETH'],
            'defi_tokens': ['UNI', 'AAVE', 'COMP', 'MKR'],
            'layer1_chains': ['SOL', 'ADA', 'DOT', 'AVAX'],
            'meme_coins': ['DOGE', 'SHIB'],
            'exchange_tokens': ['BNB', 'FTT', 'CRO']
        }
        
        # Find which group the symbol belongs to
        target_group = None
        for group, symbols in correlation_groups.items():
            if symbol in symbols:
                target_group = group
                break
        
        if not target_group:
            return True  # No correlation risk for unknown assets
        
        # Calculate current exposure to this group
        group_symbols = correlation_groups[target_group]
        current_group_value = sum(
            holding.current_value or Decimal('0')
            for holding in holdings
            if holding.symbol in group_symbols
        )
        
        # Add potential new exposure
        if transaction_type == TransactionType.BUY:
            new_group_value = current_group_value + amount
        else:
            new_group_value = current_group_value  # Selling reduces exposure
        
        # Check if group exposure exceeds limit
        group_percentage = (new_group_value / wallet.total_portfolio_value) * 100
        
        return group_percentage <= limits.max_correlation_exposure
    
    def get_user_risk_limits(self, db: Session, user_id: int) -> RiskLimits:
        """Get user-specific risk limits (could be stored in database)"""
        # For now, return default limits
        # In production, this could be customized per user based on their risk profile
        return self.default_limits
    
    def calculate_risk_metrics(self, db: Session, wallet_id: int) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            raise ValueError("Wallet not found")
        
        holdings = db.query(Holding).filter(Holding.wallet_id == wallet_id).all()
        
        # Calculate cash percentage
        cash_percentage = (wallet.usd_balance / wallet.total_portfolio_value) * 100
        
        # Find largest position
        largest_position_value = max(
            (holding.current_value or Decimal('0') for holding in holdings),
            default=Decimal('0')
        )
        largest_position_percentage = (largest_position_value / wallet.total_portfolio_value) * 100
        
        # Calculate daily P&L percentage
        daily_pnl_percentage = (wallet.daily_pnl / wallet.total_portfolio_value) * 100
        
        # Calculate total P&L percentage
        initial_balance = Decimal('10000.00')
        total_pnl_percentage = ((wallet.total_portfolio_value - initial_balance) / initial_balance) * 100
        
        # Calculate concentration risk score
        concentration_risk_score = self.calculate_concentration_risk_score(holdings, wallet.total_portfolio_value)
        
        # Calculate overall risk score (0-100, higher = riskier)
        risk_score = self.calculate_overall_risk_score(
            cash_percentage, largest_position_percentage, concentration_risk_score,
            abs(daily_pnl_percentage), wallet.max_drawdown
        )
        
        return RiskMetrics(
            total_portfolio_value=wallet.total_portfolio_value,
            cash_percentage=cash_percentage,
            largest_position_percentage=largest_position_percentage,
            daily_pnl_percentage=daily_pnl_percentage,
            total_pnl_percentage=total_pnl_percentage,
            concentration_risk_score=concentration_risk_score,
            risk_score=risk_score
        )
    
    def calculate_concentration_risk_score(self, holdings: List[Holding], total_value: Decimal) -> Decimal:
        """Calculate concentration risk score (0-100)"""
        if not holdings or total_value <= 0:
            return Decimal('0')
        
        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        hhi = sum(
            ((holding.current_value or Decimal('0')) / total_value) ** 2
            for holding in holdings
        )
        
        # Convert to 0-100 scale (higher = more concentrated)
        concentration_score = hhi * 100
        
        return min(concentration_score, Decimal('100'))
    
    def calculate_overall_risk_score(self, cash_pct: Decimal, largest_pos_pct: Decimal,
                                   concentration_score: Decimal, daily_volatility: Decimal,
                                   max_drawdown: Decimal) -> Decimal:
        """Calculate overall risk score (0-100)"""
        
        # Risk factors (higher values = higher risk)
        cash_risk = max(Decimal('0'), Decimal('20') - cash_pct)  # Risk increases as cash decreases below 20%
        position_risk = max(Decimal('0'), largest_pos_pct - Decimal('15'))  # Risk increases above 15% position
        concentration_risk = concentration_score
        volatility_risk = min(daily_volatility * 10, Decimal('30'))  # Cap at 30
        drawdown_risk = min(max_drawdown * 2, Decimal('50'))  # Cap at 50
        
        # Weighted average
        risk_score = (
            cash_risk * Decimal('0.2') +
            position_risk * Decimal('0.25') +
            concentration_risk * Decimal('0.25') +
            volatility_risk * Decimal('0.15') +
            drawdown_risk * Decimal('0.15')
        )
        
        return min(risk_score, Decimal('100'))
    
    def get_risk_recommendations(self, db: Session, wallet_id: int) -> List[str]:
        """Get risk management recommendations"""
        
        metrics = self.calculate_risk_metrics(db, wallet_id)
        recommendations = []
        
        # Cash reserve recommendations
        if metrics.cash_percentage < 10:
            recommendations.append(f"Consider increasing cash reserves (currently {metrics.cash_percentage:.1f}%)")
        
        # Position size recommendations
        if metrics.largest_position_percentage > 25:
            recommendations.append(f"Largest position is {metrics.largest_position_percentage:.1f}% - consider reducing concentration")
        
        # Overall risk recommendations
        if metrics.risk_score > 70:
            recommendations.append("High risk portfolio - consider reducing position sizes and increasing diversification")
        elif metrics.risk_score > 50:
            recommendations.append("Moderate risk portfolio - monitor positions closely")
        
        # Concentration recommendations
        if metrics.concentration_risk_score > 60:
            recommendations.append("High concentration risk - consider diversifying across more assets")
        
        # Performance recommendations
        if metrics.daily_pnl_percentage < -3:
            recommendations.append("Significant daily loss - consider reviewing trading strategy")
        
        if not recommendations:
            recommendations.append("Risk profile looks healthy - continue monitoring")
        
        return recommendations
    
    def emergency_risk_check(self, db: Session, wallet_id: int) -> Dict[str, Any]:
        """Emergency risk check - returns immediate actions needed"""
        
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
        if not wallet:
            return {"error": "Wallet not found"}
        
        metrics = self.calculate_risk_metrics(db, wallet_id)
        limits = self.default_limits
        
        emergency_actions = []
        risk_level = "LOW"
        
        # Check for emergency conditions
        if metrics.daily_pnl_percentage < -limits.max_daily_loss_percentage:
            emergency_actions.append("HALT_TRADING")
            risk_level = "CRITICAL"
        
        if metrics.total_pnl_percentage < -limits.max_total_loss_percentage:
            emergency_actions.append("LIQUIDATE_POSITIONS")
            risk_level = "CRITICAL"
        
        if metrics.largest_position_percentage > 40:
            emergency_actions.append("REDUCE_LARGEST_POSITION")
            risk_level = "HIGH" if risk_level != "CRITICAL" else risk_level
        
        if metrics.cash_percentage < 5:
            emergency_actions.append("INCREASE_CASH_RESERVES")
            risk_level = "HIGH" if risk_level not in ["CRITICAL", "HIGH"] else risk_level
        
        return {
            "risk_level": risk_level,
            "emergency_actions": emergency_actions,
            "metrics": metrics,
            "recommendations": self.get_risk_recommendations(db, wallet_id)
        }


# Global risk management service instance
risk_management_service = RiskManagementService()
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from decimal import Decimal

from app.core.auth import get_current_active_user, require_role
from app.db.database import get_sync_db
from app.models.user import User, UserRole
from app.models.wallet import TransactionType
from app.schemas.trading import (
    WalletResponse, PortfolioSummary, TradeRequest, TradeResponse,
    TransactionResponse, HoldingResponse
)
from app.services.trading_service import trading_service


router = APIRouter()


@router.post("/wallet/create", response_model=WalletResponse)
def create_wallet(
    *,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create a new trading wallet for the current user"""
    try:
        wallet = trading_service.create_wallet(db=db, user_id=current_user.id)
        return {
            "id": wallet.id,
            "user_id": wallet.user_id,
            "usd_balance": float(wallet.usd_balance),
            "total_portfolio_value": float(wallet.total_portfolio_value),
            "total_profit_loss": float(wallet.total_profit_loss),
            "total_trades": wallet.total_trades,
            "win_rate": float(wallet.win_rate),
            "created_at": wallet.created_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create wallet: {str(e)}"
        )


@router.get("/wallet", response_model=WalletResponse)
def get_wallet(
    *,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user's wallet"""
    wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found. Create a wallet first."
        )
    
    return {
        "id": wallet.id,
        "user_id": wallet.user_id,
        "usd_balance": float(wallet.usd_balance),
        "total_portfolio_value": float(wallet.total_portfolio_value),
        "total_profit_loss": float(wallet.total_profit_loss),
        "total_trades": wallet.total_trades,
        "win_rate": float(wallet.win_rate),
        "created_at": wallet.created_at
    }


@router.get("/portfolio", response_model=PortfolioSummary)
def get_portfolio_summary(
    *,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get comprehensive portfolio summary with P&L"""
    wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found. Create a wallet first."
        )
    
    try:
        portfolio_data = trading_service.get_portfolio_summary(db=db, wallet_id=wallet.id)
        return portfolio_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio summary: {str(e)}"
        )


@router.post("/buy", response_model=TradeResponse)
def buy_cryptocurrency(
    *,
    db: Session = Depends(get_sync_db),
    trade_request: TradeRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Buy cryptocurrency with USD"""
    wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found. Create a wallet first."
        )
    
    try:
        result = trading_service.place_market_order(
            db=db,
            wallet_id=wallet.id,
            symbol=trade_request.symbol.upper(),
            transaction_type=TransactionType.BUY,
            amount=Decimal(str(trade_request.amount))
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute buy order: {str(e)}"
        )


@router.post("/sell", response_model=TradeResponse)
def sell_cryptocurrency(
    *,
    db: Session = Depends(get_sync_db),
    trade_request: TradeRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Sell cryptocurrency for USD"""
    wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found. Create a wallet first."
        )
    
    try:
        result = trading_service.place_market_order(
            db=db,
            wallet_id=wallet.id,
            symbol=trade_request.symbol.upper(),
            transaction_type=TransactionType.SELL,
            amount=Decimal(str(trade_request.amount))  # This is quantity for sell orders
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute sell order: {str(e)}"
        )


@router.post("/simulate-market")
def simulate_market_movement(
    *,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
) -> Any:
    """Simulate market movement (Admin only)"""
    try:
        result = trading_service.simulate_market_movement(db=db)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to simulate market movement: {str(e)}"
        )


@router.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(
    *,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(50, ge=1, le=1000),
    transaction_type: Optional[str] = Query(None)
) -> Any:
    """Get user's transaction history"""
    wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found. Create a wallet first."
        )
    
    from app.models.wallet import Transaction
    from sqlalchemy import desc
    
    query = db.query(Transaction).filter(Transaction.wallet_id == wallet.id)
    
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    
    transactions = query.order_by(desc(Transaction.created_at)).limit(limit).all()
    
    return [
        {
            "id": tx.id,
            "transaction_type": tx.transaction_type.value,
            "symbol": tx.symbol,
            "quantity": float(tx.quantity or 0),
            "price": float(tx.price or 0),
            "total_amount": float(tx.total_amount),
            "fee": float(tx.fee),
            "realized_pnl": float(tx.realized_pnl or 0),
            "realized_pnl_percentage": float(tx.realized_pnl_percentage or 0),
            "created_at": tx.created_at
        }
        for tx in transactions
    ]


@router.get("/holdings", response_model=List[HoldingResponse])
def get_holdings(
    *,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get user's current holdings"""
    wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found. Create a wallet first."
        )
    
    from app.models.wallet import Holding
    
    holdings = db.query(Holding).filter(Holding.wallet_id == wallet.id).all()
    
    return [
        {
            "id": holding.id,
            "symbol": holding.symbol,
            "quantity": float(holding.quantity),
            "average_buy_price": float(holding.average_buy_price),
            "current_price": float(holding.current_price or 0),
            "total_cost": float(holding.total_cost),
            "current_value": float(holding.current_value or 0),
            "unrealized_pnl": float(holding.unrealized_pnl),
            "unrealized_pnl_percentage": float(holding.unrealized_pnl_percentage),
            "first_purchase_at": holding.first_purchase_at
        }
        for holding in holdings
    ]


@router.post("/update-portfolio")
def update_portfolio_values(
    *,
    db: Session = Depends(get_sync_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update portfolio values with current market prices"""
    wallet = trading_service.get_wallet(db=db, user_id=current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found. Create a wallet first."
        )
    
    try:
        result = trading_service.update_portfolio_values(db=db, wallet_id=wallet.id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update portfolio values: {str(e)}"
        )
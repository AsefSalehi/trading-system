from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, require_role
from app.db.database import get_sync_db
from app.models.user import User, UserRole
from app.schemas.portfolio import (
    Portfolio as PortfolioSchema,
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioRiskAnalysis,
    PortfolioRecommendation,
)
from app.services.portfolio_service import PortfolioService


router = APIRouter()
portfolio_service = PortfolioService()


@router.post("/", response_model=PortfolioSchema)
def create_portfolio(
    *,
    db: Session = Depends(get_sync_db),
    portfolio_in: PortfolioCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a new portfolio"""
    portfolio = portfolio_service.create_portfolio(
        db=db, portfolio_data=portfolio_in, user_id=current_user.id
    )
    return portfolio


@router.get("/", response_model=List[PortfolioSchema])
def get_portfolios(
    db: Session = Depends(get_sync_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get user's portfolios"""
    portfolios = portfolio_service.get_user_portfolios(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return portfolios


@router.get("/{portfolio_id}", response_model=PortfolioSchema)
def get_portfolio(
    *,
    db: Session = Depends(get_sync_db),
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get specific portfolio"""
    portfolio = portfolio_service.get_portfolio(db=db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    
    # Check ownership or admin access
    if portfolio.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioSchema)
def update_portfolio(
    *,
    db: Session = Depends(get_sync_db),
    portfolio_id: int,
    portfolio_in: PortfolioUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update portfolio"""
    portfolio = portfolio_service.get_portfolio(db=db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    
    # Check ownership
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    
    portfolio = portfolio_service.update_portfolio(
        db=db, portfolio_id=portfolio_id, portfolio_data=portfolio_in
    )
    return portfolio


@router.delete("/{portfolio_id}")
def delete_portfolio(
    *,
    db: Session = Depends(get_sync_db),
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Delete portfolio"""
    portfolio = portfolio_service.get_portfolio(db=db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    
    # Check ownership
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    
    success = portfolio_service.delete_portfolio(db=db, portfolio_id=portfolio_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete portfolio"
        )
    
    return {"message": "Portfolio deleted successfully"}


@router.get("/{portfolio_id}/risk-analysis", response_model=PortfolioRiskAnalysis)
def get_portfolio_risk_analysis(
    *,
    db: Session = Depends(get_sync_db),
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get portfolio risk analysis"""
    portfolio = portfolio_service.get_portfolio(db=db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    
    # Check ownership or analyst access
    if (portfolio.user_id != current_user.id and 
        current_user.role not in [UserRole.ADMIN, UserRole.ANALYST]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    
    risk_analysis = portfolio_service.calculate_portfolio_risk(
        db=db, portfolio_id=portfolio_id
    )
    return risk_analysis


@router.get("/{portfolio_id}/recommendations", response_model=List[PortfolioRecommendation])
def get_portfolio_recommendations(
    *,
    db: Session = Depends(get_sync_db),
    portfolio_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get portfolio recommendations"""
    portfolio = portfolio_service.get_portfolio(db=db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    
    # Check ownership or analyst access
    if (portfolio.user_id != current_user.id and 
        current_user.role not in [UserRole.ADMIN, UserRole.ANALYST]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    
    recommendations = portfolio_service.generate_recommendations(
        db=db, portfolio_id=portfolio_id
    )
    return recommendations


@router.post("/{portfolio_id}/rebalance")
def rebalance_portfolio(
    *,
    db: Session = Depends(get_sync_db),
    portfolio_id: int,
    target_risk_level: float = Query(..., ge=0, le=100, description="Target risk level (0-100)"),
    current_user: User = Depends(require_role(UserRole.TRADER)),
) -> Any:
    """Rebalance portfolio to target risk level"""
    portfolio = portfolio_service.get_portfolio(db=db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )
    
    # Check ownership
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    
    rebalance_plan = portfolio_service.create_rebalance_plan(
        db=db, portfolio_id=portfolio_id, target_risk_level=target_risk_level
    )
    
    return {
        "message": "Rebalance plan created",
        "plan": rebalance_plan,
        "estimated_risk_reduction": rebalance_plan.get("risk_reduction", 0),
    }
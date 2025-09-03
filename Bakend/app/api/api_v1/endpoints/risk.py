from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user, require_role
from app.db.database import get_sync_db
from app.models.user import User, UserRole
from app.models.risk_assessment import RiskScore, RiskAlert
from app.schemas.risk import (
    RiskScore as RiskScoreSchema,
    RiskAlert as RiskAlertSchema,
    RiskAssessmentRequest,
    RiskAlertCreate,
)
from app.services.risk_service import RiskService


router = APIRouter()
risk_service = RiskService()


@router.post("/assess", response_model=List[RiskScoreSchema])
def assess_cryptocurrency_risk(
    *,
    db: Session = Depends(get_sync_db),
    request: RiskAssessmentRequest,
    current_user: User = Depends(require_role(UserRole.ANALYST)),
) -> Any:
    """Assess risk for cryptocurrencies (Analyst+ role required)"""
    try:
        risk_scores = risk_service.calculate_risk_scores(
            db=db,
            crypto_ids=request.cryptocurrency_ids,
            window_days=request.window_days,
        )
        return risk_scores
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk assessment failed: {str(e)}",
        )


@router.get("/scores/{crypto_id}", response_model=RiskScoreSchema)
def get_risk_score(
    *,
    db: Session = Depends(get_sync_db),
    crypto_id: int,
    latest: bool = Query(True, description="Get latest risk score"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get risk score for a cryptocurrency"""
    risk_score = risk_service.get_risk_score(db=db, crypto_id=crypto_id, latest=latest)
    if not risk_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Risk score not found"
        )
    return risk_score


@router.get("/scores", response_model=List[RiskScoreSchema])
def get_risk_scores(
    db: Session = Depends(get_sync_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    crypto_id: Optional[int] = Query(None),
    min_risk_score: Optional[float] = Query(None, ge=0, le=100),
    max_risk_score: Optional[float] = Query(None, ge=0, le=100),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get risk scores with filtering"""
    query = db.query(RiskScore)

    if crypto_id:
        query = query.filter(RiskScore.cryptocurrency_id == crypto_id)

    if min_risk_score is not None:
        query = query.filter(RiskScore.overall_risk_score >= min_risk_score)

    if max_risk_score is not None:
        query = query.filter(RiskScore.overall_risk_score <= max_risk_score)

    risk_scores = query.offset(skip).limit(limit).all()
    return risk_scores


@router.post("/alerts", response_model=RiskAlertSchema)
def create_risk_alert(
    *,
    db: Session = Depends(get_sync_db),
    alert_in: RiskAlertCreate,
    current_user: User = Depends(require_role(UserRole.TRADER)),
) -> Any:
    """Create a risk alert (Trader+ role required)"""
    try:
        alert = risk_service.create_risk_alert(
            db=db,
            crypto_id=alert_in.cryptocurrency_id,
            alert_type=alert_in.alert_type,
            severity=alert_in.severity,
            threshold_value=alert_in.threshold_value,
            current_value=alert_in.current_value,
            title=alert_in.title,
            message=alert_in.message,
            user_id=current_user.id if alert_in.user_specific else None,
        )
        return alert
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}",
        )


@router.get("/alerts", response_model=List[RiskAlertSchema])
def get_risk_alerts(
    db: Session = Depends(get_sync_db),
    crypto_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    user_specific: bool = Query(False, description="Get user-specific alerts only"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get risk alerts"""
    user_id = current_user.id if user_specific else None

    # Non-admin users can only see their own alerts or system-wide alerts
    if (
        current_user.role not in [UserRole.ADMIN, UserRole.ANALYST]
        and not user_specific
    ):
        user_id = current_user.id

    alerts = risk_service.get_active_alerts(db=db, user_id=user_id, crypto_id=crypto_id)

    # Apply additional filters
    if severity:
        alerts = [a for a in alerts if a.severity == severity]

    if alert_type:
        alerts = [a for a in alerts if a.alert_type == alert_type]

    return alerts


@router.put("/alerts/{alert_id}/resolve")
def resolve_risk_alert(
    *,
    db: Session = Depends(get_sync_db),
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Resolve a risk alert"""
    # Check if alert exists and user has permission
    alert = db.query(RiskAlert).filter(RiskAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found"
        )

    # Users can only resolve their own alerts unless they're admin/analyst
    if alert.user_id != current_user.id and current_user.role not in [
        UserRole.ADMIN,
        UserRole.ANALYST,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    success = risk_service.resolve_alert(db=db, alert_id=alert_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert",
        )

    return {"message": "Alert resolved successfully"}


@router.get("/dashboard")
def get_risk_dashboard(
    db: Session = Depends(get_sync_db), current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get risk dashboard data"""
    # Get high-risk cryptocurrencies
    high_risk_cryptos = (
        db.query(RiskScore)
        .filter(RiskScore.overall_risk_score >= 70)
        .order_by(RiskScore.overall_risk_score.desc())
        .limit(10)
        .all()
    )

    # Get active alerts count
    user_id = (
        current_user.id
        if current_user.role not in [UserRole.ADMIN, UserRole.ANALYST]
        else None
    )
    active_alerts = risk_service.get_active_alerts(db=db, user_id=user_id)

    # Get alert counts by severity
    alert_counts = {
        "critical": len([a for a in active_alerts if a.severity == "critical"]),
        "high": len([a for a in active_alerts if a.severity == "high"]),
        "medium": len([a for a in active_alerts if a.severity == "medium"]),
        "low": len([a for a in active_alerts if a.severity == "low"]),
    }

    return {
        "high_risk_cryptocurrencies": high_risk_cryptos,
        "active_alerts_count": len(active_alerts),
        "alert_counts_by_severity": alert_counts,
        "recent_alerts": active_alerts[:5],  # Last 5 alerts
    }

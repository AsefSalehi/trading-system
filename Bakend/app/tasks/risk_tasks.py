from datetime import datetime, timedelta
from typing import List, Optional
from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.logging import logger
from app.db.database import AsyncSessionLocal, get_db
from app.services.risk_service import RiskService
from app.models.cryptocurrency import Cryptocurrency
from app.models.risk_assessment import RiskScore, RiskAlert
from app.models.user import User


@celery_app.task(bind=True, name="app.tasks.risk_tasks.calculate_daily_risk_scores")
def calculate_daily_risk_scores(self, limit: int = 100, window_days: int = 30) -> dict:
    """
    Background task to calculate daily risk scores for top cryptocurrencies

    Args:
        limit: Number of top cryptocurrencies to assess
        window_days: Number of days to analyze for risk calculation

    Returns:
        Dict with task results
    """
    try:
        logger.info(
            f"Starting daily risk score calculation - Limit: {limit}, Window: {window_days} days"
        )

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Calculating risk scores", "progress": 10},
            )

        import asyncio

        result = asyncio.run(_calculate_risk_scores_async(limit, window_days))

        logger.info(f"Daily risk score calculation completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in calculate_daily_risk_scores task: {e}")
        if current_task:
            current_task.update_state(state="FAILURE", meta={"error": str(e)})
        raise


async def _calculate_risk_scores_async(limit: int, window_days: int) -> dict:
    """Async helper function for risk score calculation"""
    # Use sync database session for risk service
    from app.db.database import SessionLocal

    try:
        db = SessionLocal()
        risk_service = RiskService()

        # Get top cryptocurrencies by market cap
        top_cryptos = (
            db.query(Cryptocurrency)
            .filter(Cryptocurrency.is_active == True)
            .order_by(Cryptocurrency.market_cap_rank)
            .limit(limit)
            .all()
        )

        crypto_ids = [crypto.id for crypto in top_cryptos]

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "status": f"Processing {len(crypto_ids)} cryptocurrencies",
                    "progress": 30,
                },
            )

        # Calculate risk scores
        risk_scores = risk_service.calculate_risk_scores(
            db=db, crypto_ids=crypto_ids, window_days=window_days
        )

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={
                    "status": "Risk scores calculated, checking for alerts",
                    "progress": 80,
                },
            )

        # Check for high-risk alerts
        high_risk_count = 0
        for risk_score in risk_scores:
            if risk_score.overall_risk_score >= 80:  # Very high risk threshold
                high_risk_count += 1
                # Create system alert for very high risk
                risk_service.create_risk_alert(
                    db=db,
                    crypto_id=risk_score.cryptocurrency_id,
                    alert_type="high_risk",
                    severity="high",
                    threshold_value=80.0,
                    current_value=risk_score.overall_risk_score,
                    title=f"High Risk Alert",
                    message=f"Cryptocurrency has very high risk score: {risk_score.overall_risk_score:.1f}/100",
                    user_id=None,  # System-wide alert
                )

        db.close()

        return {
            "status": "success",
            "processed_count": len(risk_scores),
            "high_risk_alerts_created": high_risk_count,
            "window_days": window_days,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        if "db" in locals():
            db.close()
        raise e


@celery_app.task(bind=True, name="app.tasks.risk_tasks.monitor_risk_thresholds")
def monitor_risk_thresholds(self) -> dict:
    """
    Background task to monitor risk thresholds and create alerts

    Returns:
        Dict with monitoring results
    """
    try:
        logger.info("Starting risk threshold monitoring task")

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Monitoring risk thresholds", "progress": 50},
            )

        import asyncio

        result = asyncio.run(_monitor_risk_thresholds_async())

        logger.info(f"Risk threshold monitoring completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in monitor_risk_thresholds task: {e}")
        if current_task:
            current_task.update_state(state="FAILURE", meta={"error": str(e)})
        raise


async def _monitor_risk_thresholds_async() -> dict:
    """Async helper function for risk threshold monitoring"""
    from app.db.database import SessionLocal

    try:
        db = SessionLocal()
        risk_service = RiskService()

        # Get latest risk scores
        latest_scores = (
            db.query(RiskScore)
            .filter(
                RiskScore.calculation_timestamp
                >= datetime.utcnow() - timedelta(hours=24)
            )
            .all()
        )

        alerts_created = 0
        volatility_alerts = 0
        liquidity_alerts = 0

        for score in latest_scores:
            # Check volatility threshold
            if score.volatility_score >= 85:
                risk_service.create_risk_alert(
                    db=db,
                    crypto_id=score.cryptocurrency_id,
                    alert_type="volatility",
                    severity="high" if score.volatility_score >= 90 else "medium",
                    threshold_value=85.0,
                    current_value=score.volatility_score,
                    title="High Volatility Alert",
                    message=f"Cryptocurrency showing high volatility: {score.volatility_score:.1f}/100",
                )
                volatility_alerts += 1
                alerts_created += 1

            # Check liquidity threshold
            if score.liquidity_score >= 80:
                risk_service.create_risk_alert(
                    db=db,
                    crypto_id=score.cryptocurrency_id,
                    alert_type="liquidity",
                    severity="high" if score.liquidity_score >= 90 else "medium",
                    threshold_value=80.0,
                    current_value=score.liquidity_score,
                    title="Low Liquidity Alert",
                    message=f"Cryptocurrency showing low liquidity: {score.liquidity_score:.1f}/100",
                )
                liquidity_alerts += 1
                alerts_created += 1

        db.close()

        return {
            "status": "success",
            "scores_monitored": len(latest_scores),
            "total_alerts_created": alerts_created,
            "volatility_alerts": volatility_alerts,
            "liquidity_alerts": liquidity_alerts,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        if "db" in locals():
            db.close()
        raise e


@celery_app.task(bind=True, name="app.tasks.risk_tasks.cleanup_old_risk_data")
def cleanup_old_risk_data(self, days_to_keep: int = 90) -> dict:
    """
    Background task to cleanup old risk scores and resolved alerts

    Args:
        days_to_keep: Number of days of risk data to keep

    Returns:
        Dict with cleanup results
    """
    try:
        logger.info(f"Starting risk data cleanup task - keeping {days_to_keep} days")

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Cleaning up old risk data", "progress": 50},
            )

        import asyncio

        result = asyncio.run(_cleanup_risk_data_async(days_to_keep))

        logger.info(f"Risk data cleanup completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in cleanup_old_risk_data task: {e}")
        if current_task:
            current_task.update_state(state="FAILURE", meta={"error": str(e)})
        raise


async def _cleanup_risk_data_async(days_to_keep: int) -> dict:
    """Async helper function for risk data cleanup"""
    from app.db.database import SessionLocal

    try:
        db = SessionLocal()
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Delete old risk scores
        old_scores = (
            db.query(RiskScore)
            .filter(RiskScore.calculation_timestamp < cutoff_date)
            .all()
        )
        scores_deleted = len(old_scores)

        for score in old_scores:
            db.delete(score)

        # Delete resolved alerts older than cutoff
        old_alerts = (
            db.query(RiskAlert)
            .filter(RiskAlert.is_active == False, RiskAlert.resolved_at < cutoff_date)
            .all()
        )
        alerts_deleted = len(old_alerts)

        for alert in old_alerts:
            db.delete(alert)

        db.commit()
        db.close()

        return {
            "status": "success",
            "risk_scores_deleted": scores_deleted,
            "alerts_deleted": alerts_deleted,
            "cutoff_date": cutoff_date.isoformat(),
            "days_kept": days_to_keep,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        if "db" in locals():
            db.rollback()
            db.close()
        raise e


@celery_app.task(bind=True, name="app.tasks.risk_tasks.generate_risk_report")
def generate_risk_report(self, user_id: Optional[int] = None) -> dict:
    """
    Background task to generate comprehensive risk report

    Args:
        user_id: Optional user ID for personalized report

    Returns:
        Dict with report data
    """
    try:
        logger.info(f"Starting risk report generation task for user {user_id}")

        if current_task:
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Generating risk report", "progress": 50},
            )

        import asyncio

        result = asyncio.run(_generate_risk_report_async(user_id))

        logger.info("Risk report generation completed")
        return result

    except Exception as e:
        logger.error(f"Error in generate_risk_report task: {e}")
        if current_task:
            current_task.update_state(state="FAILURE", meta={"error": str(e)})
        raise


async def _generate_risk_report_async(user_id: Optional[int]) -> dict:
    """Async helper function for risk report generation"""
    from app.db.database import SessionLocal

    try:
        db = SessionLocal()

        # Get latest risk scores
        latest_scores = (
            db.query(RiskScore)
            .filter(
                RiskScore.calculation_timestamp
                >= datetime.utcnow() - timedelta(hours=24)
            )
            .order_by(RiskScore.overall_risk_score.desc())
            .all()
        )

        # Calculate risk distribution
        risk_distribution = {
            "low_risk": len([s for s in latest_scores if s.overall_risk_score < 30]),
            "medium_risk": len(
                [s for s in latest_scores if 30 <= s.overall_risk_score < 70]
            ),
            "high_risk": len([s for s in latest_scores if s.overall_risk_score >= 70]),
        }

        # Get active alerts
        active_alerts = db.query(RiskAlert).filter(RiskAlert.is_active == True)
        if user_id:
            active_alerts = active_alerts.filter(
                (RiskAlert.user_id == user_id) | (RiskAlert.user_id.is_(None))
            )
        active_alerts = active_alerts.all()

        # Top risky cryptocurrencies
        top_risky = latest_scores[:10] if latest_scores else []

        db.close()

        return {
            "status": "success",
            "user_id": user_id,
            "total_assessed": len(latest_scores),
            "risk_distribution": risk_distribution,
            "active_alerts_count": len(active_alerts),
            "top_risky_count": len(top_risky),
            "average_risk_score": (
                sum(s.overall_risk_score for s in latest_scores) / len(latest_scores)
                if latest_scores
                else 0
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        if "db" in locals():
            db.close()
        raise e

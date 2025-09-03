import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.cryptocurrency import Cryptocurrency, PriceHistory
from app.models.risk_assessment import RiskScore, RiskAlert
from app.models.user import User


class RiskAssessmentEngine:
    """Risk assessment engine for cryptocurrency analysis"""

    MODEL_VERSION = "1.0.0"

    def __init__(self):
        self.weights = {
            "volatility": 0.3,
            "liquidity": 0.2,
            "market_cap": 0.2,
            "technical": 0.2,
            "sentiment": 0.1,
        }

    def calculate_volatility_score(
        self, price_data: List[float], window_days: int = 30
    ) -> Tuple[float, float]:
        """Calculate volatility score (0-100, higher = more volatile/risky)"""
        if len(price_data) < 2:
            return 50.0, 0.5  # Default medium risk with low confidence

        # Calculate daily returns
        prices = np.array(price_data)
        returns = np.diff(prices) / prices[:-1]

        # Calculate volatility (standard deviation of returns)
        volatility = np.std(returns) * np.sqrt(365)  # Annualized volatility

        # Convert to 0-100 scale (typical crypto volatility ranges from 0.5 to 3.0)
        volatility_score = min(100, (volatility / 3.0) * 100)

        # Confidence based on data points
        confidence = min(1.0, len(price_data) / window_days)

        return float(volatility_score), float(confidence)

    def calculate_liquidity_score(
        self, volume_data: List[float], market_cap: float
    ) -> Tuple[float, float]:
        """Calculate liquidity score (0-100, higher = less liquid/more risky)"""
        if not volume_data or market_cap <= 0:
            return 70.0, 0.3  # Default high risk with low confidence

        avg_volume = np.mean(volume_data)

        # Volume to market cap ratio
        volume_ratio = avg_volume / market_cap if market_cap > 0 else 0

        # Convert to risk score (lower liquidity = higher risk)
        # Typical good liquidity ratio is > 0.1, poor is < 0.01
        if volume_ratio >= 0.1:
            liquidity_score = 20.0  # Low risk
        elif volume_ratio >= 0.05:
            liquidity_score = 40.0  # Medium-low risk
        elif volume_ratio >= 0.01:
            liquidity_score = 60.0  # Medium-high risk
        else:
            liquidity_score = 90.0  # High risk

        confidence = 0.8 if len(volume_data) >= 7 else 0.5

        return float(liquidity_score), float(confidence)

    def calculate_market_cap_score(self, market_cap: float) -> Tuple[float, float]:
        """Calculate market cap score (0-100, higher = smaller cap/more risky)"""
        if market_cap <= 0:
            return 90.0, 0.9  # High risk for unknown market cap

        # Market cap categories (in USD)
        if market_cap >= 10_000_000_000:  # > $10B (Large cap)
            score = 20.0
        elif market_cap >= 2_000_000_000:  # $2B-$10B (Mid cap)
            score = 40.0
        elif market_cap >= 300_000_000:  # $300M-$2B (Small cap)
            score = 60.0
        elif market_cap >= 50_000_000:  # $50M-$300M (Micro cap)
            score = 80.0
        else:  # < $50M (Nano cap)
            score = 95.0

        return float(score), 0.9  # High confidence in market cap data

    def calculate_technical_score(
        self,
        price_data: List[float],
        current_price: float,
        ath: Optional[float],
        atl: Optional[float],
    ) -> Tuple[float, float]:
        """Calculate technical analysis score"""
        if len(price_data) < 10:
            return 50.0, 0.3

        prices = np.array(price_data)
        score_components = []

        # Price trend (last 7 days vs previous 7 days)
        if len(prices) >= 14:
            recent_avg = np.mean(prices[-7:])
            previous_avg = np.mean(prices[-14:-7])
            trend_score = 30 if recent_avg > previous_avg else 70
            score_components.append(trend_score)

        # Distance from ATH/ATL
        if ath and current_price > 0:
            ath_distance = (ath - current_price) / ath
            # Higher distance from ATH = lower risk
            ath_score = min(100, ath_distance * 100)
            score_components.append(ath_score)

        if atl and current_price > 0:
            atl_distance = (
                (current_price - atl) / current_price if current_price > atl else 0
            )
            # Lower distance from ATL = higher risk
            atl_score = max(0, 100 - (atl_distance * 100))
            score_components.append(atl_score)

        # Moving average position
        if len(prices) >= 20:
            ma_20 = np.mean(prices[-20:])
            ma_score = 30 if current_price > ma_20 else 70
            score_components.append(ma_score)

        technical_score = np.mean(score_components) if score_components else 50.0
        confidence = min(1.0, len(score_components) / 3)

        return float(technical_score), float(confidence)

    def calculate_sentiment_score(self, symbol: str) -> Tuple[Optional[float], float]:
        """Calculate sentiment score (-100 to 100, negative = bearish/risky)"""
        # Placeholder for sentiment analysis
        # In a real implementation, this would integrate with news APIs, social media, etc.
        return None, 0.0

    def calculate_composite_score(
        self, scores: Dict[str, Tuple[float, float]]
    ) -> Tuple[float, float]:
        """Calculate weighted composite risk score"""
        weighted_score = 0.0
        total_weight = 0.0
        confidence_sum = 0.0

        for component, (score, confidence) in scores.items():
            if score is not None and component in self.weights:
                weight = self.weights[component]
                weighted_score += score * weight * confidence
                total_weight += weight * confidence
                confidence_sum += confidence

        if total_weight == 0:
            return 50.0, 0.1  # Default medium risk with very low confidence

        final_score = weighted_score / total_weight
        avg_confidence = confidence_sum / len(
            [s for s in scores.values() if s[0] is not None]
        )

        return float(final_score), float(avg_confidence)

    def assess_cryptocurrency_risk(
        self, db: Session, crypto_id: int, window_days: int = 30
    ) -> Optional[RiskScore]:
        """Assess risk for a specific cryptocurrency"""
        # Get cryptocurrency data
        crypto = db.query(Cryptocurrency).filter(Cryptocurrency.id == crypto_id).first()
        if not crypto:
            return None

        # Get price history
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=window_days)

        price_history = (
            db.query(PriceHistory)
            .filter(
                and_(
                    PriceHistory.cryptocurrency_id == crypto_id,
                    PriceHistory.timestamp >= start_date,
                    PriceHistory.timestamp <= end_date,
                )
            )
            .order_by(PriceHistory.timestamp)
            .all()
        )

        if not price_history:
            return None

        # Extract data for analysis
        prices = [float(ph.price) for ph in price_history]
        volumes = [float(ph.total_volume) for ph in price_history if ph.total_volume]
        current_price = (
            float(crypto.current_price) if crypto.current_price else prices[-1]
        )
        market_cap = float(crypto.market_cap) if crypto.market_cap else 0
        ath = float(crypto.ath) if crypto.ath else None
        atl = float(crypto.atl) if crypto.atl else None

        # Calculate individual scores
        volatility_score, vol_confidence = self.calculate_volatility_score(
            prices, window_days
        )
        liquidity_score, liq_confidence = self.calculate_liquidity_score(
            volumes, market_cap
        )
        market_cap_score, mc_confidence = self.calculate_market_cap_score(market_cap)
        technical_score, tech_confidence = self.calculate_technical_score(
            prices, current_price, ath, atl
        )
        sentiment_score, sent_confidence = self.calculate_sentiment_score(crypto.symbol)

        # Compile scores
        scores = {
            "volatility": (volatility_score, vol_confidence),
            "liquidity": (liquidity_score, liq_confidence),
            "market_cap": (market_cap_score, mc_confidence),
            "technical": (technical_score, tech_confidence),
            "sentiment": (sentiment_score, sent_confidence),
        }

        # Calculate composite score
        overall_score, overall_confidence = self.calculate_composite_score(scores)

        # Generate risk factors and recommendations
        risk_factors = self._generate_risk_factors(scores, crypto)
        recommendations = self._generate_recommendations(overall_score, risk_factors)

        # Create risk score record
        risk_score = RiskScore(
            cryptocurrency_id=crypto_id,
            volatility_score=volatility_score,
            liquidity_score=liquidity_score,
            market_cap_score=market_cap_score,
            sentiment_score=sentiment_score,
            technical_score=technical_score,
            overall_risk_score=overall_score,
            confidence_interval=overall_confidence,
            model_version=self.MODEL_VERSION,
            data_window_days=window_days,
            risk_factors=risk_factors,
            recommendations=recommendations,
        )

        return risk_score

    def _generate_risk_factors(self, scores: Dict, crypto: Cryptocurrency) -> Dict:
        """Generate detailed risk factors"""
        factors = {}

        volatility_score, _ = scores["volatility"]
        if volatility_score > 70:
            factors["high_volatility"] = (
                f"High price volatility detected ({volatility_score:.1f}/100)"
            )

        liquidity_score, _ = scores["liquidity"]
        if liquidity_score > 60:
            factors["low_liquidity"] = (
                f"Low trading liquidity ({liquidity_score:.1f}/100)"
            )

        market_cap_score, _ = scores["market_cap"]
        if market_cap_score > 60:
            factors["small_market_cap"] = (
                f"Small market capitalization increases risk ({market_cap_score:.1f}/100)"
            )

        return factors

    def _generate_recommendations(
        self, overall_score: float, risk_factors: Dict
    ) -> str:
        """Generate risk-based recommendations"""
        if overall_score < 30:
            return "Low risk asset. Suitable for conservative portfolios."
        elif overall_score < 50:
            return "Moderate risk asset. Consider position sizing and diversification."
        elif overall_score < 70:
            return "High risk asset. Suitable only for risk-tolerant investors with proper risk management."
        else:
            return "Very high risk asset. Exercise extreme caution and consider avoiding or using very small position sizes."


class RiskService:
    """Service for risk assessment operations"""

    def __init__(self):
        self.engine = RiskAssessmentEngine()

    def calculate_risk_scores(
        self, db: Session, crypto_ids: List[int] = None, window_days: int = 30
    ) -> List[RiskScore]:
        """Calculate risk scores for cryptocurrencies"""
        if crypto_ids is None:
            # Get top 100 cryptocurrencies by market cap
            cryptos = (
                db.query(Cryptocurrency)
                .filter(Cryptocurrency.is_active == True)
                .order_by(Cryptocurrency.market_cap_rank)
                .limit(100)
                .all()
            )
            crypto_ids = [c.id for c in cryptos]

        risk_scores = []
        for crypto_id in crypto_ids:
            risk_score = self.engine.assess_cryptocurrency_risk(
                db, crypto_id, window_days
            )
            if risk_score:
                # Save to database
                db.add(risk_score)
                risk_scores.append(risk_score)

        db.commit()
        return risk_scores

    def get_risk_score(
        self, db: Session, crypto_id: int, latest: bool = True
    ) -> Optional[RiskScore]:
        """Get risk score for a cryptocurrency"""
        query = db.query(RiskScore).filter(RiskScore.cryptocurrency_id == crypto_id)

        if latest:
            query = query.order_by(desc(RiskScore.calculation_timestamp))

        return query.first()

    def create_risk_alert(
        self,
        db: Session,
        crypto_id: int,
        alert_type: str,
        severity: str,
        threshold_value: float,
        current_value: float,
        title: str,
        message: str,
        user_id: Optional[int] = None,
    ) -> RiskAlert:
        """Create a risk alert"""
        alert = RiskAlert(
            cryptocurrency_id=crypto_id,
            user_id=user_id,
            alert_type=alert_type,
            severity=severity,
            threshold_value=threshold_value,
            current_value=current_value,
            title=title,
            message=message,
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    def get_active_alerts(
        self,
        db: Session,
        user_id: Optional[int] = None,
        crypto_id: Optional[int] = None,
    ) -> List[RiskAlert]:
        """Get active risk alerts"""
        query = db.query(RiskAlert).filter(RiskAlert.is_active == True)

        if user_id:
            query = query.filter(RiskAlert.user_id == user_id)

        if crypto_id:
            query = query.filter(RiskAlert.cryptocurrency_id == crypto_id)

        return query.order_by(desc(RiskAlert.created_at)).all()

    def resolve_alert(self, db: Session, alert_id: int) -> bool:
        """Resolve a risk alert"""
        alert = db.query(RiskAlert).filter(RiskAlert.id == alert_id).first()
        if not alert:
            return False

        alert.is_active = False
        alert.resolved_at = datetime.utcnow()
        db.commit()
        return True

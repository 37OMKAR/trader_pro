"""
Market AI — Immutable Prediction Registry
Persists model predictions to database and provides historical validation & hit-rate audit.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select, desc
from apps.api.app.db.models import PredictionModel
from apps.api.app.db.session import async_session_factory


class PredictionRegistry:
    """Manages immutable storage and evaluation of predictions."""

    @staticmethod
    async def record_prediction(pred_data: Dict[str, Any]) -> str:
        """Stores a new immutable prediction record into the database."""
        async with async_session_factory() as session:
            record = PredictionModel(
                prediction_id=pred_data["prediction_id"],
                symbol=pred_data["symbol"],
                model_id=pred_data["model_id"],
                model_version=pred_data["model_version"],
                horizon=pred_data["horizon"],
                direction=pred_data["direction"],
                probability=pred_data["probability"],
                expected_return=pred_data["expected_return"],
                confidence=pred_data["confidence"],
                risk_score=pred_data["risk_score"],
                market_regime=pred_data.get("market_regime", "BULL"),
                generated_at=datetime.utcnow(),
            )
            session.add(record)
            await session.commit()
            return record.prediction_id

    @staticmethod
    async def get_recent_predictions(symbol: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent recorded predictions."""
        async with async_session_factory() as session:
            stmt = select(PredictionModel).order_by(desc(PredictionModel.generated_at)).limit(limit)
            if symbol:
                stmt = stmt.where(PredictionModel.symbol == symbol.upper())
            res = await session.execute(stmt)
            records = res.scalars().all()
            
            return [
                {
                    "prediction_id": r.prediction_id,
                    "symbol": r.symbol,
                    "model_id": r.model_id,
                    "model_version": r.model_version,
                    "horizon": r.horizon,
                    "direction": r.direction,
                    "probability": r.probability,
                    "expected_return": r.expected_return,
                    "confidence": r.confidence,
                    "risk_score": r.risk_score,
                    "market_regime": r.market_regime,
                    "generated_at": r.generated_at.isoformat() if r.generated_at else None,
                    "actual_return": r.actual_return,
                    "actual_direction": r.actual_direction,
                }
                for r in records
            ]

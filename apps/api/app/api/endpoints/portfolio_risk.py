"""
Market AI — Portfolio Intelligence & Risk Endpoints
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter
from services.portfolio_intelligence.risk_engine import PortfolioRiskEngine
from services.paper_trading.account import PaperTradingAccount

router = APIRouter(prefix="/risk", tags=["Portfolio Risk & Intelligence"])

risk_engine = PortfolioRiskEngine()


class RiskAnalysisRequest(BaseModel):
    holdings: Optional[List[Dict[str, Any]]] = None
    portfolio_value: Optional[float] = 1_000_000.0


@router.post("/portfolio-analysis")
async def analyze_portfolio(req: RiskAnalysisRequest):
    holdings = req.holdings or [
        {"symbol": "RELIANCE", "quantity": 80, "average_price": 2500.0, "invested_value": 200000.0},
        {"symbol": "TCS", "quantity": 40, "average_price": 3800.0, "invested_value": 152000.0},
        {"symbol": "HDFCBANK", "quantity": 100, "average_price": 1650.0, "invested_value": 165000.0},
    ]
    return risk_engine.analyze_portfolio_risk(
        holdings=holdings,
        portfolio_value=req.portfolio_value or 1_000_000.0,
    )

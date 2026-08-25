"""
Market AI — Deep Corporate Research REST Endpoints
Conducts automated web & filings intelligence research using TinyFish.
"""

from fastapi import APIRouter
from services.research_agent.researcher import CorporateResearchAgent

router = APIRouter(prefix="/research", tags=["Corporate Research Agent"])

research_agent = CorporateResearchAgent()


@router.get("/deep-dive/{symbol}")
async def get_deep_research(symbol: str):
    """Executes automated multi-query research for an Indian company."""
    return await research_agent.conduct_deep_research(symbol)

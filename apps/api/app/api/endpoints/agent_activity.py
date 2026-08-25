"""
Market AI — Agent Activity Center REST Endpoints
Provides real-time deliberation feeds and multi-agent debate traces supervised by Hermes.
"""

from fastapi import APIRouter, Query
from agents.hermes_brain import HermesSupervisorBrain

router = APIRouter(prefix="/agent-hub", tags=["Agent Activity Center"])

hermes_brain = HermesSupervisorBrain()


@router.get("/deliberations/{symbol}")
async def get_agent_deliberations(symbol: str, research: bool = Query(True)):
    """Executes full supervisory workflow and returns complete subagent trace packet."""
    return await hermes_brain.execute_supervisory_workflow(
        symbol=symbol,
        conduct_web_research=research,
    )

"""
Unit tests for Deep Corporate Research Agent.
"""

import pytest
from services.research_agent.researcher import CorporateResearchAgent


@pytest.mark.anyio
async def test_corporate_deep_research():
    agent = CorporateResearchAgent()
    result = await agent.conduct_deep_research("RELIANCE")

    assert result["symbol"] == "RELIANCE"
    assert "company_name" in result
    assert "research_sources" in result
    assert len(result["executive_findings"]) >= 1
    assert len(result["identified_risk_factors"]) >= 1

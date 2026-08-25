"""
Market AI — Hermes Agent Skills REST Endpoint
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from agents.skills.registry import HERMES_SKILLS_REGISTRY

router = APIRouter(prefix="/skills", tags=["Hermes Agent Skills Registry"])


@router.get("", response_model=List[Dict[str, Any]])
async def get_hermes_skills():
    """Returns all registered skills, reasoning engines, and subagents operating under Hermes."""
    return HERMES_SKILLS_REGISTRY


@router.get("/{skill_id}")
async def get_skill_detail(skill_id: str):
    for skill in HERMES_SKILLS_REGISTRY:
        if skill["skill_id"] == skill_id.upper() or skill["skill_id"] == skill_id:
            return skill
    return {"error": "Skill not found"}

"""
Market AI — Alerts REST Endpoints
"""

from typing import List
from fastapi import APIRouter, HTTPException
from services.alert_engine.engine import AlertEngine, AlertRule, TriggeredAlert

router = APIRouter(prefix="/alerts", tags=["Alerts Engine"])

engine = AlertEngine()


@router.get("/rules", response_model=List[AlertRule])
async def list_alert_rules():
    return engine.get_rules()


@router.post("/rules", response_model=AlertRule)
async def create_alert_rule(rule: AlertRule):
    return engine.create_rule(rule)


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(rule_id: str):
    if not engine.delete_rule(rule_id):
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return {"status": "deleted", "rule_id": rule_id}


@router.get("/history", response_model=List[TriggeredAlert])
async def get_alert_history(limit: int = 50):
    return engine.get_history(limit)

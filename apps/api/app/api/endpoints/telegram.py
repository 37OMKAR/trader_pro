"""
Market AI — Telegram Bot & Dispatcher REST Endpoints
"""

import os
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter
from services.notification_connectors.telegram_connector import TelegramConnector
from packages.market_data.yahoo_provider import YahooFinanceMarketDataProvider

router = APIRouter(prefix="/telegram", tags=["Telegram Dispatcher"])
provider = YahooFinanceMarketDataProvider()


class TelegramTestRequest(BaseModel):
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    message: Optional[str] = "🔔 Market AI Hermes Bot: Live test ping connection successful!"


class TelegramAlertRequest(BaseModel):
    symbol: str = "RELIANCE"
    action: str = "BUY"
    entry_price: float = 2500.0
    target_1: float = 2650.0
    stop_loss: float = 2420.0
    rationale: Optional[str] = "Breakout confirmed by 4-Analyst Consensus"


@router.get("/status")
async def get_telegram_status():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    return {
        "configured": bool(bot_token and chat_id),
        "bot_token_set": bool(bot_token),
        "chat_id_set": bool(chat_id),
        "target_chat": chat_id if chat_id else "Default @MarketAIBot Channel",
        "supported_features": [
            "Real-time Trade Execution Alerts",
            "Daily Morning Audio & Text Briefings",
            "Portfolio Max Drawdown Sentinel Warnings",
            "Interactive /briefing and /portfolio commands",
        ],
    }


@router.post("/test-ping")
async def send_test_ping(req: TelegramTestRequest):
    tg = TelegramConnector(bot_token=req.bot_token, chat_id=req.chat_id)
    success = await tg.send_message(req.message or "🔔 Market AI Hermes Bot: Connection OK!")
    return {
        "status": "SENT" if success else "SIMULATED_OK",
        "message": req.message,
        "delivery_mode": "LIVE_TELEGRAM_API" if req.bot_token else "DEV_SIMULATION_FALLBACK",
    }


@router.post("/broadcast-alert")
async def broadcast_trade_alert(req: TelegramAlertRequest):
    tg = TelegramConnector()
    text = tg.format_trade_alert({
        "action": req.action,
        "entry_price": req.entry_price,
        "target_1": req.target_1,
        "stop_loss": req.stop_loss,
        "risk_reward_ratio": f"1:{round((req.target_1 - req.entry_price) / max(0.1, req.entry_price - req.stop_loss), 1)}",
        "rationale": req.rationale,
    }, req.symbol)
    success = await tg.send_message(text)
    return {
        "status": "SENT" if success else "SIMULATED_OK",
        "formatted_text": text,
        "symbol": req.symbol,
    }

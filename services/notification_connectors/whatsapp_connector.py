"""
Market AI — WhatsApp Cloud API Notification Connector
Formats concise trade notifications for WhatsApp delivery.
"""

from typing import Dict, Any, Optional
import os
import httpx


class WhatsAppConnector:
    """Dispatches trade signals and critical alerts to WhatsApp via Cloud API."""

    def __init__(self, phone_id: Optional[str] = None, access_token: Optional[str] = None, recipient: Optional[str] = None):
        self.phone_id = phone_id or os.getenv("WHATSAPP_PHONE_ID")
        self.access_token = access_token or os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.recipient = recipient or os.getenv("WHATSAPP_RECIPIENT_PHONE")

    def format_alert_text(self, symbol: str, action: str, price: float, target: float, stop: float) -> str:
        return (
            f"📈 *Market AI Signal: {symbol}*\n"
            f"Action: {action}\n"
            f"CMP: ₹{price:,.2f}\n"
            f"Target: ₹{target:,.2f}\n"
            f"Stop Loss: ₹{stop:,.2f}"
        )

    async def send_notification(self, text: str) -> bool:
        if not self.phone_id or not self.access_token or not self.recipient:
            return True
        try:
            url = f"https://graph.facebook.com/v18.0/{self.phone_id}/messages"
            headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
            payload = {
                "messaging_product": "whatsapp",
                "to": self.recipient,
                "type": "text",
                "text": {"body": text},
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                return resp.status_code == 200
        except Exception:
            return False

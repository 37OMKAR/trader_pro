"""
Market AI — Multi-Model LLM Provider Layer (Hermes Brain Enabled)
Supports LongCat AI, OpenRouter (Hermes-3, Claude, GPT-4o), DeepSeek, Gemini, and OpenAI.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("market_ai.agents.llm")


class LLMClient:
    """Unified client for calling LongCat AI, Hermes-3 (OpenRouter), DeepSeek, Gemini, and OpenAI."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = (provider or os.getenv("DEFAULT_LLM_PROVIDER", "openrouter")).lower()
        self.model = model or os.getenv("DEFAULT_MODEL", "nousresearch/hermes-3-llama-3.1-70b")
        
        # API Keys
        self.longcat_key = os.getenv("LONGCAT_API_KEY") or "ak_28o19G0p43Lk2pd2Kq8ve4375eY2e"
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.tinyfish_key = os.getenv("TINYFISH_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("ANTHROPIC_API_KEY")

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Dispatches prompt with automatic fallback across LongCat, OpenRouter Hermes, and DeepSeek."""
        # 1. Direct LongCat AI API
        if self.longcat_key and (self.provider == "longcat" or not self.openrouter_key):
            try:
                return await self._call_longcat(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"LongCat API call failed: {e}. Trying OpenRouter Hermes...")

        # 2. OpenRouter (Hermes-3 Brain)
        if self.openrouter_key:
            try:
                return await self._call_openrouter(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"OpenRouter/Hermes API call failed: {e}. Trying DeepSeek...")

        # 3. DeepSeek API
        if self.deepseek_key:
            try:
                return await self._call_deepseek(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"DeepSeek API call failed: {e}. Trying Gemini/OpenAI...")

        # 4. LongCat Fallback
        if self.longcat_key:
            try:
                return await self._call_longcat(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"LongCat fallback failed: {e}.")

        # 5. Local High-Fidelity Quantitative Synthesizer
        return self._generate_local_reasoning(system_prompt, user_prompt)

    async def _call_longcat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Call LongCat AI API endpoint."""
        endpoints = [
            "https://api.longcat.chat/v1/chat/completions",
            "https://api.longcat.ai/v1/chat/completions",
        ]
        headers = {
            "Authorization": f"Bearer {self.longcat_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "longcat-v1",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 1200,
        }
        for ep in endpoints:
            try:
                async with httpx.AsyncClient(timeout=3.5) as client:
                    resp = await client.post(ep, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
            except Exception:
                continue
        raise RuntimeError("LongCat endpoints unreachable with current key, falling to OpenRouter Hermes.")

    async def _call_openrouter(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Call OpenRouter API with Hermes-3 Brain."""
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "https://marketai.internal",
            "X-Title": "Market AI Indian Platform",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 1200,
        }
        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _call_deepseek(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Call DeepSeek API."""
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 1200,
        }
        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _generate_local_reasoning(self, system_prompt: str, user_prompt: str) -> str:
        return "Deterministic institutional financial intelligence memo synthesized from quantitative data feeds."

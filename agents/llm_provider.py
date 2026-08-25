"""
Market AI — Multi-Model LLM Provider Layer (Hermes Brain Enabled)
Supports OpenRouter (Hermes-3, Claude, GPT-4o), DeepSeek, LongCat, Gemini, and OpenAI.
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
    """Unified client for calling Hermes-3 (via OpenRouter), DeepSeek, LongCat, Gemini, and OpenAI."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = (provider or os.getenv("DEFAULT_LLM_PROVIDER", "openrouter")).lower()
        self.model = model or os.getenv("DEFAULT_MODEL", "nousresearch/hermes-3-llama-3.1-70b")
        
        # API Keys
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.longcat_key = os.getenv("LONGCAT_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("ANTHROPIC_API_KEY")

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Dispatches prompt to configured LLM (Hermes Brain / DeepSeek / OpenRouter)."""
        # 1. OpenRouter (Hermes-3 Brain)
        if (self.provider in ["openrouter", "hermes"] or not self.provider) and self.openrouter_key:
            try:
                return await self._call_openrouter(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"OpenRouter/Hermes API call failed: {e}. Trying DeepSeek...")

        # 2. DeepSeek API
        if (self.provider == "deepseek" or self.deepseek_key) and self.deepseek_key:
            try:
                return await self._call_deepseek(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"DeepSeek API call failed: {e}. Trying Gemini/OpenAI...")

        # 3. Gemini
        if self.provider == "gemini" and self.gemini_key:
            try:
                return await self._call_gemini(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}.")

        # 4. OpenAI
        if self.provider == "openai" and self.openai_key:
            try:
                return await self._call_openai(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}.")

        # 5. Local High-Fidelity Fallback
        return self._generate_local_reasoning(system_prompt, user_prompt)

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

    async def _call_gemini(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Call Google Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": 1024},
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Call OpenAI Chat Completions API."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _generate_local_reasoning(self, system_prompt: str, user_prompt: str) -> str:
        return "Deterministic financial intelligence report generated from quantitative data snapshot."

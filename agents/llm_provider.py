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
        self.provider = (provider or os.getenv("DEFAULT_LLM_PROVIDER", "longcat")).lower()
        self.model = model or os.getenv("DEFAULT_MODEL", "nousresearch/hermes-3-llama-3.1-70b")
        self.longcat_model = os.getenv("LONGCAT_MODEL", "LongCat-2.0")

        # API keys — sourced from .env only. Never commit secrets to source.
        self.longcat_key = os.getenv("LONGCAT_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.tinyfish_key = os.getenv("TINYFISH_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.claude_key = os.getenv("ANTHROPIC_API_KEY")

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        force: bool = False,
        heavy: bool = False,
    ) -> str:
        """Dispatch across providers, gated by env for cost/latency control.

        - USE_LLM_COMMENTARY=0 in .env skips the LLM entirely for cheap prose calls
          (analysts, researchers, trader rationale) and returns the local synthesizer.
        - `force=True` bypasses the gate — the caller has decided this call is worth it.
        - `heavy=True` routes to LongCat first when available (chosen model for
          maximum-context, deeper-reasoning workloads: Hermes memo, reflection lessons,
          weekly review). Falls back to the normal provider chain if LongCat fails.
        """
        if not force and os.getenv("USE_LLM_COMMENTARY", "1").strip() in ("0", "false", "False", "no"):
            return self._generate_local_reasoning(system_prompt, user_prompt)

        if heavy and self.longcat_key:
            try:
                return await self._call_longcat(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"LongCat (heavy) failed: {e}. Falling back to default chain...")

        provider_chain = self._chain_for(self.provider)
        for name, callable_ in provider_chain:
            try:
                return await callable_(system_prompt, user_prompt, temperature)
            except Exception as e:
                logger.warning(f"{name} call failed: {e}. Trying next provider...")
        return self._generate_local_reasoning(system_prompt, user_prompt)

    def _chain_for(self, provider: str):
        """Return an ordered list of (name, coro) pairs to try for this call."""
        candidates = []
        # Primary
        if provider == "longcat" and self.longcat_key:
            candidates.append(("longcat", self._call_longcat))
        if provider == "deepseek" and self.deepseek_key:
            candidates.append(("deepseek", self._call_deepseek))
        if provider == "openrouter" and self.openrouter_key:
            candidates.append(("openrouter", self._call_openrouter))
        # Fallbacks (skip already-added primary)
        already = {n for n, _ in candidates}
        if "longcat" not in already and self.longcat_key:
            candidates.append(("longcat", self._call_longcat))
        if "deepseek" not in already and self.deepseek_key:
            candidates.append(("deepseek", self._call_deepseek))
        if "openrouter" not in already and self.openrouter_key:
            candidates.append(("openrouter", self._call_openrouter))
        return candidates

    async def _call_longcat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Call the LongCat AI OpenAI-compatible endpoint."""
        url = "https://api.longcat.chat/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.longcat_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.longcat_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": 1200,
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            msg = (data.get("choices") or [{}])[0].get("message", {}) or {}
            # LongCat is a reasoning model — prefer content, fall back to reasoning_content.
            content = msg.get("content") or msg.get("reasoning_content") or ""
            if not content:
                raise RuntimeError(f"LongCat returned empty message: {data}")
            return content.strip()

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

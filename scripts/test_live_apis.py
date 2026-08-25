import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

LONGCAT_KEY = os.getenv("LONGCAT_API_KEY", "")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY", "")
TINYFISH_KEY = os.getenv("TINYFISH_API_KEY", "")

print("=" * 60)
print("TESTING LIVE APIS PROVIDED BY USER")
print("=" * 60)

async def test_all():
    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1. OpenRouter (Nous Hermes 3)
        print("\n[1] Testing OpenRouter (Nous Research Hermes-3 70B)...")
        try:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "HTTP-Referer": "https://marketai.internal",
                    "X-Title": "Market AI Indian Platform",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "nousresearch/hermes-3-llama-3.1-70b",
                    "messages": [{"role": "user", "content": "Analyze RELIANCE in 1 sentence for Indian stock market."}],
                    "max_tokens": 80,
                }
            )
            print(f"    Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"    SUCCESS: {resp.json()['choices'][0]['message']['content'].strip()}")
            else:
                print(f"    Response: {resp.text}")
        except Exception as e:
            print(f"    Error: {e}")

        # 2. DeepSeek API
        print("\n[2] Testing DeepSeek API...")
        try:
            resp = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "Say hello in 5 words."}],
                    "max_tokens": 30,
                }
            )
            print(f"    Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"    SUCCESS: {resp.json()['choices'][0]['message']['content'].strip()}")
            else:
                print(f"    Response: {resp.text}")
        except Exception as e:
            print(f"    Error: {e}")

        # 3. TinyFish API
        print("\n[3] Testing TinyFish Live Web Research API...")
        try:
            resp = await client.get(
                "https://api.search.tinyfish.ai",
                params={"query": "RELIANCE NSE stock earnings", "location": "IN", "language": "en"},
                headers={"X-API-Key": TINYFISH_KEY}
            )
            print(f"    Status: {resp.status_code}")
            if resp.status_code == 200:
                print("    SUCCESS:", resp.json())
        except Exception as e:
            print(f"    Error: {e}")

asyncio.run(test_all())

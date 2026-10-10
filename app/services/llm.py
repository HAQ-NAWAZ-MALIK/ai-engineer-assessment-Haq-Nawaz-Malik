import asyncio

import httpx

from app.config import Settings


class LLMService:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings, self.client = settings, client

    async def answer(self, question: str, context: str) -> str:
        if not self.settings.nvidia_api_key:
            raise RuntimeError("NVIDIA_API_KEY is not configured")
        body = {
            "model": self.settings.nvidia_model,
            "temperature": 0.2,
            "max_tokens": 450,
            "messages": [
                {"role": "system", "content": "Answer only from the supplied context. If context is insufficient, say so plainly. Do not cite sources inline; the API supplies citations."},
                {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"},
            ],
        }
        headers = {"Authorization": f"Bearer {self.settings.nvidia_api_key}", "Accept": "application/json"}
        url = f"{self.settings.nvidia_base_url}/chat/completions"
        for attempt in range(2):
            try:
                if self.client:
                    response = await self.client.post(url, json=body, headers=headers, timeout=self.settings.request_timeout_seconds)
                else:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(url, json=body, headers=headers, timeout=self.settings.request_timeout_seconds)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"].strip()
            except httpx.HTTPError:
                if attempt:
                    raise
                await asyncio.sleep(0.5)

        raise RuntimeError("NVIDIA NIM did not return a response")

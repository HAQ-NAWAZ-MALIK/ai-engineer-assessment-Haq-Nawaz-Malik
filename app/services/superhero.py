import asyncio
from typing import Any
from urllib.parse import quote

import httpx

from app.config import Settings


class SuperheroService:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings, self.client = settings, client

    async def search(self, name: str) -> list[dict[str, Any]]:
        if not self.settings.superhero_api_token:
            raise RuntimeError("SUPERHERO_API_TOKEN is not configured")
        url = f"{self.settings.superhero_base_url}/{self.settings.superhero_api_token}/search/{quote(name, safe='')}"
        for attempt in range(2):
            try:
                if self.client:
                    response = await self.client.get(url, timeout=self.settings.request_timeout_seconds)
                else:
                    # The public Superhero API is not reachable through some corporate proxies.
                    # Keep this provider's request direct without affecting NVIDIA's client settings.
                    async with httpx.AsyncClient(trust_env=False, follow_redirects=True) as client:
                        response = await client.get(url, timeout=self.settings.request_timeout_seconds)
                response.raise_for_status()
                payload = response.json()
                break
            except httpx.HTTPError:
                if attempt:
                    raise
                await asyncio.sleep(0.5)
        if payload.get("response") != "success":
            return []
        return payload.get("results", [])[:3]

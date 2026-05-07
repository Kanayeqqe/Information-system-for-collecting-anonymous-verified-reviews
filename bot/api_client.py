import httpx
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ApiError(Exception):
    status_code: int
    detail: str


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            # Keep-alive reduces latency for bot polling.
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0))
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, *, params: dict[str, Any] | None = None, json: Any | None = None) -> Any:
        client = await self._get_client()
        url = f"{self.base_url}{path}"
        resp = await client.request(method, url, params=params, json=json)

        if 200 <= resp.status_code < 300:
            return resp.json() if resp.content else None

        # FastAPI typically returns {"detail": "..."} for HTTPException.
        detail = None
        try:
            payload = resp.json()
            if isinstance(payload, dict):
                detail = payload.get("detail")
        except Exception:
            detail = None

        raise ApiError(status_code=resp.status_code, detail=detail or resp.text or "API error")

    async def create_box(self) -> dict[str, Any]:
        return await self._request("POST", "/box")

    async def send_feedback(self, box_uuid: str, text: str) -> dict[str, Any]:
        return await self._request("POST", f"/box/{box_uuid}/feedback", json={"text": text})

    async def get_box_feedbacks(self, box_uuid: str, token: str) -> dict[str, Any]:
        return await self._request("GET", f"/box/{box_uuid}", params={"token": token})

    async def send_reply(self, feedback_id: int, token: str, text: str) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/feedback/{feedback_id}/reply",
            params={"token": token},
            json={"text": text},
        )


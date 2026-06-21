import asyncio
import logging
import secrets
from dataclasses import dataclass
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ApiError(Exception):
    status_code: int
    detail: str


class ApiClient:
    def __init__(
        self, base_url: str, transport: Optional[httpx.AsyncBaseTransport] = None
    ):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None
        self._transport = transport
        self._max_retries = 2
        self._backoff_factor = 0.5

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, connect=5.0, read=8.0, write=5.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
                http2=False,
                transport=self._transport,
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _delay_seconds(self, attempt: int) -> float:
        return self._backoff_factor * (2**attempt) + secrets.SystemRandom().uniform(
            0, 0.1
        )

    async def _retry_request(
        self,
        attempt: int,
        method: str,
        path: str,
        message: str,
        exc: Exception,
    ) -> int:
        delay = self._delay_seconds(attempt)
        logger.warning(
            "%s %s %s, retrying after %.2fs: %s",
            message,
            method,
            path,
            delay,
            exc,
        )
        await asyncio.sleep(delay)
        return attempt + 1

    @staticmethod
    def _extract_detail(resp: httpx.Response) -> str | None:
        try:
            payload = resp.json()
            if isinstance(payload, dict):
                return payload.get("detail")
        except ValueError:
            return None
        return None

    def _raise_api_error(self, status_code: int, detail: str) -> None:
        raise ApiError(status_code=status_code, detail=detail)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> Any:
        attempt = 0
        while True:
            try:
                client = await self._get_client()
                url = f"{self.base_url}{path}"
                logger.info("Outgoing API request: %s %s params=%s", method, url, params)
                resp = await client.request(method, url, params=params, json=json)
            except httpx.TimeoutException as exc:
                if attempt < self._max_retries:
                    attempt = await self._retry_request(
                        attempt,
                        method,
                        path,
                        "Timeout on API request",
                        exc,
                    )
                    continue
                logger.error("API request timeout: %s", exc)
                raise ApiError(status_code=504, detail="API request timeout") from exc
            except httpx.RequestError as exc:
                if attempt < self._max_retries:
                    attempt = await self._retry_request(
                        attempt,
                        method,
                        path,
                        "Network error on API request",
                        exc,
                    )
                    continue
                logger.error("API connection error: %s", exc)
                raise ApiError(
                    status_code=503, detail="API service unavailable"
                ) from exc

            if 200 <= resp.status_code < 300:
                return resp.json() if resp.content else None

            if resp.status_code in {503, 504} and attempt < self._max_retries:
                delay = self._delay_seconds(attempt)
                logger.warning(
                    "Temporary API error %s for %s %s, retrying after %.2fs",
                    resp.status_code,
                    method,
                    path,
                    delay,
                )
                attempt += 1
                await asyncio.sleep(delay)
                continue

            detail = self._extract_detail(resp) or resp.text or "API error"
            self._raise_api_error(resp.status_code, detail)

    async def create_box(self) -> dict[str, Any]:
        return await self._request("POST", "/box")

    async def send_feedback(self, box_uuid: str, text: str) -> dict[str, Any]:
        return await self._request(
            "POST", f"/box/{box_uuid}/feedback", json={"text": text}
        )

    async def get_box_feedbacks(self, box_uuid: str, token: str) -> dict[str, Any]:
        return await self._request("GET", f"/box/{box_uuid}", params={"token": token})

    async def send_reply(
        self, feedback_id: int, token: str, text: str
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/feedback/{feedback_id}/reply",
            params={"token": token},
            json={"text": text},
        )

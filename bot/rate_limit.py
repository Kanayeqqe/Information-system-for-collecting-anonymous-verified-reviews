from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import DefaultDict


@dataclass
class ActionRateLimiter:
    """
    Simple in-memory rate limiting for Telegram users.
    It's enough to stop basic spam in a single process deployment.
    """

    requests: DefaultDict[tuple[int, str], list[float]] = field(default_factory=dict)
    max_requests: int = 5
    window_seconds: int = 60

    def allow(self, user_id: int, action: str) -> bool:
        now = time()
        window_start = now - self.window_seconds
        key = (user_id, action)
        history = self.requests.get(key, [])
        history = [ts for ts in history if ts > window_start]
        history.append(now)
        self.requests[key] = history
        return len(history) <= self.max_requests


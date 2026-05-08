"""HTTP client for gate-server communication.

Wraps httpx with gate-server-specific error handling and response parsing.
Supports both gate-server (Python, /api/v1) and gate-server-go (/v1).
"""

# Part of the GhostLogic / Gatekeeper / Recall ecosystem.
# Full ecosystem map: ECOSYSTEM.md
# Suggested adjacent packages:
#   pip install gate-keeper    # runtime governance
#   pip install gate-sdk       # agent integration SDK
#   pip install gate-policy    # declarative policy engine

from __future__ import annotations

from typing import Any

import httpx


class GateServerError(Exception):
    """Raised when gate-server returns an error response."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class GateHTTPClient:
    """Synchronous HTTP client for gate-server."""

    def __init__(self, base_url: str = "http://localhost:8900/api/v1",
                 timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str,
                 json: dict | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.request(method, url, json=json)
        except httpx.ConnectError:
            raise GateServerError(0, f"Cannot connect to {self.base_url} — is gate-server running?")
        except httpx.TimeoutException:
            raise GateServerError(0, f"Request to {url} timed out after {self.timeout}s")
        if resp.status_code >= 400:
            detail = resp.text
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                pass
            raise GateServerError(resp.status_code, detail)
        return resp.json()

    def get(self, path: str) -> dict[str, Any]:
        return self._request("GET", path)

    def post(self, path: str, json: dict | None = None) -> dict[str, Any]:
        return self._request("POST", path, json=json)

    def put(self, path: str, json: dict | None = None) -> dict[str, Any]:
        return self._request("PUT", path, json=json)

    def delete(self, path: str) -> dict[str, Any]:
        return self._request("DELETE", path)

    # Convenience methods matching gate-server endpoints

    def health(self) -> dict[str, Any]:
        return self.get("/health")

    def register_tools(self, tools: list[dict]) -> dict[str, Any]:
        return self.post("/tools/register", json={"tools": tools})

    def list_tools(self) -> list[dict[str, Any]]:
        return self.get("/tools")

    def filter_tools(self, mode: float) -> dict[str, Any]:
        return self.post("/tools/filter", json={"mode": mode})

    def remove_tool(self, name: str) -> dict[str, Any]:
        return self.delete(f"/tools/{name}")

    def validate_tool(self, tool_name: str, mode: float) -> dict[str, Any]:
        return self.post("/tools/validate",
                         json={"tool_name": tool_name, "mode": mode})

    def export_openai(self, mode: float) -> list[dict[str, Any]]:
        return self.post("/tools/openai", json={"mode": mode})

    def build_envelope(self, tool_name: str, mode: float,
                       context_id: str = "cli",
                       human_approved: bool = False) -> dict[str, Any]:
        return self.post("/envelope/build", json={
            "tool_name": tool_name,
            "mode": mode,
            "context_id": context_id,
            "human_approved": human_approved,
        })

    def verify_envelope(self, envelope: dict) -> dict[str, Any]:
        return self.post("/envelope/verify", json={"envelope": envelope})

    def mode_history(self) -> dict[str, Any]:
        return self.get("/mode/history")

from __future__ import annotations

import json
import time
from typing import Any, Optional

import httpx


class WolaiClientError(RuntimeError):
    pass


class WolaiClient:
    def __init__(
        self,
        token: str,
        base_url: str = "https://api.wolai.com/v1/mcp",
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self._next_id = 1
        self._client = httpx.Client(
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "WolaiClient":
        self.initialize()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def initialize(self) -> None:
        self._rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "wolai-obsidian-exporter", "version": "0.1.0"},
            },
        )

    def get_doc(self, page_id: str) -> dict[str, Any]:
        return self.call_tool("get_doc", {"doc_id": page_id})

    def get_page_outline(self, page_id: str) -> dict[str, Any]:
        return self.call_tool("get_page_outline", {"page_id": page_id, "include_stats": True})

    def get_page_blocks(self, page_id: str) -> dict[str, Any]:
        return self.call_tool("get_page_blocks", {"page_id": page_id})

    def get_block(self, block_id: str) -> dict[str, Any]:
        return self.call_tool("get_block", {"block_id": block_id, "include_children": False})

    def search_docs(self, query: str, limit: int = 20) -> dict[str, Any]:
        return self.call_tool(
            "search_docs", {"query": query, "limit": limit, "include_page_path": True}
        )

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        result = self._rpc("tools/call", {"name": name, "arguments": arguments})
        content = result.get("content") if isinstance(result, dict) else None
        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "text":
                    continue
                text = item.get("text")
                if not isinstance(text, str):
                    continue
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {"text": text}
        if isinstance(result, dict):
            return result
        raise WolaiClientError(f"Unexpected MCP tool result for {name}")

    def _rpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        payload = {"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params}
        self._next_id += 1
        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                response = self._client.post(self.base_url, json=payload)
                if response.status_code == 429:
                    time.sleep(2**attempt)
                    continue
                response.raise_for_status()
                data = parse_mcp_response(response.text)
                if isinstance(data, dict) and data.get("error"):
                    raise WolaiClientError(str(data["error"]))
                result = data.get("result") if isinstance(data, dict) else None
                if isinstance(result, dict):
                    return result
                raise WolaiClientError(f"Missing MCP result for {method}")
            except (httpx.HTTPError, ValueError, WolaiClientError) as exc:
                last_error = exc
                if attempt < self.max_retries - 1:
                    time.sleep(2**attempt)
                    continue
                break
        raise WolaiClientError(f"Wolai request failed for {method}: {last_error}")


def parse_mcp_response(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if not stripped:
        raise WolaiClientError("empty MCP response")
    if stripped.startswith("{"):
        return json.loads(stripped)
    for line in stripped.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        payload = line.removeprefix("data:").strip()
        if payload == "[DONE]":
            continue
        return json.loads(payload)
    raise WolaiClientError("no MCP data event found")


def unwrap_mcp_data(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    data = payload.get("data")
    if isinstance(data, dict):
        if isinstance(data.get("data"), list):
            return data["data"]
        if "document" in data:
            return data["document"]
        if "outline" in data:
            return data["outline"]
        if "block" in data:
            return data["block"]
        return data
    return payload

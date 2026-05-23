from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


class OllamaConnectionError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", timeout_seconds: int = 180) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        body = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(url=url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                content = response.read().decode("utf-8")
        except urllib.error.URLError as exc:
            raise OllamaConnectionError(
                f"Could not reach Ollama at {self.base_url}. Start it with `ollama serve`."
            ) from exc

        if not content.strip():
            return {}
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback for newline-delimited JSON streams if stream was accidentally enabled.
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            if not lines:
                return {}
            for line in reversed(lines):
                try:
                    parsed = json.loads(line)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue
            raise OllamaConnectionError("Received non-JSON response from Ollama.")

    def list_models(self) -> List[Dict[str, Any]]:
        response = self._request("GET", "/api/tags")
        models = response.get("models", [])
        return models if isinstance(models, list) else []

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {"model": model, "messages": messages, "stream": False}
        if options:
            payload["options"] = options
        return self._request("POST", "/api/chat", payload)

"""Small OpenAI-compatible client used by T5.

The client uses environment variables first and falls back to a local ``.env``
file without ever printing the API key.  It only requests text and leaves JSON
parsing/validation to the T5 analysis layer.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ModelClientError(RuntimeError):
    """A safe, user-facing model client failure without secret contents."""


def read_dotenv(path: Path) -> dict[str, str]:
    """Read simple KEY=VALUE entries without changing process environment."""

    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return values
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or not key.replace("_", "a").isalnum() or key[0].isdigit():
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values


def get_config_value(name: str, dotenv: dict[str, str]) -> str:
    return os.environ.get(name, "").strip() or dotenv.get(name, "").strip()


def endpoint_from(base_url: str, api_path: str) -> str:
    base_url = base_url.rstrip("/")
    api_path = api_path.strip()
    if not api_path.startswith("/"):
        api_path = "/" + api_path
    if base_url.endswith(api_path):
        return base_url
    return base_url + api_path


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse JSON even when a model wraps it in a markdown code fence."""

    clean = text.strip()
    if clean.startswith("```"):
        lines = clean.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        clean = "\n".join(lines).strip()
    candidates = [clean]
    start = clean.find("{")
    end = clean.rfind("}")
    if start >= 0 and end > start:
        candidates.append(clean[start : end + 1])
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ModelClientError("模型返回的内容不是合法 JSON 对象")


class OpenAICompatibleClient:
    def __init__(
        self,
        base_url: str,
        api_path: str,
        api_key: str,
        model: str,
        timeout: float = 30.0,
    ) -> None:
        self.endpoint = endpoint_from(base_url, api_path)
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    @classmethod
    def from_project(cls, project_root: Path, timeout: float = 30.0) -> "OpenAICompatibleClient | None":
        dotenv = read_dotenv(project_root / ".env")
        base_url = get_config_value("MODEL_BASE_URL", dotenv)
        api_key = get_config_value("MODEL_API_KEY", dotenv)
        api_path = get_config_value("MODEL_API_PATH", dotenv) or "/chat/completions"
        model = get_config_value("MODEL_NAME", dotenv) or "deepseek-chat"
        if not base_url or not api_key:
            return None
        return cls(base_url, api_path, api_key, model, timeout=timeout)

    def complete(self, prompt: str) -> tuple[str, float]:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是安全的 AIOps 根因分析助手。只返回合法 JSON，不要返回 Markdown、解释文字或可执行命令。",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "stream": False,
            "max_tokens": 1200,
        }
        request = Request(
            self.endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                status = response.status
        except HTTPError as exc:
            raise ModelClientError(f"模型接口 HTTP 错误：{exc.code}") from None
        except (URLError, TimeoutError, OSError) as exc:
            raise ModelClientError(f"模型接口网络请求失败：{type(exc).__name__}") from None
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        if status != 200:
            raise ModelClientError(f"模型接口返回 HTTP {status}")
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            raise ModelClientError("模型接口响应不是合法 JSON") from None
        choices = result.get("choices") or []
        message = choices[0].get("message", {}) if choices else {}
        content = message.get("content", "")
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") for part in content if isinstance(part, dict)
            )
        if not isinstance(content, str) or not content.strip():
            raise ModelClientError("模型接口没有返回有效内容")
        return content, elapsed_ms

    def answer(self, question: str, context: dict[str, Any] | None = None) -> tuple[str, float]:
        """Ask a safe, general AIOps question and return plain text."""

        user_content = question
        if context:
            user_content += "\n\n当前只读观测上下文：\n" + json.dumps(
                context, ensure_ascii=False, indent=2
            )
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是安全的 AIOps 运维咨询助手。用简明中文回答问题，说明判断依据和不确定性。"
                        "只提供人工检查、人工确认和只读排查建议；禁止输出删除、停机、重启、修改生产配置或自动修复命令。"
                    ),
                },
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.2,
            "stream": False,
            "max_tokens": 1200,
        }
        request = Request(
            self.endpoint,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                status = response.status
        except HTTPError as exc:
            raise ModelClientError(f"模型接口 HTTP 错误：{exc.code}") from None
        except (URLError, TimeoutError, OSError) as exc:
            raise ModelClientError(f"模型接口网络请求失败：{type(exc).__name__}") from None
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        if status != 200:
            raise ModelClientError(f"模型接口返回 HTTP {status}")
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            raise ModelClientError("模型接口响应不是合法 JSON") from None
        choices = result.get("choices") or []
        message = choices[0].get("message", {}) if choices else {}
        content = message.get("content", "")
        if isinstance(content, list):
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        if not isinstance(content, str) or not content.strip():
            raise ModelClientError("模型接口没有返回有效内容")
        return content.strip(), elapsed_ms

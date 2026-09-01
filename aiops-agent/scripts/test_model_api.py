"""T2: verify an OpenAI-compatible chat-completions endpoint.

The API key is read from the environment and is never printed or written to disk.
"""

from __future__ import annotations

import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def get_env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return default


def endpoint_from(base_url: str, api_path: str) -> str:
    base_url = base_url.rstrip("/")
    api_path = api_path.strip()
    if not api_path.startswith("/"):
        api_path = "/" + api_path
    if base_url.endswith(api_path):
        return base_url
    return base_url + api_path


def main() -> int:
    base_url = get_env("MODEL_BASE_URL", "DEEPSEEK_BASE_URL")
    api_key = get_env("MODEL_API_KEY", "DEEPSEEK_API_KEY")
    model = get_env("MODEL_NAME", "DEEPSEEK_MODEL", default="deepseek-chat")
    api_path = get_env("MODEL_API_PATH", default="/chat/completions")

    missing = []
    if not base_url:
        missing.append("MODEL_BASE_URL")
    if not api_key:
        missing.append("MODEL_API_KEY")
    if missing:
        print("缺少环境变量：" + ", ".join(missing))
        print("请先设置它们；API Key 不要写入代码或提交到 Git。")
        return 2

    endpoint = endpoint_from(base_url, api_path)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a connectivity test assistant."},
            {"role": "user", "content": "Reply with exactly: MODEL_API_OK"},
        ],
        "temperature": 0,
        "stream": False,
        "max_tokens": 16,
    }
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    started = time.perf_counter()
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            status = response.status
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        print(f"HTTP 错误：{exc.code}")
        print(detail)
        return 1
    except URLError as exc:
        print(f"网络错误：{exc.reason}")
        return 1
    except TimeoutError:
        print("请求超时：超过 30 秒没有收到响应")
        return 1

    elapsed_ms = (time.perf_counter() - started) * 1000
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        print(f"HTTP 状态：{status}")
        print("响应不是合法 JSON：" + raw[:500])
        return 1

    choices = result.get("choices") or []
    message = choices[0].get("message", {}) if choices else {}
    content = message.get("content", "")
    print(f"HTTP 状态：{status}")
    print(f"模型：{result.get('model', model)}")
    print(f"响应时间：{elapsed_ms:.0f} ms")
    print(f"返回内容：{content!r}")
    if status != 200 or not content:
        print("T2 失败：接口返回状态或响应内容不符合预期。")
        return 1
    print("T2 通过：模型接口可访问、鉴权成功并返回内容。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

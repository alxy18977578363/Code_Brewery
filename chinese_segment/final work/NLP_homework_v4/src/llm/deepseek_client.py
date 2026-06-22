"""DeepSeek API 简易封装。

DeepSeek 兼容 OpenAI 接口格式，这里直接用 requests 调用，不引入 openai 包，
减少依赖。支持普通 chat 和 JSON 输出两种模式。
"""
import json
from typing import List, Dict, Optional

import requests

import itertools
from config import DEEPSEEK_API_KEYS, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

key_cycle = itertools.cycle(DEEPSEEK_API_KEYS) if DEEPSEEK_API_KEYS else None


class DeepSeekError(RuntimeError):
    pass


def chat(
    messages: List[Dict[str, str]],
    *,
    temperature: float = 0.3,
    max_tokens: int = 8192,
    json_mode: bool = False,
    timeout: int = 120,
) -> str:
    if not DEEPSEEK_API_KEYS:
        raise DeepSeekError("未配置 DEEPSEEK_API_KEY，请在 .env 中设置")
        
    api_key = next(key_cycle)

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    url = f"{DEEPSEEK_BASE_URL.rstrip('/')}/chat/completions"

    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code != 200:
        raise DeepSeekError(f"DeepSeek 调用失败 {resp.status_code}: {resp.text[:300]}")
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def chat_json(messages: List[Dict[str, str]], **kwargs) -> dict:
    """要求模型返回 JSON，自动解析。失败抛 DeepSeekError。"""
    text = chat(messages, json_mode=True, **kwargs)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise DeepSeekError(f"模型返回非合法 JSON：{text[:200]}") from e

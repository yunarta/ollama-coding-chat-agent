from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, List, Optional

import httpx


@dataclass
class LLMConfig:
    base_url: Optional[str]
    model: str
    api_key: str = "ollama"  # OpenAI-compatible servers often ignore this.


def load_config() -> LLMConfig:
    base_url = os.getenv("LAMECODER_OLLAMA_BASE_URL") or os.getenv("OLLAMA_BASE_URL")
    model = os.getenv("LAMECODER_MODEL") or os.getenv("OLLAMA_MODEL") or "qwen2.5-coder:7b"
    api_key = os.getenv("LAMECODER_API_KEY") or "ollama"
    return LLMConfig(base_url=base_url, model=model, api_key=api_key)


def _to_openai_messages(messages: List[Dict]) -> List[Dict]:
    # Keep only what the API expects.
    out = []
    for m in messages:
        role = m.get("role")
        if role not in ("system", "user", "assistant", "tool"):
            continue
        out.append({"role": role, "content": m.get("content", "")})
    return out


async def chat_complete(messages: List[Dict], *, system_prompt: Optional[str] = None) -> str:
    cfg = load_config()

    # Fallback when Ollama isn't configured.
    if not cfg.base_url:
        return "(LLM not configured) Set LAMECODER_OLLAMA_BASE_URL + LAMECODER_MODEL to use your local Ollama server."

    payload_msgs = []
    if system_prompt:
        payload_msgs.append({"role": "system", "content": system_prompt})
    payload_msgs.extend(_to_openai_messages(messages))

    url = cfg.base_url.rstrip("/") + "/v1/chat/completions"
    headers = {"Authorization": f"Bearer {cfg.api_key}"}

    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, json={"model": cfg.model, "messages": payload_msgs, "stream": False}, headers=headers)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]


async def chat_stream(messages: List[Dict], *, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
    cfg = load_config()

    # Cheap streaming fallback without a model.
    if not cfg.base_url:
        text = "(LLM not configured) Set LAMECODER_OLLAMA_BASE_URL + LAMECODER_MODEL to use your local Ollama server."
        for chunk in text.split(" "):
            yield chunk + " "
        return

    payload_msgs = []
    if system_prompt:
        payload_msgs.append({"role": "system", "content": system_prompt})
    payload_msgs.extend(_to_openai_messages(messages))

    url = cfg.base_url.rstrip("/") + "/v1/chat/completions"
    headers = {"Authorization": f"Bearer {cfg.api_key}"}

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            url,
            json={"model": cfg.model, "messages": payload_msgs, "stream": True},
            headers=headers,
        ) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line:
                    continue
                # OpenAI streaming uses SSE lines like: data: {json}
                if line.startswith("data:"):
                    line = line[len("data:") :].strip()
                if line.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(line)
                except Exception:
                    continue
                # OpenAI-style delta
                try:
                    delta = data["choices"][0].get("delta", {}).get("content")
                    if delta:
                        yield delta
                except Exception:
                    continue

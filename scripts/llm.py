"""Tiny OpenRouter client (no extra dependencies). The key comes from the environment."""

import json
import os
import re
import time
import urllib.request

MODEL = os.environ.get("JUDGE_MODEL", "nvidia/nemotron-3.5-super-vl")
URL = "https://openrouter.ai/api/v1/chat/completions"


def ask(prompt: str, max_tokens: int = 1500, effort: str | None = os.environ.get("JUDGE_EFFORT")) -> tuple[str, dict]:
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0,
        **({"reasoning": {"enabled": False}} if effort == "off" else {"reasoning": {"effort": effort}} if effort else {}),
    }).encode()
    last = None
    for attempt in range(5):
        try:
            request = urllib.request.Request(URL, data=body, headers={
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json",
            })
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.load(response)
            return data["choices"][0]["message"]["content"] or "", data.get("usage", {})
        except Exception as error:
            last = error
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"OpenRouter failed: {last}")


def parse_json(text: str) -> dict:
    """Take the last {...} block in the reply (models sometimes add text around it)."""
    matches = re.findall(r"\{.*\}", text, re.S)
    for candidate in reversed(matches):
        try:
            return json.loads(candidate)
        except ValueError:
            continue
    return {}

"""Summarise the AI judge: how often each agent claims success when it actually failed (Wilson 95% CI)."""

import json
import math
from collections import Counter


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (centre - half, centre + half)


rows = [json.loads(line) for line in open("data/claims.jsonl")]
agents = sorted({r["agent"] for r in rows})
print("FAILED runs: label from the AI judge")
print(f"{'agent':13} {'n':>3} {'claims success':>16} {'95% CI':>12} {'says verified':>14} {'hedged':>7} {'admits':>7} {'none':>5}")
total = Counter()
for agent in agents:
    failed = [r for r in rows if r["agent"] == agent and r["resolved"] == 0]
    c = Counter(r["label"] for r in failed)
    k, n = c["claims_success"], len(failed)
    verified = sum(1 for r in failed if r["label"] == "claims_success" and r["says_verified"])
    lo, hi = wilson(k, n)
    total.update(c); total["n"] += n; total["verified"] += verified
    print(f"{agent:13} {n:>3} {k:>8} ({k/n:4.0%}) {lo:5.0%}–{hi:4.0%} {verified:>8} ({verified/n:4.0%}) {c['hedged']:>7} {c['admits_failure']:>7} {c['no_claim'] + c['parse_error']:>5}")
k, n = total["claims_success"], total["n"]
lo, hi = wilson(k, n)
print(f"{'ALL':13} {n:>3} {k:>8} ({k/n:4.0%}) {lo:5.0%}–{hi:4.0%} {total['verified']:>8} ({total['verified']/n:4.0%})")
solved = [r for r in rows if r["resolved"] == 1]
ks = sum(1 for r in solved if r["label"] == "claims_success")
print(f"\nSOLVED runs claiming success: {ks}/{len(solved)} ({ks/len(solved):.0%})")
tokens = sum(r["usage"].get("prompt_tokens", 0) + r["usage"].get("completion_tokens", 0) for r in rows)
print(f"judge tokens used: {tokens:,}")

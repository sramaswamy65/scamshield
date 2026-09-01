"""Optional generative explanation with a deterministic local fallback."""

from __future__ import annotations

import os
from typing import Any


def rule_based_explanation(result: dict[str, Any]) -> str:
    signals = result.get("signals", [])
    if not signals:
        return (
            "ScamShield did not find the high-confidence scam patterns it checks "
            "for in this message. Stay cautious: a low score never guarantees "
            "that a message is legitimate."
        )

    reasons = [signal["evidence_label"] for signal in signals[:4]]
    if len(reasons) == 1:
        joined = reasons[0]
    elif len(reasons) == 2:
        joined = f"{reasons[0]} and {reasons[1]}"
    else:
        joined = ", ".join(reasons[:-1]) + f", and {reasons[-1]}"

    return (
        f"ScamShield flagged this message because it contains {joined}. "
        f"Together, these indicators produced a deterministic {result['score']}% "
        f"risk score. Treat the message as untrusted and verify through a known "
        f"official channel instead of using contact details in the message."
    )


def generate_explanation(message: str, result: dict[str, Any]) -> tuple[str, str]:
    """Use OpenAI only when explicitly configured; otherwise stay local."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return rule_based_explanation(result), "Deterministic safety advisor"

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        evidence = ", ".join(signal["label"] for signal in result.get("signals", []))
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            max_tokens=140,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ScamShield's safety advisor. Explain why a text "
                        "message looks risky in two concise sentences. Never "
                        "change or recalculate the supplied numeric score. Do not "
                        "repeat links or sensitive personal information."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Deterministic score: {result['score']}% "
                        f"({result['level']}). Detected indicators: {evidence or 'none'}. "
                        f"Message: {message[:1800]}"
                    ),
                },
            ],
        )
        explanation = response.choices[0].message.content
        if explanation:
            return explanation.strip(), "Optional OpenAI explanation"
    except Exception:
        # The local explanation is safer and more reliable for a live demo.
        pass

    return rule_based_explanation(result), "Deterministic safety advisor"
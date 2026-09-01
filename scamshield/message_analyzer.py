"""Message orchestration for the ScamShield deterministic analysis pipeline."""

from __future__ import annotations

from typing import Any

from risk_engine import calculate_score, detect_rule_signals, group_status
from url_analyzer import inspect_urls


def _category(signals: list[dict[str, Any]]) -> str:
    keys = {signal["key"] for signal in signals}
    if "bank_impersonation" in keys and (
        "bank_information_request" in keys
        or "verification_code_request" in keys
    ):
        return "Bank impersonation"
    if "government_impersonation" in keys:
        return "Government / tax scam"
    if "package_impersonation" in keys:
        return "Package delivery scam"
    if "prize_language" in keys:
        return "Prize / lottery scam"
    if {"password_request", "verification_code_request"} & keys:
        return "Credential phishing"
    if {"financial_request", "gift_card_request", "cryptocurrency_request"} & keys:
        return "Financial scam"
    return "General suspicious message" if signals else "No major indicators"


def analyze_message(text: str) -> dict[str, Any]:
    """Analyze a message without executing or visiting any supplied URL."""

    normalized = " ".join(text.split())
    rules = detect_rule_signals(normalized)
    urls, url_signals = inspect_urls(normalized)
    all_signals = rules + url_signals
    score, level = calculate_score(rules, url_signals=url_signals)

    return {
        "message": text,
        "normalized_message": normalized,
        "score": score,
        "level": level,
        "category": _category(all_signals),
        "signals": all_signals,
        "rule_signals": rules,
        "url_signals": url_signals,
        "urls": urls,
        "indicator_status": {
            "urgency": group_status(all_signals, "pressure"),
            "credentials": group_status(all_signals, "credentials"),
            "suspicious_link": group_status(all_signals, "link"),
            "financial": group_status(all_signals, "financial"),
            "impersonation": group_status(all_signals, "impersonation"),
        },
        "evidence": [signal["evidence"] for signal in all_signals],
    }
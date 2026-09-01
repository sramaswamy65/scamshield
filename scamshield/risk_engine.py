"""Deterministic scam risk scoring for ScamShield AI.

The engine intentionally stays independent from any LLM.  Every score is
derived from transparent, weighted signals so the classroom demo is repeatable
and the explanation can point back to concrete evidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SignalRule:
    key: str
    label: str
    weight: int
    category: str
    patterns: tuple[str, ...]
    evidence_label: str


SIGNAL_RULES: tuple[SignalRule, ...] = (
    SignalRule(
        "urgent_language",
        "Urgent language",
        10,
        "pressure",
        (
            r"\burgent\b",
            r"\bimmediately\b",
            r"\bact now\b",
            r"\basap\b",
            r"\bwithin\s+\d+\s*(?:hours?|minutes?)\b",
            r"\bfinal notice\b",
            r"\bexpires?\s+(?:today|soon)\b",
        ),
        "pressure to act quickly",
    ),
    SignalRule(
        "threats",
        "Threats or consequences",
        12,
        "pressure",
        (
            r"\bsuspend(?:ed)?\b",
            r"\blocked\b",
            r"\bclose(?:d)?\b",
            r"\blegal action\b",
            r"\barrest\b",
            r"\bpenalt(?:y|ies)\b",
            r"\baccount\s+will\b",
        ),
        "threats or account consequences",
    ),
    SignalRule(
        "password_request",
        "Password or login request",
        16,
        "credentials",
        (
            r"\bpassword\b",
            r"\bpasscode\b",
            r"\blogin details?\b",
            r"\bsign[- ]?in details?\b",
            r"\busername\b",
        ),
        "a request for login credentials",
    ),
    SignalRule(
        "verification_code_request",
        "Verification code request",
        18,
        "credentials",
        (
            r"\bverification code\b",
            r"\bsecurity code\b",
            r"\bone[- ]time code\b",
            r"\botp\b",
            r"\b2fa\b",
            r"\bauthentication code\b",
        ),
        "a request for a one-time or verification code",
    ),
    SignalRule(
        "bank_information_request",
        "Bank information request",
        15,
        "financial",
        (
            r"\bbank account\b",
            r"\brouting number\b",
            r"\baccount number\b",
            r"\bbank details?\b",
            r"\bdebit card\b",
        ),
        "a request for bank or account information",
    ),
    SignalRule(
        "credit_card_request",
        "Credit-card request",
        14,
        "financial",
        (
            r"\bcredit card\b",
            r"\bcard number\b",
            r"\bcvv\b",
            r"\bsecurity code\b",
        ),
        "a request for payment-card details",
    ),
    SignalRule(
        "financial_request",
        "Financial request",
        12,
        "financial",
        (
            r"\b(?:send|pay|transfer|wire|deposit|payment|fee|refund)\b",
            r"\bprocessing fee\b",
            r"\bclaim fee\b",
        ),
        "a request involving money or payment",
    ),
    SignalRule(
        "gift_card_request",
        "Gift-card request",
        18,
        "financial",
        (
            r"\bgift cards?\b",
            r"\bitunes cards?\b",
            r"\bgoogle play cards?\b",
            r"\bsteam cards?\b",
        ),
        "a request for gift cards",
    ),
    SignalRule(
        "cryptocurrency_request",
        "Cryptocurrency request",
        16,
        "financial",
        (
            r"\bbitcoin\b",
            r"\bcrypto(?:currency)?\b",
            r"\bwallet address\b",
            r"\busdt\b",
        ),
        "a request for cryptocurrency",
    ),
    SignalRule(
        "prize_language",
        "Prize or lottery language",
        10,
        "social engineering",
        (
            r"\bwon\b",
            r"\bwinner\b",
            r"\blottery\b",
            r"\bprize\b",
            r"\breward\b",
            r"\bclaim\b",
        ),
        "unexpected prize or reward language",
    ),
    SignalRule(
        "government_impersonation",
        "Government impersonation",
        10,
        "impersonation",
        (
            r"\birs\b",
            r"\btax (?:agency|department|return|refund)\b",
            r"\bsocial security\b",
            r"\bgovernment\b",
            r"\bdepartment of revenue\b",
        ),
        "government or tax-agency impersonation",
    ),
    SignalRule(
        "bank_impersonation",
        "Bank or payment impersonation",
        10,
        "impersonation",
        (
            r"\bbank\b",
            r"\bcredit union\b",
            r"\bpaypal\b",
            r"\bvenmo\b",
            r"\bcash app\b",
        ),
        "a bank or payment-service identity claim",
    ),
    SignalRule(
        "package_impersonation",
        "Package-delivery impersonation",
        8,
        "impersonation",
        (
            r"\bpackage\b",
            r"\bdelivery\b",
            r"\bcourier\b",
            r"\busps\b",
            r"\bups\b",
            r"\bfedex\b",
        ),
        "a package or delivery-service identity claim",
    ),
)


def _first_match(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None


def detect_rule_signals(text: str) -> list[dict[str, Any]]:
    """Return the rules that matched, including evidence and score weights."""

    found: list[dict[str, Any]] = []
    for rule in SIGNAL_RULES:
        evidence = _first_match(text, rule.patterns)
        if evidence:
            found.append(
                {
                    "key": rule.key,
                    "label": rule.label,
                    "weight": rule.weight,
                    "category": rule.category,
                    "evidence": evidence,
                    "evidence_label": rule.evidence_label,
                }
            )
    return found


def classify_score(score: int) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def calculate_score(
    rule_signals: list[dict[str, Any]],
    *,
    url_signals: list[dict[str, Any]] | None = None,
) -> tuple[int, str]:
    """Calculate a capped 0-100 score from rule and URL signals."""

    total = sum(int(signal["weight"]) for signal in rule_signals)
    total += sum(int(signal["weight"]) for signal in (url_signals or []))
    score = max(0, min(100, total))
    return score, classify_score(score)


def group_status(signals: list[dict[str, Any]], group: str) -> bool:
    """Whether any detected signal belongs to a UI indicator group."""

    return any(signal.get("category") == group for signal in signals)
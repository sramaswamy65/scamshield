"""Safe, text-only URL inspection.

ScamShield never opens or requests a URL supplied by a user.  This module only
parses the string and inspects visible URL characteristics.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse
from typing import Any


URL_PATTERN = re.compile(r"(?:(?:https?://)|(?:www\.))[^\s<>()]+", re.IGNORECASE)
SHORTENED_HOSTS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "ow.ly"}
SUSPICIOUS_TLDS = (".xyz", ".top", ".click", ".live", ".zip", ".work")
ACTION_TERMS = re.compile(
    r"(?:verify|verification|login|log-in|secure|update|account|payment|claim|confirm)",
    re.IGNORECASE,
)


def _clean_url(raw_url: str) -> str:
    return raw_url.rstrip(".,!?;:)]}")


def inspect_urls(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return discovered URLs and weighted suspicious URL indicators."""

    urls: list[dict[str, Any]] = []
    signals: list[dict[str, Any]] = []

    for raw_url in URL_PATTERN.findall(text):
        url = _clean_url(raw_url)
        candidate = url if "://" in url else f"http://{url}"
        parsed = urlparse(candidate)
        host = (parsed.hostname or "").lower()
        reasons: list[str] = []

        if not host:
            continue
        if host in SHORTENED_HOSTS:
            reasons.append("shortened URL")
            signals.append(
                {
                    "key": "shortened_url",
                    "label": "Shortened URL",
                    "weight": 10,
                    "category": "link",
                    "evidence": host,
                    "evidence_label": "a link-shortening service hides the destination",
                }
            )
        if parsed.scheme != "https":
            reasons.append("not encrypted with HTTPS")
        if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
            reasons.append("IP address used as destination")
        if "xn--" in host:
            reasons.append("encoded internationalized hostname")
        if host.endswith(SUSPICIOUS_TLDS):
            reasons.append("unusual top-level domain")
        if ACTION_TERMS.search(parsed.path) or ACTION_TERMS.search(host):
            reasons.append("action-oriented path")

        # example.com is intentionally used in the demo. It is never visited,
        # but an action-oriented path still demonstrates what a reviewer would
        # inspect in a real message.
        if host in {"example.com", "example.org", "example.net"} and reasons:
            reasons.append("demo link with a sensitive action path")

        if reasons:
            urls.append(
                {
                    "url": url,
                    "host": host,
                    "reasons": reasons,
                    "suspicious": True,
                }
            )
            if not any(signal["key"] == "suspicious_url" for signal in signals):
                signals.append(
                    {
                        "key": "suspicious_url",
                        "label": "Suspicious link",
                        "weight": 16,
                        "category": "link",
                        "evidence": host,
                        "evidence_label": "the URL has suspicious structural characteristics",
                    }
                )
        else:
            urls.append({"url": url, "host": host, "reasons": [], "suspicious": False})

    return urls, signals
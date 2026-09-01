"""SQLite persistence and demo seeding for ScamShield AI."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "scamshield.db"


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                message_excerpt TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                scam_category TEXT NOT NULL,
                indicators TEXT NOT NULL
            )
            """
        )
        connection.commit()


def save_analysis(result: dict[str, Any]) -> None:
    indicators = [signal["label"] for signal in result.get("signals", [])]
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO analyses (
                timestamp, message_excerpt, risk_score, risk_level,
                scam_category, indicators
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                " ".join(result["message"].split())[:140],
                result["score"],
                result["level"],
                result["category"],
                json.dumps(indicators),
            ),
        )
        connection.commit()


def history_dataframe(limit: int | None = None) -> pd.DataFrame:
    initialize_database()
    query = """
        SELECT timestamp, message_excerpt, risk_score, risk_level,
               scam_category, indicators
        FROM analyses
        ORDER BY timestamp DESC
    """
    params: tuple[Any, ...] = ()
    if limit:
        query += " LIMIT ?"
        params = (limit,)

    with _connect() as connection:
        rows = connection.execute(query, params).fetchall()

    frame = pd.DataFrame([dict(row) for row in rows])
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "message_excerpt",
                "risk_score",
                "risk_level",
                "scam_category",
                "indicators",
            ]
        )
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame["indicators"] = frame["indicators"].apply(
        lambda value: ", ".join(json.loads(value)) if value else "—"
    )
    return frame


def seed_demo_data() -> None:
    """Seed roughly 15 fictional records only when the database is empty."""

    initialize_database()
    with _connect() as connection:
        count = connection.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
    if count:
        return

    from message_analyzer import analyze_message

    samples = [
        "URGENT: Your First National Bank account will be suspended today. Verify your security code and bank account at https://example.com/secure/verify immediately.",
        "Your package is waiting for delivery. Confirm your address at https://example.com/parcel/confirm to avoid a return.",
        "This is the IRS. Your tax refund is on hold. Pay the processing fee within 24 hours at https://example.com/tax/claim.",
        "Congratulations, you are a prize winner! Claim your reward by paying a small processing fee at https://example.com/reward/claim.",
        "Hi Suresh, our project meeting tomorrow is still scheduled for 10:00 AM. See you then.",
        "Your bank needs you to confirm a password and one-time security code right now: https://example.com/bank/login.",
        "A delivery fee is due for your package. Review the notice at http://example.com/delivery/payment.",
        "You won a lottery reward. Send gift cards to complete the claim.",
        "Your social security account requires immediate verification. Submit your details at https://example.com/verify.",
        "Please send the invoice to accounting by Friday. Thanks for your help.",
        "Your payment account is locked. Sign in and update your details at https://example.com/account/update.",
        "Reminder: dentist appointment Tuesday at 2 PM. Reply if you need to reschedule.",
        "Final notice: wire a refund processing fee today or legal action may begin.",
        "The team lunch is moved to Thursday at noon. See you there.",
        "Your package tracking update is available at https://example.com/track.",
    ]

    now = datetime.now(timezone.utc)
    with _connect() as connection:
        for index, message in enumerate(samples):
            result = analyze_message(message)
            indicators = json.dumps([signal["label"] for signal in result["signals"]])
            timestamp = (now - timedelta(hours=index * 7 + 2)).isoformat(
                timespec="seconds"
            )
            connection.execute(
                """
                INSERT INTO analyses (
                    timestamp, message_excerpt, risk_score, risk_level,
                    scam_category, indicators
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    message[:140],
                    result["score"],
                    result["level"],
                    result["category"],
                    indicators,
                ),
            )
        connection.commit()
# ScamShield

ScamShield is a presentation-ready Streamlit application that helps people
decide whether an email, SMS, WhatsApp message, or other text may be a scam or
phishing attempt.

## What it does

- Scores messages with a deterministic, explainable 0–100 risk engine.
- Detects pressure tactics, credential requests, financial asks,
  impersonation, suspicious URL structure, and common scam categories.
- Stores analyses in SQLite and seeds fictional history on first launch.
- Provides a visual investigation trace and safety recommendation.
- Optionally uses OpenAI to improve the wording of the explanation when
  `OPENAI_API_KEY` is available. The model never controls the numeric score.

## Run it

From the project root:

```bash
streamlit run scamshield/app.py --server.port 5000
```

Or use the configured **ScamShield AI** workflow in the Replit workspace.

The app works without an OpenAI key and does not require any external
cybersecurity API. The first run creates `scamshield/data/scamshield.db`.

## Architecture

```text
User
  ↓
Streamlit UI
  ↓
ScamShield Orchestrator
  ↓
Message Analyzer + URL Inspector
  ↓
Risk Engine
  ↓
AI Explanation / Safety Advisor
  ↓
Dashboard & Recommendations
```

## How the score works

The rule engine adds weights for detected indicators and caps the result at
100:

- `0–29`: LOW RISK
- `30–69`: MEDIUM RISK
- `70–100`: HIGH RISK

The score is deterministic. Messages are only parsed as text; URLs are never
opened, requested, or executed.

## Where generative AI is used

If `OPENAI_API_KEY` is configured, the optional safety advisor can rewrite the
evidence-based explanation in concise natural language. If the key is absent,
ScamShield uses its local rule-based explanation. Either way, the risk engine
and recommendation are available.

## Limitations

ScamShield is an educational decision-support tool, not a guarantee that a
message is safe or malicious. Real scams can avoid obvious keywords, and
legitimate messages can contain urgency or links. Verify important requests
through an official website, app, or known phone number.

## Future enhancements

- User-configurable scoring profiles.
- Exportable incident reports.
- Sender/domain reputation checks through an approved security provider.
- Feedback controls to improve organization-specific detection rules.
"""Generate the ScamShield application overview and demo guide PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT = Path(__file__).resolve().parent / "docs" / "ScamShield_App_Overview.pdf"

INK = colors.HexColor("#102B35")
TEAL = colors.HexColor("#1CA9A2")
TEAL_DARK = colors.HexColor("#0A5D61")
PALE_TEAL = colors.HexColor("#E7F6F4")
SLATE = colors.HexColor("#516A73")
LIGHT = colors.HexColor("#F4F8F8")
RED = colors.HexColor("#C74451")
AMBER = colors.HexColor("#A46E13")
GREEN = colors.HexColor("#237A58")
LINE = colors.HexColor("#D9E7E8")


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=33,
            leading=38,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=14,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=14,
            leading=21,
            textColor=SLATE,
            spaceAfter=20,
        ),
        "eyebrow": ParagraphStyle(
            "Eyebrow",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=TEAL_DARK,
            tracking=1.4,
            spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=28,
            textColor=INK,
            spaceBefore=4,
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=INK,
            spaceBefore=10,
            spaceAfter=7,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=SLATE,
            spaceAfter=8,
        ),
        "body_dark": ParagraphStyle(
            "BodyDark",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=INK,
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=SLATE,
            spaceAfter=4,
        ),
        "small_dark": ParagraphStyle(
            "SmallDark",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=INK,
            spaceAfter=4,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#D9F5F1"),
        ),
        "center": ParagraphStyle(
            "Center",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=SLATE,
            alignment=TA_CENTER,
        ),
        "quote": ParagraphStyle(
            "Quote",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=22,
            textColor=INK,
            alignment=TA_CENTER,
        ),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def pill(text: str, background: colors.Color, foreground: colors.Color) -> Table:
    table = Table([[p(text, ParagraphStyle("pill", parent=styles()["small_dark"], textColor=foreground, alignment=TA_CENTER))]], colWidths=[1.05 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.5, background),
                ("ROUNDEDCORNERS", [8, 8, 8, 8]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def callout(text: str, background: colors.Color = PALE_TEAL, border: colors.Color = TEAL) -> Table:
    table = Table([[p(text, styles()["body_dark"])]], colWidths=[6.75 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("LINEBEFORE", (0, 0), (0, -1), 4, border),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return table


def card(title: str, body: str, accent: colors.Color = TEAL) -> Table:
    content = [
        p(title, ParagraphStyle("card-title", parent=styles()["small_dark"], fontName="Helvetica-Bold", textColor=accent)),
        Spacer(1, 5),
        p(body, styles()["small_dark"]),
    ]
    table = Table([[content]], colWidths=[2.08 * inch], rowHeights=[1.2 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("LINEABOVE", (0, 0), (-1, 0), 3, accent),
                ("LEFTPADDING", (0, 0), (-1, -1), 11),
                ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def bullet(text: str) -> Paragraph:
    return p(f"<font color='#1CA9A2'>•</font>&nbsp;&nbsp;{text}", styles()["body"])


def header_footer(canvas, document) -> None:
    canvas.saveState()
    width, height = letter
    if document.page > 1:
        canvas.setFillColor(TEAL)
        canvas.rect(0.58 * inch, height - 0.43 * inch, 0.24 * inch, 0.05 * inch, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(INK)
        canvas.drawString(0.9 * inch, height - 0.46 * inch, "SCAMSHIELD")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(SLATE)
        canvas.drawRightString(width - 0.58 * inch, height - 0.46 * inch, "Application overview & demo guide")
        canvas.setStrokeColor(LINE)
        canvas.line(0.58 * inch, height - 0.56 * inch, width - 0.58 * inch, height - 0.56 * inch)
    canvas.setStrokeColor(LINE)
    canvas.line(0.58 * inch, 0.52 * inch, width - 0.58 * inch, 0.52 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SLATE)
    canvas.drawString(0.58 * inch, 0.34 * inch, "Deterministic risk scoring • local-first analysis • URLs never opened")
    canvas.drawRightString(width - 0.58 * inch, 0.34 * inch, f"{document.page}")
    canvas.restoreState()


def build_pdf() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = BaseDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.58 * inch,
        leftMargin=0.58 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.72 * inch,
        title="ScamShield — Application Overview & Demo Guide",
        author="ScamShield",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="normal",
    )
    document.addPageTemplates([PageTemplate(id="scamshield", frames=[frame], onPage=header_footer)])
    s = styles()
    story: list[object] = []

    # Cover
    story.extend(
        [
            Spacer(1, 0.55 * inch),
            p("SCAMSHIELD / PROJECT BRIEF", s["eyebrow"]),
            p("ScamShield", s["title"]),
            p("A presentation-ready safety tool for spotting scam and phishing messages before they cause harm.", s["subtitle"]),
            Spacer(1, 0.35 * inch),
            Table(
                [[p("S", ParagraphStyle("cover-mark", parent=s["title"], fontSize=28, leading=30, textColor=colors.HexColor("#071B20"), alignment=TA_CENTER))]],
                colWidths=[0.75 * inch],
                rowHeights=[0.75 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), TEAL),
                        ("BOX", (0, 0), (-1, -1), 0, TEAL),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                ),
            ),
            Spacer(1, 0.45 * inch),
            callout(
                "<b>Purpose</b><br/>ScamShield helps users slow down and make a safer decision when an email, SMS, WhatsApp message, or other text feels suspicious."
            ),
            Spacer(1, 0.35 * inch),
            p("Built for a reliable seven-minute GenAI classroom demonstration.", s["quote"]),
            Spacer(1, 0.2 * inch),
            p("The numeric score is always produced by transparent local rules. Optional generative AI improves explanation wording only.", s["center"]),
            PageBreak(),
        ]
    )

    # At a glance
    story.extend(
        [
            p("01 / AT A GLANCE", s["eyebrow"]),
            p("A calm answer to a high-pressure problem.", s["h1"]),
            p(
                "ScamShield turns a suspicious message into three things a user can understand quickly: a risk score, the evidence behind that score, and a safe next action.",
                s["body"],
            ),
            Spacer(1, 0.1 * inch),
            Table(
                [[
                    card("MESSAGE INTAKE", "Paste a message or choose one of five fictional demonstration samples.", TEAL),
                    card("EVIDENCE", "See pressure tactics, credential requests, financial asks, impersonation, and URL signals.", AMBER),
                    card("NEXT ACTION", "Get a clear recommendation based on LOW, MEDIUM, or HIGH risk.", RED),
                ]],
                colWidths=[2.18 * inch, 2.18 * inch, 2.18 * inch],
                style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]),
            ),
            Spacer(1, 0.28 * inch),
            p("What makes the demo trustworthy", s["h2"]),
            bullet("<b>Deterministic:</b> the same message produces the same score every time."),
            bullet("<b>Local-first:</b> it works without an OpenAI API key or a security API."),
            bullet("<b>Safe by default:</b> URLs are treated as untrusted text and never visited."),
            bullet("<b>Traceable:</b> every result points back to visible indicators."),
            Spacer(1, 0.2 * inch),
            callout(
                "<b>Demo checkpoint</b><br/>The fictional Bank Account Warning sample returns <font color='#C74451'><b>95% HIGH RISK</b></font>. The Safe Message sample returns <font color='#237A58'><b>0% LOW RISK</b></font>.",
                background=colors.HexColor("#FFF7E3"),
                border=AMBER,
            ),
            PageBreak(),
        ]
    )

    # Architecture
    story.extend(
        [
            p("02 / ARCHITECTURE", s["eyebrow"]),
            p("A simple pipeline with clear responsibilities.", s["h1"]),
            p(
                "The app is intentionally understandable for beginner and intermediate Python developers. Each stage does one job and passes evidence forward.",
                s["body"],
            ),
            Spacer(1, 0.12 * inch),
            Table(
                [[p("USER", s["center"])], [p("↓", ParagraphStyle("arrow", parent=s["quote"], fontSize=18, leading=20, textColor=TEAL, alignment=TA_CENTER))],
                 [p("STREAMLIT UI", s["center"])], [p("↓", ParagraphStyle("arrow2", parent=s["quote"], fontSize=18, leading=20, textColor=TEAL, alignment=TA_CENTER))],
                 [p("SCAMSHIELD ORCHESTRATOR", s["center"])], [p("↓", ParagraphStyle("arrow3", parent=s["quote"], fontSize=18, leading=20, textColor=TEAL, alignment=TA_CENTER))],
                 [p("MESSAGE ANALYZER  +  URL INSPECTOR", s["center"])], [p("↓", ParagraphStyle("arrow4", parent=s["quote"], fontSize=18, leading=20, textColor=TEAL, alignment=TA_CENTER))],
                 [p("DETERMINISTIC RISK ENGINE", s["center"])], [p("↓", ParagraphStyle("arrow5", parent=s["quote"], fontSize=18, leading=20, textColor=TEAL, alignment=TA_CENTER))],
                 [p("AI EXPLANATION / SAFETY ADVISOR", s["center"])], [p("↓", ParagraphStyle("arrow6", parent=s["quote"], fontSize=18, leading=20, textColor=TEAL, alignment=TA_CENTER))],
                 [p("DASHBOARD  +  RECOMMENDATION", s["center"])]],
                colWidths=[6.5 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                        ("LEFTPADDING", (0, 0), (-1, -1), 14),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                ),
            ),
            Spacer(1, 0.25 * inch),
            p("Project structure", s["h2"]),
            Table(
                [
                    [p("<b>File</b>", s["small_dark"]), p("<b>Responsibility</b>", s["small_dark"])],
                    [p("app.py", s["small"]), p("Five-page Streamlit interface, navigation, samples, and presentation UI.", s["small"])],
                    [p("risk_engine.py", s["small"]), p("Weighted signals, score calculation, and LOW / MEDIUM / HIGH classification.", s["small"])],
                    [p("message_analyzer.py", s["small"]), p("Orchestrates language and URL checks and assigns a scam category.", s["small"])],
                    [p("url_analyzer.py", s["small"]), p("Parses visible URLs without opening or requesting them.", s["small"])],
                    [p("database.py", s["small"]), p("Creates SQLite storage, saves analyses, and seeds fictional history.", s["small"])],
                    [p("ai_explainer.py", s["small"]), p("Optional OpenAI wording with a deterministic local fallback.", s["small"])],
                ],
                colWidths=[1.65 * inch, 4.85 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), PALE_TEAL),
                        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                ),
            ),
            PageBreak(),
        ]
    )

    # Score model
    story.extend(
        [
            p("03 / RISK MODEL", s["eyebrow"]),
            p("Evidence first. Explanation second.", s["h1"]),
            p(
                "ScamShield uses weighted pattern matching to create a 0–100 score. The score is never delegated to a language model, which keeps the result repeatable and auditable.",
                s["body"],
            ),
            Table(
                [
                    [p("<b>Risk level</b>", s["small_dark"]), p("<b>Range</b>", s["small_dark"]), p("<b>Meaning</b>", s["small_dark"])],
                    [p("LOW RISK", ParagraphStyle("low", parent=s["small"], textColor=GREEN, fontName="Helvetica-Bold")), p("0–29", s["small"]), p("No major indicators detected. Continue to verify unexpected requests.", s["small"])],
                    [p("MEDIUM RISK", ParagraphStyle("medium", parent=s["small"], textColor=AMBER, fontName="Helvetica-Bold")), p("30–69", s["small"]), p("Suspicious patterns are present. Verify independently before taking action.", s["small"])],
                    [p("HIGH RISK", ParagraphStyle("high", parent=s["small"], textColor=RED, fontName="Helvetica-Bold")), p("70–100", s["small"]), p("Multiple high-confidence signals are present. Do not respond or click links.", s["small"])],
                ],
                colWidths=[1.45 * inch, 0.85 * inch, 4.2 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), PALE_TEAL),
                        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                ),
            ),
            Spacer(1, 0.22 * inch),
            p("Signals the engine checks", s["h2"]),
            Table(
                [[
                    [p("<b>Pressure</b>", s["small_dark"]), p("Urgent language<br/>Threats and consequences", s["small"])],
                    [p("<b>Credentials</b>", s["small_dark"]), p("Passwords<br/>Verification codes<br/>Bank or card details", s["small"])],
                    [p("<b>Money</b>", s["small_dark"]), p("Payments<br/>Gift cards<br/>Cryptocurrency<br/>Prize fees", s["small"])],
                    [p("<b>Identity</b>", s["small_dark"]), p("Bank impersonation<br/>Government impersonation<br/>Package delivery impersonation", s["small"])],
                ]],
                colWidths=[1.55 * inch] * 4,
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                        ("INNERGRID", (0, 0), (-1, -1), 0.45, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ]
                ),
            ),
            Spacer(1, 0.2 * inch),
            callout(
                "<b>Important safety boundary</b><br/>The app treats every URL as untrusted text. It may flag a URL based on visible characteristics such as an action-oriented path, a shortened host, or a non-HTTPS scheme, but it never connects to the destination.",
                background=colors.HexColor("#FFF2F2"),
                border=RED,
            ),
            PageBreak(),
        ]
    )

    # Demo guide
    story.extend(
        [
            p("04 / LIVE DEMO", s["eyebrow"]),
            p("A seven-minute walkthrough.", s["h1"]),
            p("Use the following sequence to show the full product story without relying on an external API or live malicious content.", s["body"]),
            Table(
                [
                    [p("<b>Time</b>", s["small_dark"]), p("<b>What to show</b>", s["small_dark"]), p("<b>Talking point</b>", s["small_dark"])],
                    [p("0:00–1:00", s["small"]), p("Dashboard", s["small_dark"]), p("Point out seeded history, the risk distribution, and the four KPIs.", s["small"])],
                    [p("1:00–2:00", s["small"]), p("Analyze Message", s["small_dark"]), p("Choose Bank Account Warning to load a fictional suspicious message.", s["small"])],
                    [p("2:00–3:00", s["small"]), p("Progress sequence", s["small_dark"]), p("Show the five-stage investigation: read, language, URLs, score, recommendation.", s["small"])],
                    [p("3:00–4:15", s["small"]), p("AI Risk Analysis", s["small_dark"]), p("Show the 95% HIGH RISK score, evidence cards, and highlighted phrases.", s["small"])],
                    [p("4:15–5:15", s["small"]), p("Investigation", s["small_dark"]), p("Walk through Message Analyzer, URL Inspector, Risk Engine, and Safety Advisor.", s["small"])],
                    [p("5:15–6:15", s["small"]), p("Recommended Action", s["small_dark"]), p("Emphasize not responding, not clicking, and verifying independently.", s["small"])],
                    [p("6:15–7:00", s["small"]), p("Safe Message", s["small_dark"]), p("Run the safe sample to demonstrate the LOW result and the system’s restraint.", s["small"])],
                ],
                colWidths=[0.85 * inch, 1.45 * inch, 4.2 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), PALE_TEAL),
                        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                ),
            ),
            Spacer(1, 0.25 * inch),
            p("Recommended sample sequence", s["h2"]),
            Table(
                [[
                    card("01 / BANK WARNING", "Expected result: 95% HIGH RISK", RED),
                    card("02 / SAFE MESSAGE", "Expected result: 0% LOW RISK", GREEN),
                    card("03 / OPTIONAL", "Try package, IRS, or prize examples to show MEDIUM results.", AMBER),
                ]],
                colWidths=[2.18 * inch, 2.18 * inch, 2.18 * inch],
                style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]),
            ),
            PageBreak(),
        ]
    )

    # Operations
    story.extend(
        [
            p("05 / RUN & OPERATE", s["eyebrow"]),
            p("Ready for a classroom demo.", s["h1"]),
            p("ScamShield is designed to run locally in the Replit environment with no required API key and no external cybersecurity service.", s["body"]),
            p("Launch command", s["h2"]),
            Table(
                [[p("streamlit run scamshield/app.py --server.port 5000", s["code"])]],
                colWidths=[6.5 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), INK),
                        ("BOX", (0, 0), (-1, -1), 0, INK),
                        ("LEFTPADDING", (0, 0), (-1, -1), 13),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 13),
                        ("TOPPADDING", (0, 0), (-1, -1), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ]
                ),
            ),
            Spacer(1, 0.18 * inch),
            p("Storage and optional AI", s["h2"]),
            bullet("SQLite history is created automatically at <b>scamshield/data/scamshield.db</b>."),
            bullet("If the database is empty, the app seeds approximately 15 fictional analyses."),
            bullet("Without an OpenAI key, the local rule-based Safety Advisor is used."),
            bullet("With <b>OPENAI_API_KEY</b>, OpenAI may improve explanation wording; it cannot change the score."),
            Spacer(1, 0.18 * inch),
            p("Presentation checklist", s["h2"]),
            bullet("Open the Dashboard and confirm the history cards are populated."),
            bullet("Run Bank Account Warning and confirm HIGH RISK."),
            bullet("Open AI Risk Analysis and point to the highlighted evidence."),
            bullet("Open Investigation and show all four components as completed."),
            bullet("Open Recommended Action and read the safety checklist."),
            bullet("Run Safe Message and confirm LOW RISK."),
            Spacer(1, 0.18 * inch),
            callout(
                "<b>Privacy reminder</b><br/>For a classroom demo, use the included fictional examples. Avoid pasting real personal, financial, or account information into the application.",
                background=colors.HexColor("#FFF7E3"),
                border=AMBER,
            ),
            PageBreak(),
        ]
    )

    # Limitations / future
    story.extend(
        [
            p("06 / BOUNDARIES", s["eyebrow"]),
            p("A decision aid, not a guarantee.", s["h1"]),
            p("ScamShield makes suspicious patterns easier to see, but no keyword-based tool can prove that a message is safe or malicious.", s["body"]),
            Table(
                [[
                    [p("<b>Limitations</b>", s["small_dark"]), bullet("Real scams can avoid obvious keywords."), bullet("Legitimate messages can contain urgency or links."), bullet("A LOW score does not guarantee legitimacy.")],
                    [p("<b>Future enhancements</b>", s["small_dark"]), bullet("User-configurable scoring profiles."), bullet("Exportable incident reports."), bullet("Approved sender/domain reputation checks.")],
                ]],
                colWidths=[3.2 * inch, 3.2 * inch],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                        ("INNERGRID", (0, 0), (-1, -1), 0.45, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 12),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                        ("TOPPADDING", (0, 0), (-1, -1), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                ),
            ),
            Spacer(1, 0.35 * inch),
            HRFlowable(width="100%", thickness=1, color=LINE, spaceBefore=4, spaceAfter=15),
            p("Closing message", s["eyebrow"]),
            p("Pause. Verify. Stay in control.", s["quote"]),
            Spacer(1, 0.12 * inch),
            p("ScamShield gives users a moment of clarity when a message is designed to create pressure.", s["center"]),
        ]
    )

    document.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build_pdf()
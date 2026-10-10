"""Builds a downloadable PDF report from a saved analysis.

All text that comes from a resume, a job description or a job posting is
untrusted. ReportLab treats paragraph text as XML-like markup, so every such
string goes through _safe() first: it strips control characters, replaces
characters the built-in PDF fonts cannot draw, clips very long values, and
escapes markup characters. User text can therefore never break the layout or
inject markup into the report.
"""

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Flowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.analysis_records import AnalysisDetailOut

PAGE_MARGIN = 18 * mm
DISCLAIMER = (
    "Estimated fit indicator, not a hiring probability. It does not predict "
    "interview or hiring outcomes."
)

_base = getSampleStyleSheet()
TITLE_STYLE = ParagraphStyle(
    "ReportTitle", parent=_base["Title"], fontSize=18, leading=22, alignment=0, spaceAfter=4
)
SUBTITLE_STYLE = ParagraphStyle(
    "ReportSubtitle", parent=_base["Normal"], fontSize=10, textColor=colors.HexColor("#555555"), spaceAfter=8
)
SCORE_STYLE = ParagraphStyle(
    "ReportScore", parent=_base["Normal"], fontSize=15, leading=19, spaceBefore=6, spaceAfter=2
)
HEADING_STYLE = ParagraphStyle(
    "ReportHeading", parent=_base["Heading2"], fontSize=12, spaceBefore=12, spaceAfter=6, keepWithNext=1
)
BODY_STYLE = ParagraphStyle("ReportBody", parent=_base["Normal"], fontSize=9.5, leading=13)
SMALL_STYLE = ParagraphStyle(
    "ReportSmall", parent=BODY_STYLE, fontSize=8.5, leading=11, textColor=colors.HexColor("#555555")
)
CELL_STYLE = ParagraphStyle("ReportCell", parent=BODY_STYLE, fontSize=8.5, leading=11)
BULLET_STYLE = ParagraphStyle("ReportBullet", parent=BODY_STYLE, leftIndent=12, bulletIndent=2)


def _safe(text: str, limit: int | None = None) -> str:
    """Makes untrusted text safe to place inside a ReportLab paragraph."""
    characters: list[str] = []
    for character in text:
        if character.isspace():
            characters.append(" ")
        elif character.isprintable():
            characters.append(character)
    cleaned = "".join(characters)

    if limit is not None and len(cleaned) > limit:
        cleaned = cleaned[: limit - 3].rstrip() + "..."

    # The built-in PDF fonts only cover Western European characters.
    cleaned = cleaned.encode("cp1252", errors="replace").decode("cp1252")
    return escape(cleaned)


def _draw_footer(canvas: Canvas, document: SimpleDocTemplate) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(PAGE_MARGIN, 10 * mm, "Estimated fit indicator, not a hiring probability.")
    canvas.drawRightString(A4[0] - PAGE_MARGIN, 10 * mm, f"Page {document.page}")
    canvas.restoreState()


def _weights_summary(detail: AnalysisDetailOut) -> str:
    weights = detail.weights
    values = {
        "Skills": weights.skills,
        "Semantic": weights.semantic,
        "Experience": weights.experience,
        "Education": weights.education,
    }
    total = sum(values.values())
    if total <= 0:
        return ""
    return ", ".join(f"{name} {round(value / total * 100)}%" for name, value in values.items())


def _skills_paragraph(label: str, names: list[str], empty: str) -> Paragraph:
    value = ", ".join(_safe(name, 60) for name in names) if names else empty
    return Paragraph(f"<b>{label}:</b> {value}", BODY_STYLE)


def _category_table(detail: AnalysisDetailOut) -> Table:
    rows: list[list[Paragraph]] = [
        [
            Paragraph("<b>Category</b>", CELL_STYLE),
            Paragraph("<b>Score</b>", CELL_STYLE),
            Paragraph("<b>Weight</b>", CELL_STYLE),
            Paragraph("<b>How it was calculated</b>", CELL_STYLE),
        ]
    ]
    for category in detail.categories:
        if category.applicable:
            score_text = f"{round(category.score * 100)}%"
            weight_text = f"{round(category.weight * 100)}%"
        else:
            score_text = "N/A"
            weight_text = "-"
        rows.append(
            [
                Paragraph(_safe(category.label, 60), CELL_STYLE),
                Paragraph(score_text, CELL_STYLE),
                Paragraph(weight_text, CELL_STYLE),
                Paragraph(_safe(category.explanation, 600), CELL_STYLE),
            ]
        )

    table = Table(rows, colWidths=[32 * mm, 16 * mm, 16 * mm, 106 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def build_report_pdf(detail: AnalysisDetailOut) -> bytes:
    """Renders a saved analysis as a PDF and returns the file's bytes."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,
        topMargin=PAGE_MARGIN,
        bottomMargin=PAGE_MARGIN + 6 * mm,
        title="Resume match report",
        author="ResumeMatch",
    )

    subtitle = f"Analysis date: {detail.created_at.strftime('%d %b %Y')}"
    if detail.is_demo:
        subtitle += "  |  DEMO DATA (fictional sample)"

    story: list[Flowable] = [
        Paragraph(
            f"{_safe(detail.job_title, 150)} at {_safe(detail.company, 100)}",
            TITLE_STYLE,
        ),
        Paragraph(subtitle, SUBTITLE_STYLE),
        Paragraph(f"<b>Overall score: {detail.overall_score} / 100</b>", SCORE_STYLE),
        Paragraph(DISCLAIMER, SMALL_STYLE),
    ]

    weights_text = _weights_summary(detail)
    if weights_text:
        story.append(Paragraph(f"Category weights used: {weights_text}.", SMALL_STYLE))

    story.append(Paragraph("Category breakdown", HEADING_STYLE))
    story.append(_category_table(detail))

    story.append(Paragraph("Skills", HEADING_STYLE))
    story.append(_skills_paragraph("Matched required", [s.name for s in detail.matched_required], "None"))
    story.append(Spacer(1, 3))
    story.append(_skills_paragraph("Missing required", detail.missing_required, "None missing"))
    story.append(Spacer(1, 3))
    story.append(_skills_paragraph("Matched preferred", [s.name for s in detail.matched_preferred], "None"))
    story.append(Spacer(1, 3))
    story.append(_skills_paragraph("Missing preferred", detail.missing_preferred, "None missing"))

    story.append(Paragraph("Supporting evidence from your resume", HEADING_STYLE))
    if detail.evidence:
        for item in detail.evidence:
            story.append(Paragraph(f"<b>{_safe(item.requirement, 150)}</b>", BODY_STYLE))
            story.append(
                Paragraph(
                    f'"{_safe(item.snippet, 400)}" (similarity {round(item.similarity * 100)}%)',
                    SMALL_STYLE,
                )
            )
            story.append(Spacer(1, 4))
    else:
        story.append(
            Paragraph("Not enough text on the resume or job description to compare passages.", BODY_STYLE)
        )

    story.append(Paragraph("Resume improvement suggestions", HEADING_STYLE))
    if detail.suggestions:
        for suggestion in detail.suggestions:
            story.append(Paragraph(f"<b>Original:</b> {_safe(suggestion.original, 400)}", BODY_STYLE))
            story.append(Paragraph(f"<b>Suggested:</b> {_safe(suggestion.suggested, 400)}", BODY_STYLE))
            story.append(Paragraph(f"Why: {_safe(suggestion.why_changed, 400)}", SMALL_STYLE))
            story.append(Spacer(1, 6))
        story.append(
            Paragraph(
                "Suggestions only rephrase what you already wrote. Keep wording only if it "
                "stays truthful to your real experience.",
                SMALL_STYLE,
            )
        )
    else:
        story.append(Paragraph("No suggestions for this analysis.", BODY_STYLE))

    story.append(Paragraph("Learning roadmap", HEADING_STYLE))
    if detail.roadmap:
        for item in detail.roadmap:
            story.append(
                Paragraph(
                    f"<b>{_safe(item.skill, 60)}</b> (about {item.estimated_weeks} weeks)",
                    BODY_STYLE,
                )
            )
            story.append(Paragraph(_safe(item.reason, 300), SMALL_STYLE))
            for step in item.steps:
                story.append(Paragraph(_safe(step, 300), BULLET_STYLE, bulletText="•"))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No missing required skills, so no roadmap is needed.", BODY_STYLE))

    story.append(Paragraph("How this was scored", HEADING_STYLE))
    for note in detail.calculation_notes:
        story.append(Paragraph(_safe(note, 400), BULLET_STYLE, bulletText="•"))

    document.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    return buffer.getvalue()
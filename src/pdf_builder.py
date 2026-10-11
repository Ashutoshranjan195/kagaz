from __future__ import annotations

import logging
from pathlib import Path
import urllib.request

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

_FONT_URL = (
    "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/"
    "NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf"
)
_FONT_NAME: str | None = None


def _ensure_devanagari_font(fonts_dir: Path) -> str:
    """Register Noto Sans Devanagari; fall back to Helvetica on failure."""
    global _FONT_NAME
    if _FONT_NAME is not None:
        return _FONT_NAME

    fonts_dir = Path(fonts_dir)
    fonts_dir.mkdir(parents=True, exist_ok=True)
    target = fonts_dir / "NotoSansDevanagari.ttf"

    if not target.exists():
        try:
            logger.info("Downloading Devanagari font to %s", target)
            urllib.request.urlretrieve(_FONT_URL, str(target))
        except Exception as exc:
            logger.warning("Font download failed (%s); using Helvetica.", exc)
            _FONT_NAME = "Helvetica"
            return _FONT_NAME

    try:
        pdfmetrics.registerFont(TTFont("NotoDeva", str(target)))
        pdfmetrics.registerFont(TTFont("NotoDeva-Bold", str(target)))
        pdfmetrics.registerFont(TTFont("NotoDeva-Italic", str(target)))
        pdfmetrics.registerFont(TTFont("NotoDeva-BoldItalic", str(target)))
        pdfmetrics.registerFontFamily(
            "NotoDeva",
            normal="NotoDeva",
            bold="NotoDeva-Bold",
            italic="NotoDeva-Italic",
            boldItalic="NotoDeva-BoldItalic",
        )
        try:
            pdfmetrics.registerFont(
                TTFont("Emoji", r"C:\Windows\Fonts\seguiemj.ttf")
            )
        except Exception as exc:
            logger.warning("Emoji font unavailable (%s).", exc)
        _FONT_NAME = "NotoDeva"
        logger.info("Registered NotoDeva font from %s", target)
    except Exception as exc:
        logger.warning("Font registration failed (%s); using Helvetica.", exc)
        _FONT_NAME = "Helvetica"
    return _FONT_NAME


def build_pdf(hunt: dict, out_path: Path) -> Path:
    """Build a printable A4 PDF for the hunt."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fonts_dir = out_path.parent.parent / "assets" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    font = _ensure_devanagari_font(fonts_dir)

    pdf = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
    )

    base = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "KagazTitle", parent=base["Title"], fontName=font,
        fontSize=22, leading=26, alignment=1, spaceAfter=6,
    )
    intro_style = ParagraphStyle(
        "KagazIntro", parent=base["Normal"], fontName=font,
        fontSize=11, leading=14, alignment=1, textColor=colors.grey,
    )
    item_style = ParagraphStyle(
        "KagazItem", parent=base["Normal"], fontName=font,
        fontSize=10, leading=13,
    )
    section_style = ParagraphStyle(
        "KagazSection", parent=base["Normal"], fontName=font,
        fontSize=13, leading=16, spaceBefore=6, spaceAfter=4,
    )
    parent_style = ParagraphStyle(
        "KagazParent", parent=base["Normal"], fontName=font,
        fontSize=9, leading=12, textColor=colors.grey,
    )

    content = []
    content.append(Paragraph(hunt["title"], title_style))
    content.append(Spacer(1, 6 * mm))
    content.append(Paragraph(hunt["intro"], intro_style))
    content.append(Spacer(1, 8 * mm))

    cells = []
    for item in hunt["items"]:
        emoji = item.get("emoji", "")
        text_hi = item.get("text_hi", "")
        text_en = item.get("text_en", "")
        hint = item.get("hint", "")
        cell_text = (
            f'<font name="Emoji">{emoji}</font>  \u2610  {text_hi}<br/>'
            f"{text_en}<br/>"
            f"<i>{hint}</i>"
        )
        cells.append(Paragraph(cell_text, item_style))

    if len(cells) % 2 == 1:
        cells.append(Paragraph("", item_style))

    table_data = [cells[i:i + 2] for i in range(0, len(cells), 2)]
    table = Table(table_data, colWidths=[pdf.width / 2.0 - 2 * mm] * 2)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    content.append(KeepTogether([table]))
    content.append(Spacer(1, 10 * mm))

    content.append(KeepTogether([
        Paragraph("Bonus Challenge", section_style),
        Paragraph(hunt["bonus_challenge"], item_style),
    ]))
    content.append(Spacer(1, 6 * mm))
    content.append(KeepTogether([
        Paragraph("Parent Note", section_style),
        Paragraph(hunt["parent_note"], parent_style),
    ]))

    pdf.build(content)
    return out_path
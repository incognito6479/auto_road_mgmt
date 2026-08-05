"""
management/pdf_fonts.py

Shared Unicode font setup for reportlab-based PDF generators (contract.py,
lesson_book.py). The base14 PDF fonts (Helvetica etc.) don't cover the
Uzbek apostrophe letters or Cyrillic, so a bundled TTF (DejaVu Sans,
permissively licensed for embedding) is registered on first use instead.
"""

import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_FONTS_REGISTERED = False


def ensure_fonts_registered():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(FONTS_DIR, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")))
    # Without this, Paragraph's <b> markup has no bold face to switch to for
    # the "DejaVu" font and silently renders as regular weight — underline
    # markup isn't affected since it doesn't depend on font substitution.
    pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu", boldItalic="DejaVu-Bold")
    _FONTS_REGISTERED = True

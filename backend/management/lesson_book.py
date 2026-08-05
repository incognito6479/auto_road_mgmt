"""
management/lesson_book.py

Generates the "Amaliy mashq bajarish varaqasi" (practical driving-lesson
exercise booklet) as a PDF, based on the driving school's paper template.
The 37-exercise table and its columns are hand-filled during actual lessons
(sana/baho/imzo etc. stay blank) — only the header identity fields and QR
code are filled in per enrollment.
"""

import os
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from management.models import Car
from management.pdf_fonts import ensure_fonts_registered

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
QR_IMAGE_PATH = os.path.join(ASSETS_DIR, "lesson_book_qr.png")
DEFAULT_PHOTO_PATH = os.path.join(ASSETS_DIR, "default_photo.png")
# Falls back to this when no QR image file has been supplied — same
# destination the printed booklet's QR code is meant to point students to.
LESSON_BOOK_QR_URL = "https://autoroadschool.taplink.ws"

EXERCISE_ROWS = [
    "(Avtotrenajyorda yoki avtotransport vositasida)*. Haydovchining o'rindiqda joylashishi. "
    "Boshqaruv hamda nazorat-o'lchov asboblari bilan tanishish",
    "(Avtotrenajyorda yoki avtotransport vositasida)*. Dvigatelni ishga tushirishga tayyorgarlik va uni ishga "
    "tushirish, qizdirish, nazorat-o'lchov asboblarini kuzatish",
    "(Avtotrenajyorda yoki avtotransport vositasida)*. Avtotransport vositasini boshqarish uslublari",
    "Harakatlanishni boshlashda, uzatmalarni yuqoriga va pastga almashtirganda, ohista va keskin tormozlashda, "
    "to'xtashda boshqaruv organlaridan foydalanish",
    "Harakatni boshlash va to'g'ri yo'nalishda yuqori va pastki uzatmalarni navbati bilan o'zgartirib harakatlanish",
    "To'g'ri yo'nalishda va burilishlarda turli uzatmalarda harakatlanish",
    "Belgilangan joyda to'xtash va qayrilib olish",
    "Ilon izi yo'li va izli taxta bo'ylab harakatlanish; to'g'ri harakatlanishdan ilon izi yo'li bo'ylab "
    "harakatlanishga o'tish",
    "Tonnelda va aylanma yo'lda harakatlanish; tonnelga to'g'ridan kirish va unda harakatlanish",
    "Cheklangan oraliqda avtotransport vositasini majmuaviy boshqarish",
    "Nazorat tekshiruvi",
    "Yo'l (aholi punkti)ga chiqish. Transport oqimida harakatlanish. To'xtash va harakatni boshlash",
    "Avtotransport vositasini to'xtab turish joyiga qo'yish. Yo'lning tor qismlarida ro'para harakatlanish",
    "Chorrahalardan o'tish. Chorrahani baholash (ko'rinish darajasi, bo'laklar soni, transport vositalarining "
    "mavjudligi va h.k.)",
    "Teng ahamiyatli bo'lmagan va teng ahamiyatli yo'llar kesishgan chorrahalarda to'g'riga harakatlanish, "
    "burilish va qayrilib olish",
    "Yo'l (aholi punkti)ga chiqish. Avtotransport vositasining yon tevaragida xavfsiz makonni shakllantirish",
    "Avtotransport vositasini to'xtab turish joyiga qo'yish. Yo'lning tor qismlarida ro'para harakatlanish",
    "Chorrahalardan o'tish. Yaqinlashib kelayotgan transport vositasigacha bo'lgan masofani aniqlash",
    "Teng ahamiyatli bo'lmagan va teng ahamiyatli yo'llar kesishgan chorrahalarda to'g'riga harakatlanish, "
    "burilish va qayrilib olish",
    "Avtotransport vositasini sutkaning qorong'i vaqtlarida boshqarish",
] + ["Avtotransport vositasini turli yo'l sharoitlarida boshqarish bo'yicha ko'nikmalarini takomillashtirish"] * 16 + [
    "Imtihon YHXBB RIB yoki Imtihon markazida",
]


def _format_date(d):
    return f"{d.strftime('%d-%m-%Y')} yil" if d else "—"


def _resolve_photo_source(student):
    if student.image:
        try:
            path = student.image.path
            if os.path.exists(path):
                return path
        except (ValueError, OSError):
            pass
    return DEFAULT_PHOTO_PATH if os.path.exists(DEFAULT_PHOTO_PATH) else None


def _resolve_qr_source():
    if os.path.exists(QR_IMAGE_PATH):
        return QR_IMAGE_PATH
    try:
        import qrcode
        buf = BytesIO()
        qrcode.make(LESSON_BOOK_QR_URL).save(buf, format="PNG")
        buf.seek(0)
        return buf
    except Exception:
        return None


def generate_lesson_book_pdf(enrollment):
    """Returns the "Amaliy mashq bajarish varaqasi" PDF as bytes for the given Enrollment."""
    ensure_fonts_registered()

    student = enrollment.student
    group = enrollment.group
    instructor = enrollment.instructor

    student_name = student.full_name or student.phone
    group_name = group.name if group else "—"
    instructor_name = instructor.full_name or instructor.phone if instructor else "—"
    car = Car.objects.filter(instructor=instructor, is_active=True).first() if instructor else None
    car_display = car.car_name if car else "—"
    started_display = _format_date(group.started_at) if group else "—"
    ends_display = _format_date(group.ends_at) if group else "—"

    styles = {
        "title": ParagraphStyle("title", fontName="DejaVu-Bold", fontSize=12, leading=15, alignment=TA_CENTER, spaceAfter=8),
        "label": ParagraphStyle("label", fontName="DejaVu", fontSize=8.3, leading=11, alignment=TA_LEFT),
        "value": ParagraphStyle("value", fontName="DejaVu-Bold", fontSize=8.3, leading=11, alignment=TA_LEFT),
        "th": ParagraphStyle("th", fontName="DejaVu-Bold", fontSize=6.6, leading=8, alignment=TA_CENTER),
        "td": ParagraphStyle("td", fontName="DejaVu", fontSize=6.8, leading=8.6, alignment=TA_LEFT),
        "td_center": ParagraphStyle("td_center", fontName="DejaVu", fontSize=7, leading=8.6, alignment=TA_CENTER),
    }

    story = [Paragraph("AMALIY MASHQ BAJARISH VARAQASI", styles["title"])]

    header_rows = [
        ("O'quvchining familiyasi ismi", student_name),
        ("O'qigan guruhining tartib raqami №", group_name),
        ("Haydovchi-yo'riqchining familiyasi va ismi", instructor_name),
        ("Yengil avtomobil markasi", car_display),
        ("O'qishning boshlanishi", started_display),
        ("O'qishning tugashi", ends_display),
        ("Ta'lim muassasaning boshlig'i", "U. IMOMOV_________________"),
    ]

    photo_source = _resolve_photo_source(student)
    photo_cell = Image(photo_source, width=22 * mm, height=22 * mm) if photo_source else ""
    qr_source = _resolve_qr_source()
    qr_cell = Image(qr_source, width=22 * mm, height=22 * mm) if qr_source else ""

    header_table_rows = []
    for i, (label, value) in enumerate(header_rows):
        row = [
            photo_cell if i == 0 else "",
            Paragraph(label, styles["label"]),
            Paragraph(value, styles["value"]),
            qr_cell if i == 0 else "",
        ]
        header_table_rows.append(row)

    header_table = Table(
        header_table_rows,
        colWidths=[26 * mm, 74 * mm, 68 * mm, 26 * mm],
        rowHeights=[22 * mm / 7] * 7,
    )
    header_table.setStyle(TableStyle([
        ("SPAN", (0, 0), (0, 6)),
        ("SPAN", (3, 0), (3, 6)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("ALIGN", (3, 0), (3, 0), "CENTER"),
        ("LEFTPADDING", (1, 0), (2, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4))

    ex_header = [
        Paragraph("№", styles["th"]),
        Paragraph("Vazifalari nomi", styles["th"]),
        Paragraph("Mashqlar umumiy soat", styles["th"]),
        Paragraph("Mashqlar raqami", styles["th"]),
        Paragraph("Mashq soatlari", styles["th"]),
        Paragraph("Sana", styles["th"]),
        Paragraph("Baho", styles["th"]),
        Paragraph("O'quvchining imzosi", styles["th"]),
        Paragraph("Ustaning imzosi", styles["th"]),
    ]
    ex_table_data = [ex_header]
    for i, text in enumerate(EXERCISE_ROWS, start=1):
        ex_table_data.append([
            Paragraph(str(i), styles["td_center"]),
            Paragraph(text, styles["td"]),
            "", "", "", "", "", "", "",
        ])
    ex_table_data.append([
        "", Paragraph("Jami soat:", styles["th"]), "", "", "", "", "", "", "",
    ])

    ex_table = Table(
        ex_table_data,
        colWidths=[10 * mm, 76 * mm, 17 * mm, 16 * mm, 16 * mm, 14 * mm, 12 * mm, 16 * mm, 17 * mm],
        repeatRows=1,
    )
    ex_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
        ("SPAN", (0, -1), (1, -1)),
        ("ALIGN", (1, -1), (1, -1), "RIGHT"),
    ]))
    story.append(ex_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Qo'shimcha haydovchi-yo'riqchilar", styles["th"]))
    story.append(Spacer(1, 2))

    extra_header = [
        Paragraph("", styles["th"]),
        Paragraph("Haydovchi-yo'riqchi F.I.SH", styles["th"]),
        Paragraph("Avtotransport markasi", styles["th"]),
        Paragraph("Avtotransport davlat raqami", styles["th"]),
    ]
    extra_table = Table(
        [extra_header] + [[Paragraph(str(i), styles["td_center"]), "", "", ""] for i in range(1, 4)],
        colWidths=[9 * mm, 65 * mm, 60 * mm, 60 * mm],
        rowHeights=[6 * mm] * 4,
    )
    extra_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(extra_table)

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=6 * mm, bottomMargin=6 * mm, leftMargin=8 * mm, rightMargin=8 * mm,
        title=f"Amaliy mashq varaqasi - {student_name}",
    )
    doc.build(story)
    return buf.getvalue()

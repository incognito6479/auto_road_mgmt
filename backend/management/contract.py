"""
management/contract.py

Generates the student enrollment agreement ("shartnoma") as a PDF, based on
the driving school's paper contract template. Static clauses (sections 1-9)
are reproduced from that template; only the fields called out below are
filled in per enrollment.
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_FONTS_REGISTERED = False


def _ensure_fonts_registered():
    """
    The base14 PDF fonts (Helvetica etc.) don't cover the Uzbek apostrophe
    letters or Cyrillic, so a bundled Unicode TTF (DejaVu Sans, permissively
    licensed for embedding) is registered on first use instead.
    """
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(FONTS_DIR, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")))
    _FONTS_REGISTERED = True


# ---------------------------------------------------------------------------
# Static organization details (the "O'quv muassasasi" side of every contract)
# ---------------------------------------------------------------------------
ORG_NAME = '"AUTO ROAD SCHOOL" MCHJ'
ORG_DIRECTOR = "UMAR IMOMOV XAZRATOVICH"
ORG_INN = "311571804"
ORG_ADDRESS_LINES = [
    ORG_NAME,
    "Samarqand viloyati, Tayloq tumani, Birlik MFY, Yuqori Tayloq qishlog'i, 56-uy",
    "H/R 20208000307476049001",
    f"MFO 01133, INN {ORG_INN}, OKONX",
    '"INVEST FINANCE BANK" AT bankining Samarqand viloyat filiali',
    "140100, Samarqand sh., O'zbekiston ko'chasi, 22",
    "Tel: +998 99 727 04 44",
    ORG_NAME,
    "(imzo) _________________ IMOMOV UMAR",
]


def _format_date(d):
    return d.strftime("%d-%m-%Y") if d else "____-__-____"


def _format_passport_plain(user):
    if not user.passport_serie or not user.passport_number:
        return "—"
    return f"{user.passport_serie} {user.passport_number}"


def _format_passport_with_number_sign(user):
    if not user.passport_serie or not user.passport_number:
        return "—"
    return f"{user.passport_serie} № {user.passport_number}"


def _format_phone(phone):
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    if len(digits) == 12 and digits.startswith("998"):
        return f"+{digits[0:3]} {digits[3:5]} {digits[5:8]} {digits[8:10]} {digits[10:12]}"
    return f"+{digits}" if digits else "—"


def _format_money(amount):
    return f"{amount:,}" if amount else "0"


def generate_contract_pdf(enrollment):
    """Returns the contract PDF as bytes for the given Enrollment."""
    _ensure_fonts_registered()

    student = enrollment.student
    category_name = enrollment.category.name if enrollment.category else "—"
    contract_number = str(enrollment.id)
    student_name = student.full_name or student.phone
    passport = _format_passport_plain(student)
    passport_with_sign = _format_passport_with_number_sign(student)
    phone_display = _format_phone(student.phone)
    date_display = _format_date(enrollment.created_at.date() if enrollment.created_at else None)

    group = enrollment.group
    if group and group.started_at and group.ends_at:
        study_period = f"{group.started_at.isoformat()} dan {group.ends_at.isoformat()}gacha"
    else:
        study_period = "—"
    price_display = "Tekin (Bonus)" if enrollment.enrolled_free else _format_money(enrollment.enrolled_amount)

    styles = {
        "small": ParagraphStyle("small", fontName="DejaVu", fontSize=8, leading=10, alignment=TA_LEFT),
        "title": ParagraphStyle("title", fontName="DejaVu-Bold", fontSize=11.5, leading=14, alignment=TA_CENTER, spaceAfter=6),
        "date_line": ParagraphStyle("date_line", fontName="DejaVu", fontSize=8.5, leading=11),
        "date_line_r": ParagraphStyle("date_line_r", fontName="DejaVu", fontSize=8.5, leading=11, alignment=TA_LEFT),
        "intro": ParagraphStyle("intro", fontName="DejaVu", fontSize=8.5, leading=11.5, alignment=TA_JUSTIFY, spaceBefore=6, spaceAfter=6),
        "section": ParagraphStyle("section", fontName="DejaVu-Bold", fontSize=9.5, leading=13, alignment=TA_CENTER, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontName="DejaVu", fontSize=8.3, leading=10.8, alignment=TA_JUSTIFY, spaceAfter=3),
        "table_cell": ParagraphStyle("table_cell", fontName="DejaVu", fontSize=7.6, leading=9.6, alignment=TA_LEFT),
        "table_header": ParagraphStyle("table_header", fontName="DejaVu-Bold", fontSize=7.6, leading=9.6, alignment=TA_CENTER),
        "table_data": ParagraphStyle("table_data", fontName="DejaVu", fontSize=7.8, leading=10, alignment=TA_CENTER),
    }

    story = []

    story.append(Paragraph(f"Shartnoma raqami: <b>{contract_number}</b>", styles["small"]))
    story.append(Paragraph(f"Pasport seria va raqam: <b>{passport}</b>", styles["small"]))
    story.append(Paragraph(f"Tashkilot inn: <b>{ORG_INN}</b>", styles["small"]))
    story.append(Spacer(1, 8))

    story.append(Paragraph(f"{contract_number} SONLI SHARTNOMA", styles["title"]))

    date_row = Table(
        [[
            Paragraph('"______"_______________', styles["date_line"]),
            Paragraph(f"{date_display}-yil Samarqand viloyati", styles["date_line_r"]),
        ]],
        colWidths=[85 * mm, 85 * mm],
    )
    date_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(date_row)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        f'{ORG_NAME} boshlig\'i {ORG_DIRECTOR} bundan keyingi matnlarda "O\'quv muassasasi" deb nomlanuvchi, '
        "O'zbekiston Respublikasi qonunchiligi va amaldagi Ustaviga asoslanib ish yurituvchi bir tomondan va fuqaro "
        f'{student_name}, bundan keyingi matnlarda "Ta\'lim oluvchi" deb nomlanuvchi, amaldagi O\'zbekiston Respublikasi '
        "qonunchiligi va amaldagi Fuqarolik kodeksi talablariga asoslanib ish yurituvchi ikkinchi tomondan mazkur "
        "shartnomani quyidagilar to'g'risida tuzdik:",
        styles["intro"],
    ))

    story.append(Paragraph("1. SHARTNOMANING PREDMETI", styles["section"]))
    story.append(Paragraph(
        f'1.1. "O\'quv muassasasi" mazkur shartnoma shartlariga asosan, «Ta\'lim oluvchini» {category_name} toifali '
        "avtotransport vositalari haydovchilarini tayyorlash toifali avtotransport vositasi haydovchiligiga tayyorlaydi.",
        styles["body"],
    ))

    story.append(Paragraph("2. \"O'QUV MUASSASASI\" NING HUQUQ VA MAJBURIYATLARI", styles["section"]))
    for text in [
        "2.1. Avtotransport vositalari haydovchilarini tayyorlash va qayta tayyorlash o'quv jarayonini O'zbekiston "
        "Respublikasi Vazirlar Mahkamasining Qarorlari, amaldagi rahbariy-me'yoriy xujjatlar hamda belgilangan tartibda "
        "tasdiqlangan yagona o'quv rejasi va dasturlariga asosan olib boradi. O'quv dasturlarida belgilangan o'quv "
        "mashg'ulotlarining to'la xajmda bajarlishini ta'minlaydi.",
        "2.2. \"Ta'lim oluvchi\"ning o'qishga qabul qilinishi uchun taqdim etishi lozim bo'lgan xujjatlarni, amaldagi "
        "rahbariy-me'yoriy xujjatlar asosida to'liq talab qiladi.",
        "2.3. \"Ta'lim oluvchi\" uchun avtomototransport vositalari xaydovchilarini tayyorlash va qayta tayyorlash "
        "muddatlarini tasdiqlangan rejalar va o'quv dasturlariga muvofiq belgilaydi.",
        "2.4. \"Ta'lim oluvchi\"ga tegishli dastur asosida o'quv muassasasidagi bitiruv imtixonlarini test sinovlari "
        "asosida muvaffaqiyatli topshirganidan so'ng, unga ta'limni tugatganligi to'g'risidagi, belgilangan na'munadagi "
        "guvohnomani beradi.",
        "2.5. Zarurat tug'ilganda \"Ta'lim oluvchi\"lar safiga qabul qilinayotgan nomzodlarning bilim darajasi va amaliy "
        "mahoratlarini aniqlash uchun suhbatdan o'tkazadi.",
        "2.6. \"Ta'lim oluvchi\"larga ta'lim olish uchun qulay sharoitlar (talab darajasida jixozlangan o'quv va sinf "
        "xonalari, amaliy mashg'ulotlarni o'tashlari uchun texnik soz bo'lgan o'quv avtomobili bilan ta'minlash) yaratadi.",
        "2.7. Mazkur shartnomaning 4-bo'lim 4.2-bandiga asosan oldindan o'qish pulini to'lamagan \"Ta'lim oluvchi\"lar "
        "o'qishga qabul qilinmaydi va ta'lim olishdan chetlatiladi.",
        "2.8. «Ta'lim oluvchi» uchun ushbu shartnomaning 3-bo'limi bandlari orqali belgilangan vazifalar, o'quvchi "
        "tomonidan qo'pol ravishda buzilsa, unga nisbatdan mos ravishda ta'sir choralari ko'riladi.",
        "2.9. «Ta'lim oluvchi»dan o'quv mashg'ulotlarini qo'yib yuborgan kunlarini tasdiqlovchi xujjatlarni taqdim "
        "etishini talab qiladi.",
        "2.10. Agar \"Ta'lim oluvchi\" Dasturda belgilangan o'quv mashg'ulotlarining 20 foizidan ortig'ini sababsiz "
        "qoldirsa va sababini tasdiqlovchi xujjatlarni taqdim etmasa, \"Ta'lim oluvchi\" buyruq asosida ta'lim "
        "oluvchilar safidan chiqariladi va o'qishga qayta qabul qilish umumiy qoidalar asosida amalga oshiriladi.",
        "2.11. Agar «Ta'lim oluvchi» Dasturda belgilangan o'quv mashg'ulotlarining 20 foizi miqdorini sababli ravishda "
        "qoldirsa, o'quv dasturi bo'yicha quyib yuborgan soatlarini xisobga olgan xolda, «Ta'lim oluvchi» boshqa o'quv "
        "guruhiga o'tkaziladi.",
    ]:
        story.append(Paragraph(text, styles["body"]))

    story.append(Paragraph("3. «TA'LIM OLUVCHI» NING HUQUQ VA MAJBURIYATLARI", styles["section"]))
    for text in [
        "3.1. \"Ta'lim oluvchi\" O'zbekiston Respublikasi Vazirlar Mahkamasining Qarorlari, amaldagi rahbariy-me'yoriy "
        "xujjatlar talablariga asosan, o'qishga qabul qilish uchun tegishli xujjatlarni «O'quv muassasasi»ga taqdim etadi.",
        f"3.2. O'quv mashg'ulotlari soatlari va xajmining, haydovchilarni «{category_name}» toifali avtotransport "
        "vositalari haydovchilarini tayyorlash toifali avtotransport vositasi haydovchiligiga tayyorlashdagi o'quv "
        "reja va dasturlarida belgilangan to'liq xajmda olib borilishini «O'quv muassasasi»dan talab qiladi.",
        "3.3. Avtotransport vositalari xaydovchilarini tegishli toifalarga sifatli tayyorlash va qayta tayyorlashga "
        "imkoniyat yaratish uchun qulay sharoitlar tashkil etilishini «O'quv muassasasi»dan talab etadi.",
        "3.4. O'qish uchun haq to'lashni ushbu shartnomaning 4-bo'lim 4.2-bandida ko'rsatilgan miqdorda, o'quv guruhi "
        "tashkil etilgunga qadar tegishli bank yoki bank shaxobchalari orqali naqd pul to'lash, plastik kartochkalar "
        "orqali to'lash yoki pul o'tkazish yo'li bilan «O'quv muassasasi»ning xisob raqamiga pul tushirish yo'li bilan "
        "amalga oshiradi.",
        "3.5. «O'quv muassasasi» tomonidan o'tkaziladigan barcha tadbirlarda faol qatnashadi.",
        "3.6. «O'quv muassasasi» ning ichki tartib qoidalariga qat'iy rioya qiladi.",
        "3.7. O'qish yakunida o'quv Dasturi bo'yicha belgilangan tartibda o'quv muassasasidagi ichki imtixonlarni "
        "belgilangan tartibdagi test sinovlari asosida topshiradi.",
    ]:
        story.append(Paragraph(text, styles["body"]))

    section4_header = Paragraph("4. O'QUV MASHG'ULOTINING TURI, HAJMI, MUDDATI VA UMUMIY QIYMATI", styles["section"])
    section4_intro = Paragraph("4.1. O'quv mashg'ulotlarining qiymat miqdori va muddatini aniqlash.", styles["body"])

    table4 = Table(
        [
            [
                Paragraph("O'quv mashg'ulotlari (ta'lim) turi", styles["table_header"]),
                Paragraph("Nazariy soat", styles["table_header"]),
                Paragraph("Amaliy soat", styles["table_header"]),
                Paragraph("Amaliy boshqaruv soati", styles["table_header"]),
                Paragraph("O'qish muddati", styles["table_header"]),
                Paragraph("O'qish narxi (so'm)", styles["table_header"]),
            ],
            [
                Paragraph("Nazariy va amaliy mashg'ulotlar", styles["table_data"]),
                "", "", "",
                Paragraph(study_period, styles["table_data"]),
                Paragraph(price_display, styles["table_data"]),
            ],
        ],
        colWidths=[42 * mm, 20 * mm, 20 * mm, 25 * mm, 43 * mm, 25 * mm],
    )
    table4.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(KeepTogether([section4_header, section4_intro, Spacer(1, 3), table4]))
    story.append(Spacer(1, 4))

    story.append(Paragraph(
        "4.2. Tomonlar kelishuviga asosan, «Ta'lim oluvchi» to'lov summasining 30 % (o'ttiz foiz) kam bo'lmagan mablag' "
        "miqdori to'lovini o'quv mashg'ulotlari boshlanishidan oldin, qolgan qismini esa (to'la xisob-kitobni) o'quv "
        "Dasturining birinchi yarmi tugaguniga qadar to'liq amalga oshiradi.",
        styles["body"],
    ))
    story.append(Paragraph(
        "4.3. «Ta'lim oluvchi» da avtomobilni boshqarishni o'rganish bo'yicha qo'shimcha dars mashg'ulotlarini o'tish "
        "istagi bo'lgan taqdirda, yozma ravishda ariza bilan murojaat etadi va kalkulyatsiya bo'yicha bank va bank "
        "shaxobchalari orqali tegishli mablag'ni «O'quv muassasasi» xisob raqamiga to'laydi.",
        styles["body"],
    ))

    story.append(Paragraph("5. ALOHIDA SHARTLAR", styles["section"]))
    for text in [
        "5.1. Hukumat qarorlari yoki farmonlariga asosan yoqilg'i-moy va boshqa tovar maxsulotlarining narxlari va ish "
        "xaqining oshishi munosabati bilan o'quv jarayonini tashkil etishga sarflanadigan xarajatlar ko'paysa, shunga "
        "mos ravishda to'lov miqdori o'zgarishi va oshishi mumkin. Bu borada «O'quv muassasasi» 10 kun ichida «Ta'lim "
        "oluvchi»ga xabar beradi va shu davr ichida «Ta'lim oluvchi» belgilangan to'lovni amalga oshiradi.",
        "5.2. O'quv guruhi to'liq jamlangandan keyin, «Ta'lim oluvchi»lar bilan o'qish boshlanadi va bu to'g'rida "
        "o'qishning boshlanishi haqida «O'quv muassasa» bo'yicha buyruq chiqariladi.",
        "5.3. «Ta'lim oluvchi» «O'quv muassasasi» da o'quv Dasturini to'liq o'tib, «Ta'lim oluvchi» ichki test "
        "imtihonlarini topshirgan va o'qiganlik haqidagi guvohnoma olgan kuni o'qish muddati tugagan va mazkur shartnoma "
        "bo'yicha ikki tomonlama olingan majburiyatlar to'liq bajarilgan deb hisoblanadi.",
    ]:
        story.append(Paragraph(text, styles["body"]))

    story.append(Paragraph("6. TOMONLARNING JAVOBGARLIGI", styles["section"]))
    for text in [
        "6.1. Shartnomadagi to'lov miqdorini o'z vaqtida to'liq miqdorda to'lamasa «Ta'lim oluvchi»dan har bir "
        "kechiktirilgan kun uchun umumiy o'qish pulining 0,4%, lekin bu miqdor shartnomada ko'rsatilgan umumiy o'qish "
        "pulining 15% dan ko'p bo'lmasligi kerak.",
        "6.2. Ushbu shartnomaning 2-bo'lim 2.3-bandida qayd etilgan hamda o'qish muddatlari sababsiz ravishda «O'quv "
        "muassasasi» tomonidan uzaytirilsa, «O'quv muassasasi» «Ta'lim oluvchiga» uzaytirilgan har bir kun uchun "
        "shartnomadagi umumiy summaning 0,4% miqdorida penya to'laydi, lekin bu miqdor shartnomada ko'rsatilgan umumiy "
        "o'qish pulining 15% dan ko'p bo'lmasligi kerak.",
        "6.3. Agar «Ta'lim oluvchi» ushbu shartnomaning 2-bo'lim 2.10-bandi va 3-bo'lim 3.5-bandiga asosan «Ta'lim "
        "oluvchi»lar safidan chiqarilgan bo'lsa «O'quv muassasasi» «Ta'lim oluvchi» tomonidan to'langan pul "
        "mablag'larini qaytarmaydi.",
        "6.4. Agar «Ta'lim oluvchi» o'quvchilar safidan sababli ravishda chiqarilgan bo'lsa, uning to'lagan pul "
        "mablag'lari miqdori o'qish davrida xaqiqiy sarflangan xarajatlari bo'yicha xisob-kitob qilinadi va qolgan "
        "qoldiq mablag'lar «Ta'lim oluvchi»ga qonunda belgilangan tartibda uning shaxsiy hisob raqamiga o'tkazish "
        "orqali qaytarib beriladi.",
        "6.5. Agar ushbu shartnoma bo'yicha bahs va tortishuvlar ro'y bersa, ular muzokara yo'li bilan hal etiladi, aks "
        "holda tomonlar tegishli sud idoralariga murojaat etish xuquqiga ega.",
    ]:
        story.append(Paragraph(text, styles["body"]))

    story.append(Paragraph("7. FORS-MAJOR HOLATLAR", styles["section"]))
    story.append(Paragraph(
        "7.1. Ushbu shartnomadagi o'zaro olingan majburiyatlar ularga bog'liq bo'lmagan sabablarga ko'ra to'la yoki "
        "qisman bajarilmasa, tomonlar javobgarlikka tortilmaydi.",
        styles["body"],
    ))

    story.append(Paragraph("8. SHARTNOMANING AMAL QILISHI, UNI O'ZGARTIRISH VA BEKOR QILISH", styles["section"]))
    for text in [
        "8.1. Shartnoma imzolangan kundan boshlab kuchga kiradi va «Ta'lim oluvchi» tomonidan o'qish Dasturini to'liq "
        "o'tab, avtomototransport vositalari xaydovchilarini tayyorlash kurslarini tugatganligi to'g'risidagi "
        "guvohnomani olgunga qadar amal qiladi.",
        "8.2. Ushbu shartnoma taraflarning kelishuviga muvofiq o'zgartirilishi yoki bekor qilinishi mumkin.",
        "8.3. Shartnoma ikki nusxada tuziladi va bir xil kuchga ega.",
    ]:
        story.append(Paragraph(text, styles["body"]))

    org_cell = Paragraph("<br/>".join(ORG_ADDRESS_LINES), styles["table_cell"])
    student_lines = [
        student_name,
        "Manzili: ",
        f"Pasport seria va raqam: {passport_with_sign}",
        f"Telefonlar: (uy) {phone_display}",
        "",
        "Imzo:_________________________________",
    ]
    student_cell = Paragraph("<br/>".join(student_lines), styles["table_cell"])

    table9 = Table(
        [
            [Paragraph('"O\'QUV MUASSASASI"', styles["table_header"]), Paragraph('"TA\'LIM OLUVCHI"', styles["table_header"])],
            [org_cell, student_cell],
        ],
        colWidths=[85 * mm, 85 * mm],
    )
    table9.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    section9_header = Paragraph("9. TOMONLAR XUQUQIY MANZILLARI VA REKVIZITLARI", styles["section"])
    story.append(KeepTogether([section9_header, Spacer(1, 3), table9]))

    from io import BytesIO
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=14 * mm, bottomMargin=14 * mm, leftMargin=16 * mm, rightMargin=16 * mm,
        title=f"Shartnoma {contract_number}",
    )
    doc.build(story)
    return buf.getvalue()

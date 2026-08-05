"""
management/dispatch_log.py

Generates the car's daily dispatch log ("Йўл варақаси") as an Excel
workbook, based on the driving school's paper booklet template — one sheet
per requested date, each an exact copy of the single-page template
(dispatch_log_page_template.xlsx, itself extracted from one page of the
school's original 110-page pre-built booklet, styles and all) with only the
fields that come from our data filled in.
"""

import os
from io import BytesIO

from openpyxl import load_workbook

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "assets", "dispatch_log_page_template.xlsx")
MAX_DATES = 62  # two months at a time is plenty for one print run

# Fixed business hours the garage operates on (source: the original
# template's own reference data), not something that varies per car or
# date.
PLANNED_DEPARTURE_HOUR = 7
PLANNED_RETURN_HOUR = 19

UZ_WEEKDAYS = ["Душанба", "Сешанба", "Чоршанба", "Пайшанба", "Жума", "Шанба", "Якшанба"]
UZ_MONTHS = [
    "январь", "февраль", "март", "апрель", "май", "июнь",
    "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
]


def _format_uz_date(d):
    return f"{UZ_WEEKDAYS[d.weekday()]} «{d.day}» {UZ_MONTHS[d.month - 1]} {d.year} й."


def _instructor_short_name(full_name):
    """First and last word only (drops a middle patronymic, e.g. "Usmonov
    Sherxon Ibragimovich" -> "Usmonov Sherxon"), matching the template's own
    original name-shortening formula — the field isn't wide enough for a
    full three-part name."""
    words = (full_name or "").split()
    if len(words) <= 2:
        return full_name or ""
    return f"{words[0]} {words[1]}"


def _fill_page(ws, car, model_name, plate_number, instructor_name, instructor_license, d):
    # copy_worksheet doesn't carry over print_area (it's a workbook-level
    # defined name, not a plain sheet attribute) — every sheet needs its own.
    ws.print_area = "A1:AP33"
    ws.cell(row=1, column=42).value = None  # unused external "booklet number" field
    ws.cell(row=3, column=15, value=car.id)
    ws.cell(row=6, column=7, value=_format_uz_date(d))
    ws.cell(row=8, column=14, value=model_name)
    ws.cell(row=9, column=12, value=plate_number)
    ws.cell(row=10, column=9, value=instructor_name)
    ws.cell(row=10, column=17, value=instructor_license)
    ws.cell(row=15, column=7, value=PLANNED_DEPARTURE_HOUR)
    ws.cell(row=17, column=7, value=PLANNED_RETURN_HOUR)


def generate_dispatch_log_excel(car, dates):
    """
    Returns the dispatch log workbook as bytes, with one sheet/page per date
    in `dates` (a list of `date` objects, used in the given order).
    """
    if not dates:
        raise ValueError("At least one date is required.")
    if len(dates) > MAX_DATES:
        raise ValueError(f"At most {MAX_DATES} dates can be generated at once.")

    model_name, _, plate_number = (car.car_name or "").partition(" ")
    instructor = car.instructor
    instructor_name = _instructor_short_name(instructor.full_name) if instructor else ""
    instructor_license = (
        f"{instructor.license_series or ''}{instructor.license_number or ''}" if instructor else ""
    )

    wb = load_workbook(TEMPLATE_PATH)
    base_ws = wb.active

    used_titles = set()
    for i, d in enumerate(dates):
        ws = base_ws if i == 0 else wb.copy_worksheet(base_ws)
        title = d.strftime("%d.%m.%Y")
        if title in used_titles:
            title = f"{title} ({i + 1})"
        used_titles.add(title)
        ws.title = title
        _fill_page(ws, car, model_name, plate_number, instructor_name, instructor_license, d)

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()

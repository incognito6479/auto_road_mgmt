"""
management/helpers.py

Small, dependency-free parsing and lookup-or-create utilities used by the
Excel import (management/import_excel.py). Pulled out of that module so the
row-by-row import loop stays readable — nothing in here is import-specific
business logic, just "turn this messy cell value into a clean field value"
and "find or create this related object".
"""

import re
from datetime import date, datetime

from management.models import Agent, Category, Group, User

CERT_SERIES_RE = re.compile(r"^([A-Za-z]{2})\s*[\s\xa0]*(\d+)$")
PASSPORT_RE = re.compile(r"^([A-Za-z]{2})[\s\xa0]*(\d+)$")
DIGITS_RE = re.compile(r"\D+")


def clean_text(value):
    """Cell value -> trimmed string, or None if blank/whitespace-only."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def smart_title(name):
    """
    ALL-CAPS Latin-script Uzbek names -> "Ashurov Mahmudxon O'g'li".
    Python's str.title() mangles the o'g'li/qizi apostrophe suffix
    ("O'G'LI".title() -> "O'G'Li"); this only touches the first letter of
    each whitespace-separated word instead.
    """
    words = name.split()
    return " ".join(w[0].upper() + w[1:].lower() for w in words if w)


def parse_full_name(raw):
    text = clean_text(raw)
    if not text:
        return None
    return smart_title(re.sub(r"\s+", " ", text))


def normalize_phone(raw):
    """
    9-digit local number (with or without stray text attached, e.g.
    "933490344 амаки") -> "998XXXXXXXXX". Returns None if it can't be
    turned into a plausible Uzbek mobile number.
    """
    text = clean_text(raw)
    if not text:
        return None
    digits = DIGITS_RE.sub("", text)
    if not digits:
        return None
    if digits.startswith("998") and len(digits) == 12:
        return digits
    if len(digits) == 9:
        return "998" + digits
    return None


def parse_jshshr(raw):
    text = clean_text(raw)
    if not text:
        return None
    digits = DIGITS_RE.sub("", text)
    return int(digits) if digits else None


def parse_passport(raw):
    """"AC 2695808" / "AC\\xa02695808" / "AC2695808" -> ("AC", 2695808)."""
    text = clean_text(raw)
    if not text:
        return None, None
    match = PASSPORT_RE.match(text)
    if not match:
        return None, None
    serie, number = match.groups()
    return serie.upper(), int(number)


def parse_certificate(raw):
    """
    Course-completion certificate cell -> (series, number, unparsed_note).
    Handles "SA 000006873" (series + number), bare numeric IDs like
    "773163" (number only, per the business's own convention for older
    records), and genuinely unparseable text (kept verbatim as a note
    instead of being forced into the number field).
    """
    text = clean_text(raw)
    if not text:
        return None, None, None
    match = CERT_SERIES_RE.match(text)
    if match:
        series, number = match.groups()
        if len(number) <= 9:
            return series.upper(), number, None
        return None, None, text
    digits = DIGITS_RE.sub("", text)
    if digits and digits == text.replace(" ", "") and len(digits) <= 9:
        return None, digits, None
    return None, None, text


def parse_excel_date(raw):
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    text = clean_text(raw)
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def to_money(raw):
    """Sheet amounts are written in thousands (1000 means 1,000,000 so'm)."""
    if raw is None:
        return 0
    if isinstance(raw, str):
        raw = DIGITS_RE.sub("", raw)
        if not raw:
            return 0
    try:
        return int(float(raw) * 1000)
    except (TypeError, ValueError):
        return 0


class ImportContext:
    """
    Per-run caches and counters shared across the helper get-or-create
    functions below, so the import loop doesn't hit the database for the
    same category/group/agent on every row, and every synthesized phone
    number is guaranteed unique against both the DB and the rest of the
    file being imported.
    """

    def __init__(self):
        self.categories = {}
        self.groups = {}
        self.agents = {}
        self.used_phones = set(User.objects.values_list("phone", flat=True))
        self._placeholder_phone_seq = 0
        # Seeded from the current count so a second run (e.g. after fixing a
        # data issue) doesn't retry the same "import-1", "import-2", ...
        # phone values and collide with Agent.phone's unique constraint.
        self._placeholder_agent_seq = Agent.objects.filter(phone__startswith="import-").count()
        self.warnings = []
        self.created = {
            "categories": 0, "groups": 0, "agents": 0,
            "students": 0, "enrollments": 0, "payments": 0, "bonus_payments": 0,
        }

    def warn(self, row_number, message):
        self.warnings.append(f"{row_number}-qator: {message}")

    def next_placeholder_phone(self):
        while True:
            self._placeholder_phone_seq += 1
            candidate = f"998000{self._placeholder_phone_seq:06d}"
            if candidate not in self.used_phones:
                return candidate

    def reserve_phone(self, phone):
        self.used_phones.add(phone)


def get_or_create_category(ctx, name):
    key = name.strip().upper()
    if key in ctx.categories:
        return ctx.categories[key]
    category = Category.objects.filter(name__iexact=key).first()
    if category is None:
        category = Category.objects.create(name=key, price=0)
        ctx.created["categories"] += 1
    ctx.categories[key] = category
    return category


def get_or_create_group(ctx, name, category, started_at, ends_at, branch):
    key = name.strip()
    if key in ctx.groups:
        return ctx.groups[key]
    group = Group.objects.filter(name=key).first()
    if group is None:
        status = Group.Status.FINISHED if (ends_at and ends_at < date.today()) else Group.Status.STARTED
        group = Group.objects.create(
            branch=branch,
            category=category,
            name=key,
            started_at=started_at,
            ends_at=ends_at,
            status=status,
        )
        ctx.created["groups"] += 1
    ctx.groups[key] = group
    return group


def get_or_create_agent(ctx, nickname, branch):
    key = nickname.strip()
    cache_key = key.lower()
    if cache_key in ctx.agents:
        return ctx.agents[cache_key]
    agent = Agent.objects.filter(full_name__iexact=key).first()
    if agent is None:
        ctx._placeholder_agent_seq += 1
        agent = Agent.objects.create(
            branch=branch,
            full_name=key,
            phone=f"import-{ctx._placeholder_agent_seq}",
            notes="Excel import orqali qo'shilgan — telefon raqami mavjud emas.",
        )
        ctx.created["agents"] += 1
    ctx.agents[cache_key] = agent
    return agent


def get_or_create_student(ctx, row_number, jshshr, phone, full_name, phone2, passport_serie, passport_number, birth_date, branch):
    """
    Looks up an existing student by JSHSHR (Uzbekistan's per-person national
    ID, so it's the one reliable natural key even when phone is missing or
    duplicated across siblings), reusing that User for a second enrollment
    if found. Otherwise creates a new student. Phone is deduplicated against
    every phone used so far in this run (and the DB) — the app's login
    (`User.objects.get(phone=...)`) breaks outright if two accounts share a
    number, so a colliding or missing phone always falls back to a unique
    synthetic placeholder rather than risk that.
    """
    existing = None
    if jshshr:
        existing = User.objects.filter(role=User.Role.STUDENT, jshshr=jshshr).first()

    if existing:
        updated_fields = []
        if not existing.phone and phone and phone not in ctx.used_phones:
            existing.phone = phone
            ctx.reserve_phone(phone)
            updated_fields.append("phone")
        if not existing.passport_serie and passport_serie:
            existing.passport_serie = passport_serie
            existing.passport_number = passport_number
            updated_fields.extend(["passport_serie", "passport_number"])
        if not existing.birth_date and birth_date:
            existing.birth_date = birth_date
            updated_fields.append("birth_date")
        if not existing.branch and branch:
            existing.branch = branch
            updated_fields.append("branch")
        if updated_fields:
            existing.save(update_fields=updated_fields + ["updated_at"])
        return existing, False

    final_phone = phone
    if not final_phone or final_phone in ctx.used_phones:
        if phone:
            ctx.warn(row_number, f"telefon raqami boshqa o'quvchida band ({phone}) — vaqtinchalik raqam berildi.")
        final_phone = ctx.next_placeholder_phone()
    ctx.reserve_phone(final_phone)

    student = User(
        role=User.Role.STUDENT,
        branch=branch,
        full_name=full_name,
        phone=final_phone,
        phone2=phone2,
        jshshr=jshshr,
        passport_serie=passport_serie,
        passport_number=passport_number,
        birth_date=birth_date,
    )
    # User.save() sets the initial password from jshshr automatically when
    # one isn't already set — same convention StudentCreateSerializer uses.
    student.save()
    ctx.created["students"] += 1
    return student, True

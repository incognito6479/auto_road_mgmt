"""
management/management/commands/seed_test_data.py

Wipes every row in every app model except superuser accounts, then seeds
a realistic-looking Uzbek dataset across all of them (varied statuses,
varied timestamps). Run with:

    python manage.py seed_test_data

This is a destructive, irreversible operation on purpose — it exists for
resetting a dev/staging database to a clean demo state, never run it
against a database you care about.
"""

import itertools
import random
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from management.models import (
    AutodromeAccessGrant,
    Agent,
    Branch,
    Car,
    CarAssignmentHistory,
    CarWash,
    Category,
    DrivingLessons,
    Enrollment,
    Group,
    Holidays,
    LearningPlace,
    Notification,
    Payment,
    StudentCertificate,
    TeacherReview,
    User,
)

NOW = timezone.now()

# ---------------------------------------------------------------------------
# Uzbek name / word pools
# ---------------------------------------------------------------------------

MALE_FIRST_NAMES = [
    "Aziz", "Bekzod", "Dilshod", "Farrux", "Jasur", "Kamron", "Laziz", "Muzaffar",
    "Nodir", "Otabek", "Rustam", "Sardor", "Temur", "Ulug'bek", "Xurshid", "Yusuf",
    "Zafar", "Sherzod", "Anvar", "Bahodir", "Davron", "Elyor", "Farhod", "G'ayrat",
    "Ilhom", "Jahongir", "Komil", "Murod", "Nurbek", "Sanjar", "Shuhrat", "Akmal",
]
FEMALE_FIRST_NAMES = [
    "Malika", "Nilufar", "Zarina", "Gulnora", "Shahnoza", "Feruza", "Madina", "Dilnoza",
    "Sevara", "Kamola", "Nargiza", "Umida", "Zulfiya", "Yulduz", "Nasiba", "Lola",
    "Mohira", "Sabina", "Rayhona", "Aziza", "Gulbahor", "Dildora", "Shaxlo", "Xurshida",
    "Munisa", "Sitora", "Iroda", "Charos",
]
SURNAME_PAIRS = [
    ("Abdullayev", "Abdullayeva"), ("Yusupov", "Yusupova"), ("Karimov", "Karimova"),
    ("Rahimov", "Rahimova"), ("Ergashev", "Ergasheva"), ("Nazarov", "Nazarova"),
    ("Xudayberganov", "Xudayberganova"), ("Islomov", "Islomova"), ("Turg'unov", "Turg'unova"),
    ("Sodiqov", "Sodiqova"), ("Mirzayev", "Mirzayeva"), ("Yoqubov", "Yoqubova"),
    ("Umarov", "Umarova"), ("Saidov", "Saidova"), ("Ne'matov", "Ne'matova"),
    ("Xolmatov", "Xolmatova"), ("Rustamov", "Rustamova"), ("G'aniyev", "G'aniyeva"),
    ("Toshpo'latov", "Toshpo'latova"), ("Qodirov", "Qodirova"), ("Sultonov", "Sultonova"),
    ("Ismoilov", "Ismoilova"), ("Aliyev", "Aliyeva"), ("Xasanov", "Xasanova"),
    ("Tursunov", "Tursunova"), ("Nortojiyev", "Nortojiyeva"),
]

BRANCH_NAMES = ["ARSS", "AutoRoad School"]

CATEGORY_DATA = [
    ("A", 2_500_000, 30), ("A1", 2_000_000, 25), ("B", 4_500_000, 68),
    ("B1", 4_000_000, 60), ("BC", 6_500_000, 90), ("C", 5_500_000, 75),
    ("C1", 5_000_000, 70), ("D", 7_000_000, 95), ("D1", 6_000_000, 85),
    ("T", 8_000_000, 100),
]

CAR_MODELS = [
    "Chevrolet Cobalt", "Chevrolet Nexia 3", "Chevrolet Malibu 2", "Chevrolet Spark",
    "Chevrolet Damas", "Chevrolet Lacetti", "Chevrolet Gentra", "Chevrolet Onix",
    "Chevrolet Tracker", "Daewoo Matiz",
]

LEARNING_PLACE_SUFFIXES = ["o'quv markazi", "auditoriyasi", "o'quv sinfi", "nazariya markazi"]

STUDENT_NOTES_POOL = [
    "Yaxshi o'quvchi, faol qatnashadi.", "Vaqtida keladi, intizomli.",
    "Qo'shimcha mashg'ulot kerak.", "Amaliy darslarda yaxshi natija ko'rsatmoqda.",
    "Nazariy bilimlari yaxshi.", "Ota-onasi bilan bog'lanish kerak.", "", "", "",
]

WEEKDAY_PRESETS = [[0, 2, 4], [1, 3, 5], [0, 1, 2, 3, 4, 5]]

# ---------------------------------------------------------------------------
# Unique-value generators
# ---------------------------------------------------------------------------

_phone_seq = itertools.count(1_000_000)
_OPERATOR_CODES = ["90", "91", "93", "94", "95", "97", "98", "99", "33", "88", "77"]


def next_phone():
    op = random.choice(_OPERATOR_CODES)
    n = next(_phone_seq)
    return f"998{op}{n:07d}"


_jshshr_seq = itertools.count(30_000_000_000_000)


def next_jshshr():
    return next(_jshshr_seq)


_passport_seq = itertools.count(1_000_000)
_PASSPORT_SERIES = ["AA", "AB", "AC", "AD", "FA", "FB"]


def next_passport():
    serie = random.choice(_PASSPORT_SERIES)
    number = next(_passport_seq) % 10_000_000
    return serie, number


def random_plate():
    region = random.choice(["01", "10", "20", "30", "50", "70", "75", "80", "85", "90"])
    letter = random.choice("ABCDEHKMOPT")
    digits = random.randint(100, 999)
    suffix = "".join(random.choices("ABCDEHKMOPT", k=2))
    return f"{region} {letter} {digits} {suffix}"


def random_person(gender=None):
    gender = gender or random.choice(["M", "F"])
    first = random.choice(MALE_FIRST_NAMES if gender == "M" else FEMALE_FIRST_NAMES)
    pair = random.choice(SURNAME_PAIRS)
    last = pair[0] if gender == "M" else pair[1]
    return gender, first, last


def rand_dt(days_back_max, days_back_min=0):
    """A tz-aware datetime somewhere between `days_back_min` and
    `days_back_max` days before now, at a random time of day."""
    delta_days = random.uniform(days_back_min, days_back_max)
    return NOW - timedelta(days=delta_days)


def rand_date(days_back_max, days_back_min=0):
    return rand_dt(days_back_max, days_back_min).date()


def backdate(instance, created_at=None, updated_at=None):
    """created_at is a plain field (settable on save()); updated_at has
    auto_now=True so Django overwrites it on every save() — only a bare
    QuerySet.update() (which skips pre_save/auto_now handling) can set a
    custom value for it."""
    fields = {}
    if created_at is not None:
        fields["created_at"] = created_at
    if updated_at is not None:
        fields["updated_at"] = updated_at
    if fields:
        type(instance).objects.filter(pk=instance.pk).update(**fields)


class Command(BaseCommand):
    help = "Wipes all non-superuser data and seeds realistic Uzbek test data."

    def handle(self, *args, **options):
        with transaction.atomic():
            self.wipe()
            self.branches = self.seed_branches()
            self.categories = self.seed_categories()
            self.seed_holidays()
            self.learning_places = self.seed_learning_places()
            self.admins, self.coordinators, self.instructors, self.mechanics, self.students = self.seed_users()
            self.agents = self.seed_agents()
            self.groups = self.seed_groups()
            self.enrollments = self.seed_enrollments()
            self.seed_payments()
            self.cars = self.seed_cars()
            self.seed_car_history()
            self.seed_driving_lessons()
            self.seed_notifications()
            self.seed_teacher_reviews()
            self.seed_student_certificates()
        self.stdout.write(self.style.SUCCESS("Done — database wiped and reseeded."))

    # ------------------------------------------------------------------
    # Wipe (dependency order: leaves first, PROTECTed parents last)
    # ------------------------------------------------------------------
    def wipe(self):
        self.stdout.write("Wiping existing data (except superusers)...")
        StudentCertificate.objects.all().delete()
        TeacherReview.objects.all().delete()
        Notification.objects.all().delete()
        AutodromeAccessGrant.objects.all().delete()
        DrivingLessons.objects.all().delete()
        CarWash.objects.all().delete()
        CarAssignmentHistory.objects.all().delete()
        Payment.objects.all().delete()
        Enrollment.objects.all().delete()
        Car.objects.all().delete()
        Group.objects.all().delete()
        Agent.objects.all().delete()
        LearningPlace.objects.all().delete()
        Category.objects.all().delete()
        Holidays.objects.all().delete()
        Branch.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    # ------------------------------------------------------------------
    def seed_branches(self):
        self.stdout.write("Seeding branches...")
        branches = []
        for name in BRANCH_NAMES:
            b = Branch.objects.create(name=name, created_at=rand_dt(300, 250))
            backdate(b, updated_at=rand_dt(60, 0))
            branches.append(b)
        return branches

    def seed_categories(self):
        self.stdout.write("Seeding categories...")
        categories = []
        for name, price, duration in CATEGORY_DATA:
            c = Category.objects.create(
                branch=random.choice(self.branches),
                name=name,
                price=price,
                duration=duration,
                created_at=rand_dt(280, 240),
            )
            backdate(c, updated_at=rand_dt(60, 0))
            categories.append(c)
        return categories

    def seed_holidays(self):
        self.stdout.write("Seeding holidays...")
        year = date.today().year
        specs = [
            ("Yangi yil bayrami", (1, 1), (1, 2)),
            ("Xotira va qadrlash kuni", (1, 14), (1, 14)),
            ("Xalqaro xotin-qizlar kuni", (3, 8), (3, 8)),
            ("Navro'z bayrami", (3, 21), (3, 22)),
            ("Xotira va qadrlash kuni (9-may)", (5, 9), (5, 9)),
            ("Mustaqillik kuni", (9, 1), (9, 2)),
            ("O'qituvchi va murabbiylar kuni", (10, 1), (10, 1)),
            ("Konstitutsiya kuni", (12, 8), (12, 8)),
        ]
        count = 0
        for y in (year - 1, year):
            for name, start_md, end_md in specs:
                h = Holidays.objects.create(
                    holiday_name=name,
                    start_date=date(y, *start_md),
                    end_date=date(y, *end_md),
                    note="Rasmiy dam olish kuni",
                    created_at=rand_dt(300, 200),
                )
                backdate(h, updated_at=rand_dt(60, 0))
                count += 1
                if count >= 12:
                    return

    def seed_learning_places(self):
        self.stdout.write("Seeding learning places...")
        places = []
        for _ in range(18):
            branch = random.choice(self.branches)
            name = f"{branch.name.split()[0]} {random.choice(LEARNING_PLACE_SUFFIXES)}"
            lp = LearningPlace.objects.create(
                branch=branch, place_name=name, created_at=rand_dt(280, 230),
            )
            backdate(lp, updated_at=rand_dt(60, 0))
            places.append(lp)
        return places

    # ------------------------------------------------------------------
    def _make_staff(self, role, count, license_fields=False):
        made = []
        for _ in range(count):
            gender, first, last = random_person()
            phone = next_phone()
            jshshr = next_jshshr()
            serie, number = next_passport()
            kwargs = dict(
                role=role,
                phone=phone,
                phone2=next_phone() if random.random() < 0.3 else None,
                first_name=first,
                last_name=last,
                full_name=f"{first} {last}",
                jshshr=jshshr,
                passport_serie=serie,
                passport_number=number,
                birth_date=rand_date(365 * 40, 365 * 19),
                branch=random.choice(self.branches),
                notes=random.choice(STUDENT_NOTES_POOL),
                date_joined=rand_dt(365, 30),
            )
            if license_fields and role == User.Role.INSTRUCTOR:
                kwargs["license_series"] = random.choice(_PASSPORT_SERIES)
                kwargs["license_number"] = f"{random.randint(0, 999999):06d}"
            u = User(**kwargs)
            u.save()
            backdate(u, updated_at=rand_dt(60, 0))
            made.append(u)
        return made

    def seed_users(self):
        self.stdout.write("Seeding staff and student users...")
        admins = self._make_staff(User.Role.ADMIN, 12)
        coordinators = self._make_staff(User.Role.COORDINATOR, 30)
        instructors = self._make_staff(User.Role.INSTRUCTOR, 30, license_fields=True)
        mechanics = self._make_staff(User.Role.MECHANIC, 12)
        students = self._make_staff(User.Role.STUDENT, 90)
        # A handful of students already have their exam-completion certificate on file.
        for s in random.sample(students, 20):
            s.certificate_series = random.choice(_PASSPORT_SERIES)
            s.certificate_number = f"{random.randint(0, 999999999):09d}"
            added = rand_dt(200, 5)
            s.certificate_added_date = added
            s.save(update_fields=["certificate_series", "certificate_number", "certificate_added_date"])
        return admins, coordinators, instructors, mechanics, students

    def seed_agents(self):
        self.stdout.write("Seeding agents...")
        agents = []
        # A third of the agents are teachers/instructors moonlighting as
        # referral agents (Agent.user), the rest are standalone referrers.
        teacher_agents_source = self.coordinators[:5] + self.instructors[:5]
        random.shuffle(teacher_agents_source)
        for i in range(30):
            branch = random.choice(self.branches)
            if i < 10 and teacher_agents_source:
                user = teacher_agents_source.pop()
                a = Agent.objects.create(
                    branch=branch,
                    full_name=user.full_name,
                    phone=user.phone,
                    user=user,
                    created_at=rand_dt(280, 20),
                )
            else:
                gender, first, last = random_person()
                a = Agent.objects.create(
                    branch=branch,
                    full_name=f"{first} {last}",
                    phone=next_phone(),
                    phone2=next_phone() if random.random() < 0.2 else None,
                    created_at=rand_dt(280, 20),
                )
            backdate(a, updated_at=rand_dt(60, 0))
            agents.append(a)
        return agents

    def seed_groups(self):
        self.stdout.write("Seeding groups...")
        groups = []
        for i in range(24):
            category = random.choice(self.categories)
            working_days = category.duration
            weekdays = random.choice(WEEKDAY_PRESETS)
            # Spread starts across the last ~10 months so some groups are
            # clearly finished, some are ongoing, a few are brand new.
            started_at = rand_date(300, 5)
            span_days = int(working_days * 1.6)
            ends_at = started_at + timedelta(days=span_days)
            duration_months = round(span_days / 30.0, 1)

            if ends_at < date.today():
                status = random.choices(
                    [Group.Status.FINISHED, Group.Status.CANCELED], weights=[85, 15]
                )[0]
            else:
                status = random.choices(
                    [Group.Status.STARTED, Group.Status.CANCELED], weights=[90, 10]
                )[0]

            g = Group.objects.create(
                branch=category.branch,
                category=category,
                name=f"{category.name}-{100 + i}",
                started_at=started_at,
                ends_at=ends_at,
                working_days=working_days,
                selected_weekdays=weekdays,
                duration=duration_months,
                status=status,
                created_at=timezone.make_aware(datetime.combine(started_at, datetime.min.time())),
            )
            backdate(g, updated_at=rand_dt(60, 0))
            groups.append(g)
        return groups

    def seed_enrollments(self):
        self.stdout.write("Seeding enrollments...")
        enrollments = []
        status_choices = [
            Enrollment.Status.NEW, Enrollment.Status.ENROLLED,
            Enrollment.Status.FINISHED, Enrollment.Status.CANCELED,
        ]
        for student in self.students:
            group = random.choice(self.groups) if random.random() < 0.85 else None
            category = group.category if group else random.choice(self.categories)
            if group:
                status = {
                    Group.Status.FINISHED: Enrollment.Status.FINISHED,
                    Group.Status.CANCELED: Enrollment.Status.CANCELED,
                    Group.Status.STARTED: random.choice(
                        [Enrollment.Status.ENROLLED, Enrollment.Status.NEW]
                    ),
                }[group.status]
            else:
                status = Enrollment.Status.NEW
            enrolled_free = random.random() < 0.05
            e = Enrollment.objects.create(
                branch=category.branch,
                student=student,
                category=category,
                group=group,
                instructor=random.choice(self.instructors) if random.random() < 0.85 else None,
                coordinator=random.choice(self.coordinators) if random.random() < 0.85 else None,
                agent=random.choice(self.agents) if random.random() < 0.4 else None,
                learning_place=random.choice(self.learning_places) if random.random() < 0.7 else None,
                learning_time=random.choice(["09:00", "11:00", "14:00", "16:00", "18:00"]),
                learning_days=random.choice(WEEKDAY_PRESETS),
                status=status,
                enrolled_free=enrolled_free,
                enrolled_amount=0 if enrolled_free else category.price,
                can_view_payments=random.random() < 0.9,
                created_at=rand_dt(280, 2),
            )
            backdate(e, updated_at=rand_dt(60, 0))
            enrollments.append(e)

        # A handful of students re-enrolled after finishing/cancelling their
        # first course — exercises the "current enrollment only" payment
        # scoping (a prior enrollment may have been fully refunded).
        for student in random.sample(self.students, 10):
            category = random.choice(self.categories)
            group = random.choice([g for g in self.groups if g.status == Group.Status.STARTED] or self.groups)
            e = Enrollment.objects.create(
                branch=category.branch,
                student=student,
                category=category,
                group=group,
                instructor=random.choice(self.instructors),
                coordinator=random.choice(self.coordinators),
                learning_time=random.choice(["09:00", "11:00", "14:00", "16:00", "18:00"]),
                learning_days=random.choice(WEEKDAY_PRESETS),
                status=Enrollment.Status.ENROLLED,
                enrolled_amount=category.price,
                created_at=rand_dt(30, 1),
            )
            backdate(e, updated_at=rand_dt(20, 0))
            enrollments.append(e)
        return enrollments

    def seed_payments(self):
        self.stdout.write("Seeding payments...")
        cashiers = self.admins
        superusers = list(User.objects.filter(is_superuser=True)) or cashiers

        for e in self.enrollments:
            if e.enrolled_free:
                continue
            n_payments = random.randint(0, 4)
            paid_so_far = 0
            for _ in range(n_payments):
                remaining = max(0, e.enrolled_amount - paid_so_far)
                if remaining <= 0:
                    break
                amount = min(remaining, random.choice([300_000, 500_000, 750_000, 1_000_000, 1_500_000]))
                paid_so_far += amount
                method = random.choices(
                    ["cash", "card", "qr_code", "click", "transfer"], weights=[45, 20, 10, 20, 5]
                )[0]
                p = Payment.objects.create(
                    branch=e.branch,
                    user=random.choice(cashiers),
                    created_by=random.choice(cashiers),
                    enrollment=e,
                    amount=amount,
                    status=Payment.Status.ACCEPTED,
                    method=method,
                    notes=random.choice(["", "", "Naqd to'lov", "Oylik to'lov"]),
                    created_at=rand_dt(270, 1),
                )
                backdate(p, updated_at=rand_dt(60, 0))

            # Occasionally a payment gets returned (refund/cancellation).
            if paid_so_far > 0 and random.random() < 0.12:
                refund = random.choice([300_000, 500_000, paid_so_far])
                p = Payment.objects.create(
                    branch=e.branch,
                    user=random.choice(superusers),
                    created_by=random.choice(superusers),
                    enrollment=e,
                    amount=min(refund, paid_so_far),
                    status=Payment.Status.RETURNED,
                    method=random.choice(["cash", "card", "click"]),
                    notes="Mijoz talabiga ko'ra qaytarildi",
                    created_at=rand_dt(200, 1),
                )
                backdate(p, updated_at=rand_dt(60, 0))

            # Some payments go through the bank instead of being handled by a cashier.
            if random.random() < 0.15:
                p = Payment.objects.create(
                    branch=e.branch,
                    user=random.choice(cashiers),
                    created_by=random.choice(cashiers),
                    enrollment=e,
                    amount=random.choice([500_000, 1_000_000, 2_000_000]),
                    status=Payment.Status.BANK,
                    method="transfer",
                    notes="Bank orqali o'tkazma",
                    created_at=rand_dt(200, 1),
                )
                backdate(p, updated_at=rand_dt(60, 0))

            # Agent referral bonus payout, when this enrollment came through an agent.
            if e.agent_id and random.random() < 0.5:
                p = Payment.objects.create(
                    branch=e.branch,
                    user=random.choice(cashiers),
                    created_by=random.choice(cashiers),
                    enrollment=e,
                    agent=e.agent,
                    amount=random.choice([100_000, 150_000, 200_000, 300_000]),
                    status=Payment.Status.BONUS,
                    method=random.choice(["cash", "card", "click"]),
                    notes=f"Agentlik bonusi: {e.student.full_name}",
                    created_at=rand_dt(180, 1),
                )
                backdate(p, updated_at=rand_dt(60, 0))

        # Instructor/teacher salary-style "paid" payments (not tied to a
        # specific student enrollment).
        for teacher in self.instructors + self.coordinators:
            for _ in range(random.randint(0, 3)):
                p = Payment.objects.create(
                    branch=teacher.branch,
                    user=teacher,
                    created_by=random.choice(cashiers),
                    amount=random.choice([1_000_000, 1_500_000, 2_000_000, 2_500_000]),
                    status=Payment.Status.PAID,
                    method=random.choice(["cash", "card", "transfer"]),
                    notes="Oylik maosh to'lovi",
                    created_at=rand_dt(200, 1),
                )
                backdate(p, updated_at=rand_dt(60, 0))

    # ------------------------------------------------------------------
    def seed_cars(self):
        self.stdout.write("Seeding cars...")
        cars = []
        statuses = [Car.Status.AVAILABLE, Car.Status.REPAIRING, Car.Status.NOT_AVAILABLE]
        for _ in range(30):
            mileage = random.randint(5_000, 180_000)
            c = Car.objects.create(
                car_name=f"{random.choice(CAR_MODELS)} {random_plate()}",
                manufact_year=random.randint(2014, 2024),
                policy_date=date.today() + timedelta(days=random.randint(-30, 300)),
                tech_inspection_date=date.today() + timedelta(days=random.randint(-30, 300)),
                status=random.choices(statuses, weights=[75, 15, 10])[0],
                instructor=random.choice(self.instructors) if random.random() < 0.8 else None,
                mileage=mileage,
                oil_change_date=rand_date(200, 1),
                oil_change_mileage=max(0, mileage - random.randint(500, 4000)),
                oil_change_interval_km=random.choice([5000, 7000, 10000]),
                last_washed_at=rand_dt(30, 0),
                created_at=rand_dt(300, 100),
            )
            backdate(c, updated_at=rand_dt(60, 0))
            cars.append(c)
        return cars

    def seed_car_history(self):
        self.stdout.write("Seeding car assignment/wash history...")
        for car in self.cars:
            for _ in range(random.randint(0, 2)):
                instructor = random.choice(self.instructors)
                assigned_at = rand_dt(280, 30)
                closed = random.random() < 0.6
                h = CarAssignmentHistory.objects.create(
                    car=car,
                    instructor=instructor,
                    assigned_at=assigned_at,
                    unassigned_at=assigned_at + timedelta(days=random.randint(5, 60)) if closed else None,
                    mileage_at_unassignment=random.randint(5_000, 150_000) if closed else None,
                    created_at=assigned_at,
                )
                backdate(h, updated_at=rand_dt(60, 0))
            for _ in range(random.randint(0, 3)):
                washed_at = rand_dt(120, 0)
                w = CarWash.objects.create(
                    car=car,
                    instructor=car.instructor or random.choice(self.instructors),
                    washed_at=washed_at,
                    created_at=washed_at,
                )
                backdate(w, updated_at=rand_dt(60, 0))

    def seed_driving_lessons(self):
        self.stdout.write("Seeding driving lessons and avtodrom history...")
        active_enrollments = [e for e in self.enrollments if e.instructor_id]
        for e in random.sample(active_enrollments, min(120, len(active_enrollments))):
            for _ in range(random.randint(1, 4)):
                lesson_dt = rand_dt(180, 1)
                l = DrivingLessons.objects.create(
                    branch=e.branch,
                    lesson_type=DrivingLessons.LessonType.DRIVING,
                    student=e.student,
                    instructor=e.instructor,
                    car=random.choice(self.cars) if random.random() < 0.8 else None,
                    lesson_date=lesson_dt,
                    notes=random.choice(["", "", "Yaxshi bajardi", "Parallel parkovka mashq qilindi"]),
                    created_at=lesson_dt,
                )
                backdate(l, updated_at=rand_dt(60, 0))

        # Avtodrom sessions, capped at 6 hours per student — matches the
        # AUTODROME_MAX_HOURS business rule enforced in the API serializer.
        autodrome_candidates = random.sample(active_enrollments, min(40, len(active_enrollments)))
        for e in autodrome_candidates:
            hours_used = 0
            attempts = random.randint(1, 3)
            for _ in range(attempts):
                remaining = 6 - hours_used
                if remaining <= 0:
                    break
                hours = random.randint(1, remaining)
                hours_used += hours
                lesson_dt = rand_dt(150, 1)
                l = DrivingLessons.objects.create(
                    branch=e.branch,
                    lesson_type=DrivingLessons.LessonType.AUTODROME,
                    student=e.student,
                    instructor=e.instructor,
                    hours=hours,
                    lesson_date=lesson_dt,
                    notes="",
                    created_at=lesson_dt,
                )
                backdate(l, updated_at=rand_dt(60, 0))

        # A few students who used up their 6 hours get an extra-visit grant.
        maxed_out_students = []
        for e in autodrome_candidates:
            total = DrivingLessons.objects.filter(
                student=e.student, lesson_type=DrivingLessons.LessonType.AUTODROME
            ).aggregate(total=Sum("hours"))["total"] or 0
            if total >= 6:
                maxed_out_students.append(e.student)
        for student in maxed_out_students[:8]:
            start = date.today() - timedelta(days=random.randint(0, 5))
            grant = AutodromeAccessGrant.objects.create(
                student=student,
                granted_by=random.choice(self.admins),
                branch=student.branch,
                visits=random.choice([3, 6]),
                start_date=start,
                end_date=start + timedelta(days=7),
                created_at=rand_dt(5, 0),
            )
            backdate(grant, updated_at=rand_dt(3, 0))

    def seed_notifications(self):
        self.stdout.write("Seeding notifications...")
        statuses = [
            Notification.Status.DRIVING_LESSON, Notification.Status.CERTIFICATE_UPLOAD,
            Notification.Status.PAYMENT, Notification.Status.AGENT_PAYMENT, Notification.Status.REVIEW,
        ]
        titles = {
            Notification.Status.DRIVING_LESSON: "Yangi amaliy dars tasdiqlandi",
            Notification.Status.CERTIFICATE_UPLOAD: "Yangi sertifikat yuklandi",
            Notification.Status.PAYMENT: "Yangi to'lov qabul qilindi",
            Notification.Status.AGENT_PAYMENT: "Agentga bonus to'landi",
            Notification.Status.REVIEW: "Yangi sharh qoldirildi",
        }
        for _ in range(40):
            status = random.choice(statuses)
            student = random.choice(self.students)
            dt = rand_dt(150, 0)
            n = Notification.objects.create(
                branch=random.choice(self.branches) if random.random() < 0.5 else None,
                user=random.choice(self.admins) if random.random() < 0.5 else None,
                title=titles[status],
                date=dt,
                note=f"O'quvchi: {student.full_name}",
                is_read=random.random() < 0.5,
                status=status,
                target_id=student.id,
                created_at=dt,
            )
            backdate(n, updated_at=dt)

    def seed_teacher_reviews(self):
        self.stdout.write("Seeding teacher reviews...")
        comments = [
            "Juda tushunarli tushuntiradi.", "Sabr-toqatli va yordamchi.",
            "Darslar qiziqarli o'tadi.", "Vaqtida keladi, professional.",
            "Tavsiya qilaman!", "",
        ]
        teachers = self.coordinators + self.instructors
        for _ in range(30):
            student = random.choice(self.students)
            teacher = random.choice(teachers)
            dt = rand_dt(180, 1)
            r = TeacherReview.objects.create(
                branch=teacher.branch,
                student=student,
                teacher=teacher,
                rating=random.choices([5, 4, 3, 2], weights=[55, 25, 12, 8])[0],
                comment=random.choice(comments),
                created_at=dt,
            )
            backdate(r, updated_at=dt)

    def seed_student_certificates(self):
        self.stdout.write("Seeding student exam certificates...")
        candidates = random.sample(self.students, min(30, len(self.students)))
        for student in candidates:
            coordinator = random.choice(self.coordinators)
            uploaded_at = rand_dt(150, 3)
            cert = StudentCertificate.objects.create(
                branch=coordinator.branch,
                student=student,
                coordinator=coordinator,
                image="certificates/certificate_default_9MQvwme.jpg",
                notes="",
                created_at=uploaded_at,
            )
            backdate(cert, updated_at=uploaded_at)

            if random.random() < 0.5:
                paid_at = uploaded_at + timedelta(days=random.randint(1, 10))
                payment = Payment.objects.create(
                    user=coordinator,
                    enrollment=Enrollment.objects.filter(student=student).first(),
                    amount=random.choice([100_000, 150_000, 200_000]),
                    status=Payment.Status.BONUS_TEACHER,
                    method=random.choice(["cash", "card", "click"]),
                    branch=cert.branch,
                    notes=f"Sertifikat bonusi: {student.full_name}",
                    created_at=paid_at,
                )
                backdate(payment, updated_at=paid_at)
                cert.bonus_payment = payment
                cert.save(update_fields=["bonus_payment"])
                backdate(cert, updated_at=paid_at)

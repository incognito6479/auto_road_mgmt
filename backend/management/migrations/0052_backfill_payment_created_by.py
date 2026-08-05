from django.db import migrations, models


# For these statuses "user" already means the cashier/admin who processed the
# payment (the same person "created_by" now tracks explicitly), so backfilling
# from it is accurate. For "paid"/"bonus_teacher", "user" is the teacher or
# instructor being paid — the actual recorder was never captured, so those
# rows are left with created_by = NULL rather than backfilled with a guess.
BACKFILLABLE_STATUSES = ["accepted", "returned", "bank", "bonus"]


def backfill_created_by(apps, schema_editor):
    Payment = apps.get_model("management", "Payment")
    Payment.objects.filter(status__in=BACKFILLABLE_STATUSES, created_by__isnull=True).update(
        created_by=models.F("user")
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0051_payment_created_by_alter_payment_user"),
    ]

    operations = [
        migrations.RunPython(backfill_created_by, reverse_code=noop),
    ]

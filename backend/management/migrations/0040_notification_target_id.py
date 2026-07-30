# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0039_teacher_review_and_student_certificate'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='target_id',
            field=models.PositiveIntegerField(blank=True, help_text="Bog'liq obyekt IDsi — status'ga qarab qayerga ishora qilishini frontend hal qiladi (driving_lesson/certificate_upload -> o'quvchi ID, review -> o'qituvchi/instruktor ID).", null=True),
        ),
    ]

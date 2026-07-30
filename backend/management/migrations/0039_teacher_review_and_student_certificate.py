# Generated manually

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('management', '0038_car_oil_change_interval_km'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('accepted', "Qabul qilingan"), ('returned', "Qaytarilgan"), ('paid', "To'langan"), ('bonus', 'Bonus'), ('bank', 'Bank'), ('bonus_teacher', "O'qituvchi bonusi")], default='accepted', max_length=20),
        ),
        migrations.AlterField(
            model_name='notification',
            name='status',
            field=models.CharField(choices=[('driving_lesson', 'Amaliy Haydash Darsi'), ('certificate_upload', 'Sertifikat Yuklash'), ('payment', "To'lov"), ('agent_payment', "Agent To'lovi"), ('review', 'Sharh')], default='driving_lesson', max_length=30),
        ),
        migrations.CreateModel(
            name='TeacherReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('notes', models.TextField(blank=True, help_text="Qo'shimcha eslatmalar", null=True)),
                ('rating', models.PositiveSmallIntegerField(default=5, help_text='Baho (1 dan 5 gacha)')),
                ('comment', models.TextField(blank=True, help_text='Sharh matni', null=True)),
                ('branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teacher_reviews', to='management.branch')),
                ('student', models.ForeignKey(help_text="Sharh qoldirgan o'quvchi", limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.CASCADE, related_name='reviews_given', to=settings.AUTH_USER_MODEL)),
                ('teacher', models.ForeignKey(help_text="Sharh qoldirilgan o'qituvchi yoki instruktor", limit_choices_to={'role__in': ['instructor', 'coordinator']}, on_delete=django.db.models.deletion.CASCADE, related_name='reviews_received', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "O'qituvchi sharhi",
                'verbose_name_plural': "O'qituvchi sharhlari",
                'db_table': 'teacher_review',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StudentCertificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('notes', models.TextField(blank=True, help_text="Qo'shimcha eslatmalar", null=True)),
                ('image', models.FileField(help_text='Sertifikat rasmi', upload_to='certificates/')),
                ('branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_certificates', to='management.branch')),
                ('bonus_payment', models.ForeignKey(blank=True, help_text="Ushbu sertifikat uchun instruktorga to'langan bonus to'lovi (agar to'langan bo'lsa)", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='certificate', to='management.payment')),
                ('instructor', models.ForeignKey(blank=True, help_text='Sertifikatni yuklagan instruktor', limit_choices_to={'role': 'instructor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_certificates', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(help_text="Sertifikat tegishli bo'lgan o'quvchi", limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.CASCADE, related_name='certificates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "O'quvchi sertifikati",
                'verbose_name_plural': "O'quvchi sertifikatlari",
                'db_table': 'student_certificate',
                'ordering': ['-created_at'],
            },
        ),
    ]

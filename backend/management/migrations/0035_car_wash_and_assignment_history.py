# Generated manually

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('management', '0034_alter_user_phone2'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='mileage',
            field=models.PositiveIntegerField(blank=True, help_text='Probeg (km)', null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='oil_change_date',
            field=models.DateField(blank=True, help_text="Moy so'nggi almashtirilgan sana", null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='last_washed_at',
            field=models.DateTimeField(blank=True, help_text="Oxirgi marta yuvilgan sana va vaqt (avtomatik to'ldiriladi)", null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='instructor',
            field=models.ForeignKey(blank=True, help_text='Ushbu avtomobilga biriktirilgan instruktor', limit_choices_to={'role': 'instructor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_cars', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CarAssignmentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('notes', models.TextField(blank=True, help_text="Qo'shimcha eslatmalar", null=True)),
                ('assigned_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('unassigned_at', models.DateTimeField(blank=True, null=True)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_history', to='management.car')),
                ('instructor', models.ForeignKey(blank=True, limit_choices_to={'role': 'instructor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='car_assignment_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Avtomobil biriktirish tarixi',
                'verbose_name_plural': 'Avtomobil biriktirish tarixi',
                'db_table': 'car_assignment_history',
                'ordering': ['-assigned_at'],
            },
        ),
        migrations.CreateModel(
            name='CarWash',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('notes', models.TextField(blank=True, help_text="Qo'shimcha eslatmalar", null=True)),
                ('washed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wash_history', to='management.car')),
                ('instructor', models.ForeignKey(blank=True, limit_choices_to={'role': 'instructor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='car_washes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Avtomobil yuvish tarixi',
                'verbose_name_plural': 'Avtomobil yuvish tarixi',
                'db_table': 'car_wash',
                'ordering': ['-washed_at'],
            },
        ),
    ]

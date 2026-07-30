# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0037_car_oil_change_mileage'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='oil_change_interval_km',
            field=models.PositiveIntegerField(default=5000, help_text="Moy almashtirish oralig'i (km). Necha km da moy almashtirilishi kerakligini belgilaydi (standart: 5000 km)."),
        ),
    ]

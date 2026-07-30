# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0036_group_ends_at_selected_weekdays'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='oil_change_mileage',
            field=models.PositiveIntegerField(blank=True, help_text="Moy so'nggi almashtirilgandagi probeg (km). Joriy probeg bilan solishtirib, keyingi almashtirishgacha necha km qolganini hisoblash uchun ishlatiladi.", null=True),
        ),
    ]

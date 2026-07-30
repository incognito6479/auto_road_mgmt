# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0033_user_pass_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone2',
            field=models.CharField(blank=True, help_text="Qo'shimcha telefon raqami, xohlasa qarindoshi nomi bilan (namuna: +998 90 900 90 90 amakisi)", max_length=100, null=True),
        ),
    ]

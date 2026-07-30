# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0035_car_wash_and_assignment_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='ends_at',
            field=models.DateField(blank=True, help_text="Tugash sanasi (avtomatik hisoblanadi: ish kunlari + bayramlar + dars bo'lmagan kunlar)", null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='selected_weekdays',
            field=models.JSONField(blank=True, default=list, help_text='Dars kunlari, Dushanba-Shanba: 0=Dushanba, 1=Seshanba, 2=Chorshanba, 3=Payshanba, 4=Juma, 5=Shanba'),
        ),
        migrations.AlterField(
            model_name='group',
            name='working_weekends',
            field=models.CharField(choices=[('everyday', 'Har kuni (Mon-Sat)'), ('mon-wed-fri', "Dushanba - Chorshanba - Juma (Mo-Wed-Fri)"), ('tue-wed-sat', "Seshanba - Payshanba - Shanba (Tue-Thu-Sat)")], default='mon-wed-fri', help_text="Dars kunlari jadvali (eski, selected_weekdays yo'q bo'lsa ishlatiladi)", max_length=20),
        ),
    ]

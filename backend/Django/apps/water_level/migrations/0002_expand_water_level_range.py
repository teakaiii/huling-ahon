from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('water_level', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waterlevelreading',
            name='water_level_cm',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]
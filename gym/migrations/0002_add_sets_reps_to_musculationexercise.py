# Generated manually to add missing sets and reps fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='musculationexercise',
            name='sets',
            field=models.IntegerField(default=0, verbose_name='Series'),
        ),
        migrations.AddField(
            model_name='musculationexercise',
            name='reps',
            field=models.IntegerField(default=0, verbose_name='Repeticiones'),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ia", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ollamamodelconfig",
            name="pull_progress",
            field=models.IntegerField(
                blank=True,
                help_text="0-100 mientras se descarga; None si no hay descarga en curso.",
                null=True,
                verbose_name="Progreso descarga",
            ),
        ),
    ]

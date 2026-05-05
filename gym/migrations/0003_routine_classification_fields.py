from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gym", "0002_session"),
    ]

    operations = [
        migrations.AddField(
            model_name="routine",
            name="intensity_techniques",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Técnicas aplicadas: series clásicas, superseries, drop-sets, circuitos",
                null=True,
                verbose_name="Técnicas de intensidad",
            ),
        ),
        migrations.AddField(
            model_name="routine",
            name="training_focus",
            field=models.CharField(
                blank=True,
                choices=[
                    ("powerlifting", "Powerlifting"),
                    ("halterofilia", "Halterofilia"),
                    ("fuerza_resistencia", "Fuerza-resistencia"),
                    ("bodybuilding", "Bodybuilding"),
                    ("powerbuilding", "Powerbuilding"),
                    ("calistenia", "Calistenia"),
                    ("funcional_hibrido", "Funcional/Híbrido"),
                ],
                help_text="Objetivo principal fisiológico de la rutina",
                max_length=50,
                null=True,
                verbose_name="Enfoque de entrenamiento",
            ),
        ),
        migrations.AddField(
            model_name="routine",
            name="weekly_structure",
            field=models.CharField(
                blank=True,
                choices=[
                    ("full_body", "Full Body"),
                    ("torso_pierna", "Torso/Pierna"),
                    ("push_pull_legs", "Push/Pull/Legs (PPL)"),
                    ("weider", "Weider (dividida)"),
                ],
                help_text="Cómo se divide la rutina en la semana (Full Body, PPL, etc.)",
                max_length=50,
                null=True,
                verbose_name="Estructura temporal",
            ),
        ),
    ]

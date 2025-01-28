# Generated by Django 3.1.3 on 2025-01-26 16:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kyykka", "0023_auto_20250120_1741"),
    ]

    operations = [
        migrations.RenameField(
            model_name="teamsinseason",
            old_name="second_stage_bracket",
            new_name="first_stage_bracket",
        ),
        migrations.AlterField(
            model_name="match",
            name="match_type",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (1, "Runkosarja"),
                    (2, "Finaali"),
                    (3, "Pronssi"),
                    (4, "Välierä"),
                    (5, "Puolivälierä"),
                    (6, "Neljännesvälierä"),
                    (7, "Kahdeksannesvälierä"),
                    (8, "2. Kierros"),
                    (9, "1. Kierros"),
                    (10, "Runkosarjafinaali"),
                    (11, "Jatkosarja"),
                    (20, "Putoamiskarsinta"),
                    (31, "SuperWeekend: Alkulohko"),
                    (32, "SuperWeekend: Finaali"),
                    (33, "SuperWeekend: Pronssi"),
                    (34, "SuperWeekend: Välierä"),
                    (35, "SuperWeekend: Puolivälierä"),
                    (36, "SuperWeekend: Neljännesvälierä"),
                    (37, "SuperWeekend: Kahdeksannesvälierä"),
                ],
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="teamsinseason",
            name="super_weekend_bracket",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="ExtraBracketStagePlacement",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("placement", models.IntegerField(blank=True, null=True)),
                ("stage", models.IntegerField(null=True)),
                (
                    "team_in_season",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="kyykka.teamsinseason",
                    ),
                ),
            ],
            options={
                "ordering": ("team_in_season", "stage", "placement"),
            },
        ),
        migrations.AddConstraint(
            model_name="extrabracketstageplacement",
            constraint=models.UniqueConstraint(
                fields=("team_in_season", "stage"), name="unique_team_stage"
            ),
        ),
    ]

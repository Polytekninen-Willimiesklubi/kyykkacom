# Generated by Django 3.1.3 on 2024-02-18 15:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kyykka", "0019_auto_20231119_1734"),
    ]

    operations = [
        migrations.AddField(
            model_name="season",
            name="playoff_format",
            field=models.IntegerField(
                choices=[
                    (0, "Ei vielä päätetty / Undefined"),
                    (1, "Kiinteä 16 joukkueen Cup"),
                    (2, "Kiinteä 8 joukkueen Cup"),
                    (3, "Kiinteä 4 joukkueen Cup"),
                    (4, "Kiinteä 22 joukkueen Cup"),
                    (5, "1.Kierroksen Seedaus 6 joukkueen Cup"),
                    (6, "1.Kierroksen Seedaus 12 joukkueen Cup"),
                    (7, "SuperWeekend OKA seedaus 15 joukkueen Cup"),
                ],
                default=0,
            ),
        ),
        migrations.AddField(
            model_name="teamsinseason",
            name="bracket_placement",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="teamsinseason",
            name="super_weekend_bracket",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="teamsinseason",
            name="super_weekend_bracket_placement",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="teamsinseason",
            name="super_weekend_playoff_seed",
            field=models.IntegerField(blank=True, null=True),
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
                    (10, "Runkosarjafinaali"),
                    (20, "Jumbofinaali"),
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
        migrations.CreateModel(
            name="SuperWeekend",
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
                (
                    "super_weekend_no_brackets",
                    models.IntegerField(blank=True, default=0, null=True),
                ),
                (
                    "super_weekend_playoff_format",
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (0, "Ei vielä päätetty / Undefined"),
                            (1, "Kiinteä 16 joukkueen Cup"),
                            (2, "Kiinteä 8 joukkueen Cup"),
                            (3, "Kiinteä 4 joukkueen Cup"),
                            (4, "Kiinteä 22 joukkueen Cup"),
                            (5, "1.Kierroksen Seedaus 6 joukkueen Cup"),
                            (6, "1.Kierroksen Seedaus 12 joukkueen Cup"),
                            (7, "SuperWeekend OKA seedaus 15 joukkueen Cup"),
                        ],
                        default=0,
                        null=True,
                    ),
                ),
                (
                    "season",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="kyykka.season"
                    ),
                ),
                (
                    "winner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="kyykka.teamsinseason",
                    ),
                ),
            ],
        ),
    ]

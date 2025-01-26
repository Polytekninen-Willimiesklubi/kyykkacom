from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("kyykka", "0021_auto_20241230_2232"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="news",
            options={"verbose_name_plural": "News"},
        ),
        migrations.AlterModelOptions(
            name="teamsinseason",
            options={"ordering": ("-season", "bracket", "bracket_placement")},
        ),
        migrations.AlterField(
            model_name="throw",
            name="score_first",
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name="throw",
            name="score_fourth",
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name="throw",
            name="score_second",
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name="throw",
            name="score_third",
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name="throw",
            name="throw_round",
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name="throw",
            name="throw_turn",
            field=models.IntegerField(db_index=True),
        ),
    ]

# Generated by Django 2.1.5 on 2019-04-02 18:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0007_auto_20190402_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='away_first_round_score',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='away_second_round_score',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='home_first_round_score',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='home_second_round_score',
            field=models.IntegerField(null=True),
        ),
    ]

# Generated by Django 3.1.3 on 2024-09-06 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kyykka', '0025_seasonstats_gte_six'),
    ]

    operations = [
        migrations.AddField(
            model_name='positionstats',
            name='scaled_points',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='seasonstats',
            name='scaled_points',
            field=models.IntegerField(default=0),
        ),
    ]

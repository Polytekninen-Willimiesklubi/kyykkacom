# Generated by Django 3.1.3 on 2023-11-19 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0016_auto_20231119_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='abbreviation',
            field=models.CharField(max_length=15),
        ),
    ]

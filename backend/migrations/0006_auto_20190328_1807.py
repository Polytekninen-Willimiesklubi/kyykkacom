# Generated by Django 2.1.5 on 2019-03-28 16:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0005_player'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='player_number',
            new_name='number',
        ),
    ]

# Generated by Django 2.1.5 on 2019-03-17 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentSeason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Current Season',
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_time', models.DateTimeField()),
                ('home_first_round_score', models.IntegerField()),
                ('home_second_round_score', models.IntegerField()),
                ('away_first_round_score', models.IntegerField()),
                ('away_second_round_score', models.IntegerField()),
                ('is_validated', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Matches',
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.TextField()),
                ('date', models.DateTimeField()),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PlayersInTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_captain', models.BooleanField(default=False)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=4, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('abbreviation', models.CharField(max_length=10, unique=True)),
                ('players', models.ManyToManyField(through='backend.PlayersInTeam', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Throw',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('throw_round', models.IntegerField()),
                ('throw_turn', models.CharField(max_length=1)),
                ('score', models.CharField(max_length=2)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Match')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Team')),
            ],
        ),
        migrations.AddField(
            model_name='season',
            name='teams',
            field=models.ManyToManyField(blank=True, to='backend.Team'),
        ),
        migrations.AddField(
            model_name='playersinteam',
            name='season',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Season'),
        ),
        migrations.AddField(
            model_name='playersinteam',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Team'),
        ),
        migrations.AddField(
            model_name='match',
            name='away_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_team',
                                    to='backend.Team'),
        ),
        migrations.AddField(
            model_name='match',
            name='home_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_team',
                                    to='backend.Team'),
        ),
        migrations.AddField(
            model_name='match',
            name='season',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend.Season'),
        ),
        migrations.AddField(
            model_name='currentseason',
            name='season',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='backend.Season'),
        ),
        migrations.AlterUniqueTogether(
            name='playersinteam',
            unique_together={('player', 'season')},
        ),
    ]

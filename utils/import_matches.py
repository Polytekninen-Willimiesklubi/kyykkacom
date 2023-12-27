# -*- coding: utf-8 -*-
# Run this through shell - put matches.csv into  root folder

import csv, datetime
from django.db import transaction
from kyykka.models import Team, Match, CurrentSeason, TeamsInSeason

def test_import():
    c = CurrentSeason.objects.first()
    print(f"Current season is set to: {CurrentSeason.objects.first()}")
    print(f'First matches binds are: ')
    with open('./matches.csv') as csvfile:
        i = 0
        readCSV = csv.reader(csvfile, delimiter=',')
        with transaction.atomic():
            for row in readCSV:
                if i == 4: break
                home_team = TeamsInSeason.objects.get(current_abbreviation=row[1], season=c.season)
                away_team = TeamsInSeason.objects.get(current_abbreviation=row[2], season=c.season)
                print(row[1], '->', home_team, f'ID: {home_team.id}, Season: {home_team.season}')
                print(row[2], '->', away_team, f'ID: {away_team.id}, Season: {away_team.season}')

def import_matches():
    """
    Import matches from matches.csv
    """
    with open('./matches.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        current = CurrentSeason.objects.first().season
        with transaction.atomic():
            for row in readCSV:
                date_time_str = row[0].replace("'", "")
                home = row[1]
                away = row[2]
                field = row[3]
                date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                home_team = TeamsInSeason.objects.get(current_abbreviation=home, season=current)
                away_team = TeamsInSeason.objects.get(current_abbreviation=away, season=current)
                field_num = field[-1]
                Match.objects.create(
                    season=current,
                    match_time=date_time_obj,
                    field=field_num,
                    home_team=home_team,
                    away_team=away_team
                )

# -*- coding: utf-8 -*-
# Run this through shell - put matches.csv into  root folder

import csv, datetime
from django.db import transaction
from kyykka.models import Team, Match, CurrentSeason, TeamsInSeason

def test_import():
    c = CurrentSeason.objects.first()
    print(f"Current season is set to: {CurrentSeason.objects.first()}")
    print(f'First matches binds are: ')
    with open('./matches.csv', encoding='utf-8') as csvfile:
        i = 0
        readCSV = csv.reader(csvfile, delimiter=',')
        with transaction.atomic():
            for row in readCSV:
                if i == 4: break
                home_team = TeamsInSeason.objects.filter(current_abbreviation=row[1], season=c.season).first()
                away_team = TeamsInSeason.objects.filter(current_abbreviation=row[2], season=c.season).first()
                print(row[2], row[1])
                print(away_team, home_team)
                print(row[1], '->', home_team, f'ID: {home_team.id}, Season: {home_team.season}')
                print(row[2], '->', away_team, f'ID: {away_team.id}, Season: {away_team.season}')

def import_matches():
    """
    Import matches from matches.csv
    """
    with open('./matches.csv', encoding='utf-8') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        current = CurrentSeason.objects.first()
        with transaction.atomic():
            for row in readCSV:
                date_time_str = row[0].replace("'", "")
                field = row[3]
                date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                home_team = TeamsInSeason.objects.filter(current_abbreviation=row[1], season=current.season).first()
                away_team = TeamsInSeason.objects.filter(current_abbreviation=row[2], season=current.season).first()
                field_num = field[-1]
                Match.objects.create(
                    season=current.season,
                    match_time=date_time_obj,
                    field=field_num,
                    home_team=home_team,
                    away_team=away_team,
                    match_type=1
                )

if __name__ == '__main__':
    test_import()
    user = input('Haluatko jatkaa [Y]/n:')
    if user == 'Y':
        import_matches()
    else:
        print('Aboting....')
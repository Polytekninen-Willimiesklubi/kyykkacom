# -*- coding: utf-8 -*-
# Run this through shell - put matches.csv into  root folder

import csv, datetime
from django.db import transaction
from backend.models import Team, Match, CurrentSeason, TeamsInSeason

def test_import():
    c = CurrentSeason.objects.first()
    print(f"Current season is set to: {CurrentSeason.objects.first()}")
    print(f'First four match binds are: ')
    with open('./matches.csv', encoding='utf-8') as csvfile:
        i = 0
        readCSV = csv.reader(csvfile, delimiter=',')
        all_fine = True
        with transaction.atomic():
            for row in readCSV:
                if i <= 4:
                    home_team = TeamsInSeason.objects.filter(current_abbreviation=row[1], season=c.season).first()
                    away_team = TeamsInSeason.objects.filter(current_abbreviation=row[2], season=c.season).first()
                    print(row[2], row[1])
                    print(away_team, home_team)
                    print(row[1], '->', home_team, f'ID: {home_team.id}, Season: {home_team.season}')
                    print(row[2], '->', away_team, f'ID: {away_team.id}, Season: {away_team.season}')
                else:
                    home_team = TeamsInSeason.objects.filter(current_abbreviation=row[1], season=c.season)
                    away_team = TeamsInSeason.objects.filter(current_abbreviation=row[2], season=c.season)

                    if len(home_team) == 0:
                        print(f"Didn't find a database team for team: {row[1]}")
                        all_fine = False
                    elif len(away_team) == 0:
                        print(f"Didn't find a database team for team: {row[2]}")
                        all_fine = False
                    if len(home_team) > 1:
                        print(f"Found too mcuh database teams for team: {row[1]} ; found teams: {home_team}")
                        all_fine = False
                    elif len(away_team) > 1:
                        print(f"Found too mcuh database teams for team: {row[2]} ; found teams: {away_team}")
                        all_fine = False
                i += 1

    if all_fine:
        print('Näytti hyvältä! Ei löytynyt huonoja team nimiä tms.')
    else:
        print('VIRHEITÄ LÖYTYI! Konsultoi ihmistä joka tietää')


def import_matches():
    """
    Import matches from matches.csv
    """
    user = input('Haluatko testata importtausta ensin [Y]/n:')
    if user == 'Y':
        print()
        test_import()
    print()
    user = input('Haluatko varmasti importata [Y]/n:')
    if user != 'Y':
        return
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

    print()
    print('Importtaus on valmis!')
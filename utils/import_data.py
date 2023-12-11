from django.contrib.auth.models import User
from kyykka.models import Team, Season, PlayersInTeam, CurrentSeason, Match, Throw, Player, TeamsInSeason
import pandas as pd
import datetime as dt
import random
import math
import warnings
warnings.filterwarnings("ignore")


def makeThrow(row, player ,match, season, team, round, turn, eka, toka, kolmas, neljas):
    eka = row[eka] if isinstance(row[eka], str) else None
    toka = row[toka] if isinstance(row[toka], str) else None
    kolmas = row[kolmas] if isinstance(row[kolmas], str) else None
    neljas = row[neljas] if isinstance(row[neljas], str) else None

    if isinstance(row[player], float):
        pelaaja = None
    else:
        pelaaja = row[player].split(" ")

    throw = match.throw_set.filter(throw_turn=turn, throw_round=round, team=team).first()
    throw.match=match
    throw.season = season
    throw.player=User.objects.filter(first_name=" ".join(pelaaja[:-1]), last_name=pelaaja[-1]).first() if pelaaja is not None else None
    throw.team=team
    throw.throw_round=round
    throw.throw_turn=turn
    throw.score_first=eka
    throw.score_second=toka
    throw.score_third=kolmas
    throw.score_fourth=neljas
    throw.save()


def init_gen():
    # User.objects.create_superuser('test','','test')
    for year in range(2000, 2024):
        i = year - 2000
        bra = 2 if year == 2021 or year == 2023 else 1
        if Season.objects.filter(year=year).exists(): continue
        season = Season.objects.create(year=year, no_brackets=bra)
        if year == 2023:
            CurrentSeason.objects.create(season=season)
    team_names = {}

    df = pd.read_csv("./data/NKL Tilastoja - Kaikki Joukkueet kausittain.csv")
    for index, row in df.iterrows():
        if (row["Kausi"], row["lyhenne"]) not in team_names:
            team_names[(row["Kausi"], row["lyhenne"])] = row["Joukkue ID"]
        team = None
        if not Team.objects.filter(id=row["Joukkue ID"]).exists():
            # print(row["lyhenne"] + " :" + str(row["Joukkue ID"]))
            team = Team.objects.create(id=row["Joukkue ID"], name=row["Koko nimi"], abbreviation=row["lyhenne"])
        else:
            # print("Updated: "+ str(row["Joukkue ID"]) + "to " + row["lyhenne"])
            team = Team.objects.filter(id=row["Joukkue ID"]).first()
            team.abbreviation = row["lyhenne"]
            team.name = row["Koko nimi"]
            team.save()
        print(row['Runkosarja Lohko ID'], type(row['Runkosarja Lohko ID']))
        bra = int(row['Runkosarja Lohko ID']) if not math.isnan(row['Runkosarja Lohko ID']) else 1
        season = Season.objects.filter(year=row["Kausi"]).first()
        TeamsInSeason.objects.create(season=season, team=team, 
                                     current_name=row["Koko nimi"], 
                                     current_abbreviation=row["lyhenne"],
                                     bracket=bra)
        
    df_players = pd.read_csv("./data/NKL Tilastoja - Kaikki Pelaajat.csv")
    print("Pelaajat:")

    print(PlayersInTeam.objects.all())
    for index, row in df_players.iterrows():
        if index % 100 == 0:
            print(f"Pelaajat: {index}")
        email = row["Etunimi"] + "." + row["Sukunimi"] + "@test.fi"
        if not User.objects.filter(first_name=row["Etunimi"], last_name=row["Sukunimi"]).exists():
            email = row["Etunimi"] + "." + row["Sukunimi"] + "@test.fi"
            user = User.objects.create_user(email, email, 'test')
            user.first_name = row["Etunimi"]
            user.last_name = row["Sukunimi"]
            user.save()
            Player.objects.create(user=user, number=random.randint(1, 99))

        season = Season.objects.filter(year=row["Kausi"]).first()
        team = Team.objects.filter(id=row["Joukkue ID"]).first()
        team_season = TeamsInSeason.objects.filter(season=season, team=team).first()
        user = User.objects.filter(first_name=row["Etunimi"], last_name=row["Sukunimi"]).first()

        if PlayersInTeam.objects.filter(team_season=team_season, player=user).exists():
            continue
        # print(f"{user}: {team}: {season}")
        PlayersInTeam.objects.create(team_season=team_season, player=user, is_captain=False)
    
    print("Ottelut: ")
    df_matches = pd.read_csv("./data/NKL Tilastoja - Kaikki Pelit.csv")
    
    for index, row in df_matches.iterrows():
        if index % 100 == 0:
            print(f"Ottelut {index}")
        season = Season.objects.filter(year=row["kausi"]).first()

        klo = "00:00:00" if not isinstance(row["klo"], str) else row["klo"]
        time = dt.datetime.strptime(klo,'%H:%M:%S').time()
        date = dt.datetime.strptime(row["pvm"], '%Y-%m-%d').date()

        home = TeamsInSeason.objects.filter(season=season, current_abbreviation=row["koti_joukkue"]).first()
        away = TeamsInSeason.objects.filter(season=season, current_abbreviation=row["vieras_joukkue"]).first()

        home_1 = row["k1"] if ord(row["k1"][0]) != 8722 else int(row["k1"][1:]) * -1
        home_2 = row["k2"] if ord(row["k2"][0]) != 8722 else int(row["k2"][1:]) * -1
        away_1 = row["v1"] if ord(row["v1"][0]) != 8722 else int(row["v1"][1:]) * -1
        away_2 = row["v2"] if ord(row["v2"][0]) != 8722 else int(row["v2"][1:]) * -1
        match = Match.objects.create(
            season = season,
            field = 0 if math.isnan(row["Kenttä nro."]) else row["Kenttä nro."],
            match_time = dt.datetime.combine(date, time),
            home_first_round_score=home_1,
            home_second_round_score=home_2,
            away_first_round_score=away_1,
            away_second_round_score=away_2,
            home_team=home,
            away_team=away,
            is_validated=True,
            post_season= (row["tyyppi"] != 1),
            match_type = row["tyyppi"],
            seriers = 0 if math.isnan(row["Pelisarja Id"]) else row["Pelisarja Id"],
        )
        # Koti 1. erä hp1
        makeThrow(row, "koti_e1_hp1_pelaaja", match, season, home, 1, 1, "koti_e1_1","koti_e1_2","koti_e1_9", "koti_e1_10")
        makeThrow(row, "koti_e1_hp2_pelaaja", match, season, home, 1, 2, "koti_e1_3","koti_e1_4","koti_e1_11", "koti_e1_12")
        makeThrow(row, "koti_e1_hp3_pelaaja", match, season, home, 1, 3, "koti_e1_5","koti_e1_6","koti_e1_13", "koti_e1_14")
        makeThrow(row, "koti_e1_hp4_pelaaja", match, season, home, 1, 4, "koti_e1_7","koti_e1_8","koti_e1_15", "koti_e1_16")

        makeThrow(row,"koti_e2_hp1_pelaaja", match, season, home, 2, 1, "koti_e2_1","koti_e2_2","koti_e2_9", "koti_e2_10")
        makeThrow(row,"koti_e2_hp2_pelaaja", match, season, home, 2, 2, "koti_e2_3","koti_e2_4","koti_e2_11", "koti_e2_12")
        makeThrow(row,"koti_e2_hp3_pelaaja", match, season, home, 2, 3, "koti_e2_5","koti_e2_6","koti_e2_13", "koti_e2_14")
        makeThrow(row,"koti_e2_hp4_pelaaja", match, season, home, 2, 4, "koti_e2_7","koti_e2_8","koti_e2_15", "koti_e2_16")

        makeThrow(row, "vieras_e1_hp1_pelaaja", match, season, away, 1, 1, "vieras_e1_1","vieras_e1_2","vieras_e1_9", "vieras_e1_10")
        makeThrow(row, "vieras_e1_hp2_pelaaja", match, season, away, 1, 2, "vieras_e1_3","vieras_e1_4","vieras_e1_11", "vieras_e1_12")
        makeThrow(row, "vieras_e1_hp3_pelaaja", match, season, away, 1, 3, "vieras_e1_5","vieras_e1_6","vieras_e1_13", "vieras_e1_14")
        makeThrow(row, "vieras_e1_hp4_pelaaja", match, season, away, 1, 4, "vieras_e1_7","vieras_e1_8","vieras_e1_15", "vieras_e1_16")

        makeThrow(row, "vieras_e2_hp1_pelaaja", match, season, away, 2, 1, "vieras_e2_1","vieras_e2_2","vieras_e2_9", "vieras_e2_10")
        makeThrow(row, "vieras_e2_hp2_pelaaja", match, season, away, 2, 2, "vieras_e2_3","vieras_e2_4","vieras_e2_11", "vieras_e2_12")
        makeThrow(row, "vieras_e2_hp3_pelaaja", match, season, away, 2, 3, "vieras_e2_5","vieras_e2_6","vieras_e2_13", "vieras_e2_14")
        makeThrow(row, "vieras_e2_hp4_pelaaja", match, season, away, 2, 4, "vieras_e2_7","vieras_e2_8","vieras_e2_15", "vieras_e2_16")

if __name__ == "__main__":
    init_gen()
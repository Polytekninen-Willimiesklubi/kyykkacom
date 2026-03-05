from django import forms
from django.contrib.auth.models import User

from kyykka.models import (
    CurrentSeason,
    PlayerAccolade,
    Season,
    TeamAccolade,
    TeamsInSeason,
)


class TeamModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: TeamsInSeason):
        return obj.current_abbreviation


class PlayerModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: User):
        return f"{obj.first_name} {obj.last_name}"


class SeasonAccoladeForm(forms.Form):
    # Player accolades
    kck_ahti = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="KCK Ahti",
        required=False,
    )
    player_of_the_year = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Vuoden Kyykkääjä",
        required=False,
    )
    opposite_genre_poy = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Vuoden nais-/mieskyykkääjä",
        required=False,
    )
    best_newcomer = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Vuoden Tulokas",
        required=False,
    )
    best_finisher = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Vuoden Viimeistelijä",
        required=False,
    )
    best_playoff_player = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Pudotuspelien paras",
        required=False,
    )
    best_bracket_player = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Runkosarjan paras",
        required=False,
    )
    pike_king = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Haukikuningas/-tar",
        required=False,
    )
    mvp = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Vuoden MVP",
        required=False,
    )
    evergreen_cutter = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Vuoden Kuusenkaataja",
        required=False,
    )
    individual_tournament_winner = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Henkkari-Cupin Voittaja",
        required=False,
    )
    individual_tournament_finalist = PlayerModelChoiceField(
        queryset=User.objects.none(),
        label="Henkkari-Cupin Finalisti",
        required=False,
    )

    # Team accolades
    champion = TeamModelChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="Liigamestari",
        required=False,
    )
    runner_up = TeamModelChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="Hopea mitallisti",
        required=False,
    )
    third_place = TeamModelChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="Pronssi mitallisti",
        required=False,
    )
    fourth_place = TeamModelChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="Neljäs sija",
        required=False,
    )
    super_weekend_winner = TeamModelChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="SuperWeekend-Cupin Voittaja",
        required=False,
    )
    super_weekend_second = TeamModelChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="SuperWeekend-Cupin Finalisti",
        required=False,
    )
    bracket_stage_winner = TeamModelChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="Runkosarjan voittaja",
        required=False,
    )

    # Other
    top8 = forms.ModelMultipleChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="Top 8; kaikki joukkueet jotka sijoittuivat 5-8",
        required=False,
    )
    top16 = forms.ModelMultipleChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="Top 16; kaikki joukkueet jotka sijoittuivat 9-16",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the selected season from form data (POST) or initial data
        season_id = None

        # Check form data first (for submitted forms)
        if self.data and "season_id" in self.data:
            try:
                # type ignore since we try except invald value
                season_id = int(self.data.get("season_id"))  # type: ignore
            except (ValueError, TypeError):
                pass

        # Then check initial data
        if season_id is None and "season_id" in self.initial:
            season_id = self.initial["season_id"]

        if season_id is None:
            try:
                season_id = CurrentSeason.objects.first()
                if season_id is None:
                    raise CurrentSeason.DoesNotExist
                season_id = season_id.season.pk
            except (CurrentSeason.DoesNotExist, AttributeError):
                pass
        # Only populate if we have a valid season
        if not isinstance(season_id, int):
            return

        season = Season.objects.get(id=season_id)
        # Get all players in this season
        player_ids = TeamsInSeason.objects.filter(season=season).values_list(
            "players", flat=True
        )
        season_players = User.objects.filter(id__in=player_ids).order_by(
            "first_name", "last_name"
        )

        # Get all teams in this season
        season_teams = TeamsInSeason.objects.filter(season=season).order_by(
            "current_abbreviation"
        )

        # Mapping of form field names to their labels for accolade matching
        label_to_field = {
            "KCK Ahti": "kck_ahti",
            "Vuoden Kyykkääjä": "player_of_the_year",
            "Vuoden nais-/mieskyykkääjä": "opposite_genre_poy",
            "Vuoden Tulokas": "best_newcomer",
            "Vuoden Viimeistelijä": "best_finisher",
            "Pudotuspelien paras": "best_playoff_player",
            "Runkosarjan paras": "best_bracket_player",
            "Haukikuningas/-tar": "pike_king",
            "Vuoden MVP": "mvp",
            "Vuoden Kuusenkaataja": "evergreen_cutter",
            "Henkkari-Cupin Voittaja": "individual_tournament_winner",
            "Henkkari-Cupin Finalisti": "individual_tournament_finalist",
            "Liigamestari": "champion",
            "Hopea mitallisti": "runner_up",
            "Pronssi mitallisti": "third_place",
            "Neljäs sija": "fourth_place",
            "SuperWeekend-Cupin Voittaja": "super_weekend_winner",
            "SuperWeekend-Cupin Finalisti": "super_weekend_second",
            "Runkosarjan voittaja": "bracket_stage_winner",
        }

        # Give all players to all player field fields and modify the label to show full name
        player_fields = [
            "kck_ahti",
            "player_of_the_year",
            "opposite_genre_poy",
            "best_newcomer",
            "best_finisher",
            "best_playoff_player",
            "best_bracket_player",
            "pike_king",
            "mvp",
            "evergreen_cutter",
            "individual_tournament_winner",
            "individual_tournament_finalist",
        ]
        player_accolades = PlayerAccolade.objects.filter(season=season)

        for field_name in player_fields:
            self.fields[field_name].queryset = season_players

        for player_accolade in player_accolades:
            if player_accolade.accolade.name not in label_to_field.keys():
                continue
            self.initial[label_to_field[player_accolade.accolade.name]] = (
                player_accolade.player.pk
            )

        # Give all teams to all team modal fields and modify the label to show current abbreviation
        team_fields = [
            "champion",
            "runner_up",
            "third_place",
            "fourth_place",
            "super_weekend_winner",
            "super_weekend_second",
            "bracket_stage_winner",
        ]

        team_accolades = TeamAccolade.objects.filter(season=season)

        for field_name in team_fields:
            self.fields[field_name].queryset = season_teams

        # Set the initial values if are accolades already setted for this season
        for team_accolade in team_accolades:
            if team_accolade.team is None:
                # Unknown team, skip
                continue
            if team_accolade.accolade.name == "Liigamestaruus":
                if team_accolade.placement == 1:
                    self.initial["champion"] = team_accolade.team.pk
                elif team_accolade.placement == 2:
                    self.initial["runner_up"] = team_accolade.team.pk
                elif team_accolade.placement == 3:
                    self.initial["third_place"] = team_accolade.team.pk
                elif team_accolade.placement == 4:
                    self.initial["fourth_place"] = team_accolade.team.pk
            elif team_accolade.accolade.name == "SuperWeekend-Cup":
                if team_accolade.placement == 1:
                    self.initial["super_weekend_winner"] = team_accolade.team.pk
                elif team_accolade.placement == 2:
                    self.initial["super_weekend_second"] = team_accolade.team.pk
            elif team_accolade.accolade.name == "Runkosarjamestaruus":
                if team_accolade.placement == 1:
                    self.initial["bracket_stage_winner"] = team_accolade.team.pk

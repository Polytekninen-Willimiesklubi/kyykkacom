from django import forms

from kyykka.models import (
    CurrentSeason,
    Season,
    TeamsInSeason,
    UserProxy,
)


class TeamModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: TeamsInSeason):
        return obj.current_abbreviation


class TeamModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj: TeamsInSeason):
        return obj.current_abbreviation


class SeasonAccoladeForm(forms.Form):
    # Player accolades
    kck_ahti = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="KCK Ahti",
        required=False,
    )
    player_of_the_year = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="Vuoden Kyykkääjä",
        required=False,
    )
    opposite_genre_poy = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="Vuoden nais-/mieskyykkääjä",
        required=False,
    )
    best_newcomer = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="Vuoden Tulokas",
        required=False,
    )
    best_finisher = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="Vuoden Viimeistelijä",
        required=False,
    )
    best_playoff_player = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="Pudotuspelien paras",
        required=False,
    )
    best_bracket_player = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="Runkosarjan paras",
        required=False,
    )
    pike_king = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="Haukikuningas/-tar",
        required=False,
    )
    mvp = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="Vuoden MVP",
        required=False,
    )
    evergreen_cutter = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="Vuoden Kuusenkaataja",
        required=False,
    )
    individual_tournament_winner = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
        label="Henkkari-Cupin Voittaja",
        required=False,
    )
    individual_tournament_finalist = forms.ModelChoiceField(
        queryset=UserProxy.objects.none(),
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
    top8 = TeamModelMultipleChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="Top 8; kaikki joukkueet jotka sijoittuivat 5-8. Käytä 'Ctrl' pohjassa, useamman valitsemiseen",
        required=False,
    )
    top16 = TeamModelMultipleChoiceField(
        queryset=TeamsInSeason.objects.none(),
        label="Top 16; kaikki joukkueet jotka sijoittuivat 9-16. Käytä 'Ctrl' pohjassa, useamman valitsemiseen",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the selected season from form data (POST) or initial data
        season_id = None

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
        season_players = UserProxy.objects.filter(id__in=player_ids).order_by(
            "first_name", "last_name"
        )

        # Get all teams in this season
        season_teams = TeamsInSeason.objects.filter(season=season).order_by(
            "current_abbreviation"
        )

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

        for field_name in player_fields:
            self.fields[field_name].queryset = season_players  # pyright: ignore[reportAttributeAccessIssue]

        # Give all teams to all team modal fields and modify the label to show current abbreviation
        team_fields = [
            "champion",
            "runner_up",
            "third_place",
            "fourth_place",
            "super_weekend_winner",
            "super_weekend_second",
            "bracket_stage_winner",
            "top8",
            "top16",
        ]

        for field_name in team_fields:
            self.fields[field_name].queryset = season_teams  # pyright: ignore[reportAttributeAccessIssue]

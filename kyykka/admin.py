from django.contrib import admin, messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path

from kyykka.admin_forms import SeasonAccoladeForm
from kyykka.models import (
    Accolade,
    CurrentSeason,
    ExtraBracketStagePlacement,
    Match,
    News,
    PlayerAccolade,
    PlayersInTeam,
    Season,
    SuperWeekend,
    Team,
    TeamAccolade,
    TeamsInSeason,
    Throw,
)

# Register your models here.


class PlayersInTeamInline(admin.TabularInline):
    """
    This is required to display PlayersInTeam at the admin panel,
    because the "through" attribute is used with the Team players ManyToManyField
    """

    model = PlayersInTeam
    extra = 1


class TeamsInSeasonInline(admin.TabularInline):
    model = TeamsInSeason
    extra = 1


class ThrowsInMatchInline(admin.TabularInline):
    model = Throw
    fields = ["player", "score_first", "score_second", "score_third", "score_fourth"]
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj):
        return False


class TeamsInSeasonAdmin(admin.ModelAdmin):
    inlines = (TeamsInSeasonInline,)


class PlayersInTeamAdmin(admin.ModelAdmin):
    search_fields = ["current_abbreviation"]
    inlines = (PlayersInTeamInline,)


class PlayerSearchAdmin(admin.ModelAdmin):
    search_fields = [
        "team_season__current_abbreviation",
        "team_season__season__year",
        "player__first_name",
        "player__last_name",
    ]


class ThrowsAdmin(admin.ModelAdmin):
    search_fields = [
        "home_team__current_abbreviation",
        "away_team__current_abbreviation",
    ]
    inlines = (ThrowsInMatchInline,)


def season_end_accolades(request, season_id: int | None = None):
    season = None
    initial = {}
    if season_id is None:
        try:
            current_season = CurrentSeason.objects.first()
            if current_season is None:
                messages.error(request, "No current season set.")
                return redirect("admin:index")
            season = current_season.season
        except CurrentSeason.DoesNotExist:
            messages.error(request, "No current season set.")
            return redirect("admin:index")
    else:
        try:
            season = Season.objects.get(id=season_id)
        except Season.DoesNotExist:
            messages.error(request, f"Season '{season_id}' not found.")
            return redirect("admin:index")

    initial["season_id"] = season.pk

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
    player_accolades = PlayerAccolade.objects.filter(season=season)

    for player_accolade in player_accolades:
        if player_accolade.accolade.name not in label_to_field.keys():
            continue
        if player_accolade.accolade.name == "Henkkari-Cup":
            if player_accolade.placement == 1:
                initial["individual_tournament_winner"] = player_accolade.player.pk
            elif player_accolade.placement == 2:
                initial["individual_tournament_finalist"] = player_accolade.player.pk
        else:
            initial[label_to_field[player_accolade.accolade.name]] = (
                player_accolade.player.pk
            )

    team_accolades = TeamAccolade.objects.filter(season=season)
    # Set the initial values if are accolades already setted for this season
    for team_accolade in team_accolades:
        if team_accolade.team is None:
            # Unknown team, skip
            continue
        if team_accolade.accolade.name == "Liigamestaruus":
            if team_accolade.placement == 1:
                initial["champion"] = team_accolade.team.pk
            elif team_accolade.placement == 2:
                initial["runner_up"] = team_accolade.team.pk
            elif team_accolade.placement == 3:
                initial["third_place"] = team_accolade.team.pk
            elif team_accolade.placement == 4:
                initial["fourth_place"] = team_accolade.team.pk

            elif team_accolade.placement == 8:
                if "top8" not in initial:
                    initial["top8"] = []
                initial["top8"].append(team_accolade.team.pk)
            elif team_accolade.placement == 16:
                if "top16" not in initial:
                    initial["top16"] = []
                initial["top16"].append(team_accolade.team.pk)
        elif team_accolade.accolade.name == "SuperWeekend-Cup":
            if team_accolade.placement == 1:
                initial["super_weekend_winner"] = team_accolade.team.pk
            elif team_accolade.placement == 2:
                initial["super_weekend_second"] = team_accolade.team.pk
        elif team_accolade.accolade.name == "Runkosarjamestaruus":
            if team_accolade.placement == 1:
                initial["bracket_stage_winner"] = team_accolade.team.pk

    form = SeasonAccoladeForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            # Create reverse mapping from field names to accolade names
            field_to_label = {v: k for k, v in label_to_field.items()}

            # ===== PROCESS PLAYER ACCOLADES =====
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
                posted_player = form.cleaned_data.get(field_name)
                accolade_name = field_to_label.get(field_name)

                if not accolade_name:
                    continue

                placement = None
                if accolade_name.startswith("Henkkari-Cupin"):
                    if accolade_name.endswith("Voittaja"):
                        placement = 1
                    elif accolade_name.endswith("Finalisti"):
                        placement = 2
                    accolade_name = "Henkkari-Cup"
                print(
                    "Processing field:",
                    field_name,
                    "Accolade:",
                    accolade_name,
                    "Placement:",
                    placement,
                )
                accolade = Accolade.objects.get(name=accolade_name)
                existing_accolade = PlayerAccolade.objects.filter(
                    season=season, accolade=accolade
                ).first()

                if posted_player:
                    # Data was posted - create or update

                    if existing_accolade:
                        # Update if player changed
                        if existing_accolade.player.pk != posted_player.pk:
                            existing_accolade.player = posted_player
                            existing_accolade.save()
                    else:
                        # Create new
                        PlayerAccolade.objects.create(
                            season=season,
                            accolade=accolade,
                            player=posted_player,
                            placement=placement,
                        )
                else:
                    # No data posted - delete if exists
                    if existing_accolade:
                        existing_accolade.delete()

            # ===== PROCESS TEAM ACCOLADES =====
            # Handle single-selection team fields (champion, runner_up, etc.)
            single_team_fields = {
                "champion": (1, "Liigamestaruus"),
                "runner_up": (2, "Liigamestaruus"),
                "third_place": (3, "Liigamestaruus"),
                "fourth_place": (4, "Liigamestaruus"),
                "super_weekend_winner": (1, "SuperWeekend-Cup"),
                "super_weekend_second": (2, "SuperWeekend-Cup"),
                "bracket_stage_winner": (1, "Runkosarjamestaruus"),
            }

            for field_name, (placement, accolade_name) in single_team_fields.items():
                posted_team = form.cleaned_data.get(field_name)
                accolade = Accolade.objects.get(name=accolade_name)
                existing_accolade = TeamAccolade.objects.filter(
                    season=season, accolade=accolade, placement=placement
                ).first()

                if posted_team:
                    # Data was posted - create or update
                    if existing_accolade:
                        # Update if team changed
                        if (
                            not existing_accolade.team
                            or existing_accolade.team.pk != posted_team
                        ):
                            existing_accolade.team = posted_team
                            existing_accolade.save()
                    else:
                        TeamAccolade.objects.create(
                            season=season,
                            accolade=accolade,
                            team=posted_team,
                            placement=placement,
                        )
                else:
                    # No data posted - delete if exists
                    if existing_accolade:
                        existing_accolade.delete()

            # Handle multi-selection team fields (top8, top16)
            multi_team_fields = {
                "top8": (8, "Liigamestaruus"),
                "top16": (16, "Liigamestaruus"),
            }

            for field_name, (placement, accolade_name) in multi_team_fields.items():
                posted_teams = form.cleaned_data.get(field_name, [])
                accolade = Accolade.objects.get(name=accolade_name)
                existing_accolades = TeamAccolade.objects.filter(
                    season=season, accolade=accolade, placement=placement
                )

                # Convert to set of IDs for comparison
                posted_ids_set = set(int(team.pk) for team in posted_teams)
                existing_ids_set = set(
                    existing_accolades.values_list("team_id", flat=True)
                )

                # Delete accolades that are no longer in posted data
                to_delete = existing_ids_set - posted_ids_set
                if to_delete:
                    existing_accolades.filter(team_id__in=to_delete).delete()

                # Create new accolades
                to_create = posted_ids_set - existing_ids_set
                for team_id in to_create:
                    team = TeamsInSeason.objects.get(pk=team_id)
                    TeamAccolade.objects.create(
                        season=season, accolade=accolade, team=team, placement=placement
                    )

        messages.success(request, "Accolades saved successfully!")
        return redirect("admin:index")

    context = dict(
        admin.site.each_context(request),
        form=form,
        title=f"Kauden {season.year} Palkinnot ja Kunnianosoitukset",
    )
    return render(request, "admin/season_accolades_form.html", context)


admin.site.register(TeamsInSeason, PlayersInTeamAdmin)
admin.site.register(Team)
admin.site.register(Season, TeamsInSeasonAdmin)
admin.site.register(PlayersInTeam, PlayerSearchAdmin)
admin.site.register(Match, ThrowsAdmin)
admin.site.register(Throw)
admin.site.register(CurrentSeason)
admin.site.register(SuperWeekend)
admin.site.register(News)
admin.site.register(ExtraBracketStagePlacement)
admin.site.register(Accolade)
admin.site.register(TeamAccolade)
admin.site.register(PlayerAccolade)


get_urls = admin.site.get_urls


def custom_get_urls():
    urls = get_urls()
    custom_urls = [
        path(
            "season-end-accolades/",
            admin.site.admin_view(season_end_accolades),
            name="season-end-accolades",
        ),
        path(
            "season-end-accolades/<int:season_id>/",
            admin.site.admin_view(season_end_accolades),
            name="season-end-accolades-with-id",
        ),
    ]
    return custom_urls + urls


admin.site.get_urls = custom_get_urls  # pyright: ignore[reportAttributeAccessIssue]

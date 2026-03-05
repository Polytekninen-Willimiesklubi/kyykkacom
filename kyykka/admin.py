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
    if season_id is None:
        try:
            current_season = CurrentSeason.objects.first()
            if current_season is None:
                messages.error(request, "No current season set.")
                return redirect("admin:index")
            season_id = current_season.season.pk
        except CurrentSeason.DoesNotExist:
            messages.error(request, "No current season set.")
            return redirect("admin:index")

    form = SeasonAccoladeForm(request.POST or None, initial={"season_id": season_id})
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            pass
        # Process the form data and save accolades
        messages.success(request, "Accolades saved successfully!")
        return redirect("admin:index")

    season = Season.objects.filter(id=season_id).first()
    if not season:
        messages.error(request, "Season not found.")
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

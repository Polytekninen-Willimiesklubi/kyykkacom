from django.contrib import admin

from kyykka.models import (
    CurrentSeason,
    ExtraBracketStagePlacement,
    Match,
    News,
    PlayersInTeam,
    Season,
    SuperWeekend,
    Team,
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
    inlines = (PlayersInTeamInline,)


class ThrowsAdmin(admin.ModelAdmin):
    inlines = (ThrowsInMatchInline,)


admin.site.register(TeamsInSeason, PlayersInTeamAdmin)
admin.site.register(Team)
admin.site.register(Season, TeamsInSeasonAdmin)
admin.site.register(PlayersInTeam)
admin.site.register(Match, ThrowsAdmin)
admin.site.register(Throw)
admin.site.register(CurrentSeason)
admin.site.register(SuperWeekend)
admin.site.register(News)
admin.site.register(ExtraBracketStagePlacement)

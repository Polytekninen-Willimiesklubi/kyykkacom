# from django.contrib.admin import action
from django.contrib import admin
from backend.utils import (
    count_negative_values, 
    count_throw_results, 
    count_score_total, 
    count_gte_six_throw_results,
    calculate_scaled_points
)

from backend.models import (
    Team, 
    Season, 
    PlayersInTeam, 
    Match, 
    Throw, 
    CurrentSeason, 
    TeamsInSeason, 
    SuperWeekend,
    SeasonStats,
    PositionStats,
)


# Register your models here.

class PlayersInTeamInline(admin.TabularInline):
    '''
    This is required to display PlayersInTeam at the admin panel,
    because the "through" attribute is used with the Team players ManyToManyField
    '''
    model = PlayersInTeam
    extra = 1

class TeamsInSeasonInline(admin.TabularInline):
    model = TeamsInSeason
    extra = 1

class PositionsStatsInline(admin.TabularInline):
    model = PositionStats
    extra = 1

class TeamsInSeasonAdmin(admin.ModelAdmin):
    inlines = (TeamsInSeasonInline,)
class PlayersInTeamAdmin(admin.ModelAdmin):
    inlines = (PlayersInTeamInline,)


def recalculate_selected_stastics(modeladmin, request, queryset):
    for selected in queryset.all():
        user = selected.player.player
        season = selected.player.team_season.season
        # Throw object is one periods all throws
        all_periods = Throw.objects.filter(
            match__is_validated=True,
            player=user,
            season=season,
        )
        
        # Before 2012 counting -> Format was different
        pikes, zeros = count_negative_values(all_periods, season)

        selected.periods = len(all_periods)
        selected.kyykat = count_score_total(all_periods)
        selected.throws = len(all_periods) * 4 - count_throw_results(all_periods, "e")
        selected.pikes = pikes + count_throw_results(all_periods, "h")
        selected.zeros = zeros + count_throw_results(all_periods, 0)
        selected.gte_six = count_gte_six_throw_results(all_periods)
        selected.scaled_points = calculate_scaled_points(all_periods)
        selected.save()

        all_positions = PositionStats.objects.filter(
            seasons_stats=selected
        )
        for i in range(1,5):
            pos = all_positions.filter(position=i).first()
            if not pos:
                pos = PositionStats.objects.create(
                    position=i,
                    seasons_stats=selected,
                )
            pos_throws = all_periods.filter(throw_turn=i)
            
            # Before 2012 counting -> Format was different
            pikes, zeros = count_negative_values(pos_throws, season)
            
            pos.periods = len(pos_throws)
            pos.throws = len(pos_throws) * 4 - count_throw_results(pos_throws, "e")
            pos.pikes = pikes + count_throw_results(pos_throws, "h")
            pos.zeros = zeros + count_throw_results(pos_throws, 0)
            pos.ones = count_throw_results(pos_throws, 1)
            pos.twos = count_throw_results(pos_throws, 2)
            pos.threes = count_throw_results(pos_throws, 3)
            pos.fours = count_throw_results(pos_throws, 4)
            pos.fives = count_throw_results(pos_throws, 5)
            pos.gte_six = count_gte_six_throw_results(pos_throws)
            pos.scaled_points = calculate_scaled_points(pos_throws)
            pos.save()
    # TODO Make responsive to send message if failed or success

class AdminSeasonStats(admin.ModelAdmin):
    inlines = (PositionsStatsInline,)
    actions = [recalculate_selected_stastics]

admin.site.register(TeamsInSeason, PlayersInTeamAdmin)
admin.site.register(Team)
admin.site.register(Season, TeamsInSeasonAdmin)
admin.site.register(PlayersInTeam)
admin.site.register(Match)
admin.site.register(Throw)
admin.site.register(CurrentSeason)
admin.site.register(SuperWeekend)
admin.site.register(SeasonStats, AdminSeasonStats)
admin.site.register(PositionStats)

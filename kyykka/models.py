from __future__ import annotations

import typing as t

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

# from utils.caching import reset_player_cache

if t.TYPE_CHECKING:

    class ScoreData(t.TypedDict):
        first_round_score: int | None
        second_round_score: int | None
        total: int | None


class MatchTypes(models.IntegerChoices):
    NOT_DEFINED = 0, _("Ei tyyppiä / Undefined")
    REGULAR_SEASON = 1, _("Runkosarja")
    FINAL = 2, _("Finaali")
    BRONZE = 3, _("Pronssi")
    SEMIFINAL = 4, _("Välierä")
    QUARTERFINAL = 5, _("Puolivälierä")
    EIGHTH_FINAL = 6, _("Neljännesvälierä")
    SIXTEENTH_FINAL = 7, _("Kahdeksannesvälierä")
    SECOND_ROUND = 8, _("2. Kierros")
    FIRST_ROUND = 9, _("1. Kierros")
    REGULAR_SEASON_FINAL = 10, _("Runkosarjafinaali")
    CONTINUATION_SERIES = 11, _("Jatkosarja")
    RELEGATION_PLAYOFF = 20, _("Putoamiskarsinta")
    SUPERWEEKEND_GROUP_STAGE = 31, _("SuperWeekend: Alkulohko")
    SUPERWEEKEND_FINAL = 32, _("SuperWeekend: Finaali")
    SUPERWEEKEND_BRONZE = 33, _("SuperWeekend: Pronssi")
    SUPERWEEKEND_SEMIFINAL = 34, _("SuperWeekend: Välierä")
    SUPERWEEKEND_QUARTERFINAL = 35, _("SuperWeekend: Puolivälierä")
    SUPERWEEKEND_EIGHTH_FINAL = 36, _("SuperWeekend: Neljännesvälierä")
    SUPERWEEKEND_SIXTEENTH_FINAL = 37, _("SuperWeekend: Kahdeksannesvälierä")


class PlayoffFormat(models.IntegerChoices):
    NOT_DEFINED = 0, _("Ei vielä päätetty / Undefined")
    FIXED_16_TEAM_CUP = 1, _("Kiinteä 16 joukkueen Cup")
    FIXED_8_TEAM_CUP = 2, _("Kiinteä 8 joukkueen Cup")
    FIXED_4_TEAM_CUP = 3, _("Kiinteä 4 joukkueen Cup")
    FIXED_22_TEAM_CUP = 4, _("Kiinteä 22 joukkueen Cup")
    FIRST_ROUND_SEEDING_6_TEAM_CUP = 5, _("1.Kierroksen Seedaus 6 joukkueen Cup")
    FIRST_ROUND_SEEDING_12_TEAM_CUP = 6, _("1.Kierroksen Seedaus 12 joukkueen Cup")
    SUPERWEEKEND_OKA_SEEDING_15_TEAM_CUP = (
        7,
        _("SuperWeekend OKA seedaus 15 joukkueen Cup"),
    )
    FIXED_30_TEAM_CUP = 8, _("Kiinteä 30 joukkueen Cup")


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="player")
    number = models.CharField(max_length=2, default="99")


class Team(models.Model):
    name = models.CharField(max_length=128, unique=True)
    abbreviation = models.CharField(max_length=15)

    def __str__(self):
        return "%s" % (self.abbreviation)


class Season(models.Model):
    year = models.CharField(max_length=4, unique=True)
    no_brackets = models.IntegerField(default=1, blank=False)
    playoff_format = models.IntegerField(
        default=0, blank=False, choices=PlayoffFormat.choices
    )

    def __str__(self):
        return f"Kausi {self.year}"


class CurrentSeason(models.Model):
    season = models.OneToOneField(Season, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Current Season"

    def __str__(self):
        return "Season %s" % (self.season.year)


class TeamsInSeason(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    current_name = models.CharField(max_length=128)
    current_abbreviation = models.CharField(max_length=15)
    players = models.ManyToManyField(User, through="PlayersInTeam")
    bracket = models.IntegerField(null=True)
    bracket_placement = models.IntegerField(
        blank=True, null=True
    )  # Winner of the Bracket stage is marked with 0
    second_stage_bracket = models.IntegerField(blank=True, null=True)
    super_weekend_bracket = models.IntegerField(blank=True, null=True)
    super_weekend_bracket_placement = models.IntegerField(blank=True, null=True)
    super_weekend_playoff_seed = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ("-season", "bracket", "bracket_placement")
        constraints = [
            models.UniqueConstraint(
                fields=["season", "team"], name="unique_team_season"
            )
        ]

    def __str__(self):
        return f"{self.current_abbreviation} {self.season.year}"


class SuperWeekend(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=False)
    winner = models.ForeignKey(TeamsInSeason, on_delete=models.CASCADE, null=True)
    super_weekend_no_brackets = models.IntegerField(default=0, blank=True, null=True)
    super_weekend_playoff_format = models.IntegerField(
        default=0, blank=True, null=True, choices=PlayoffFormat.choices
    )

    def __str__(self):
        return f"SuperWeekend {self.season.year}"


class PlayersInTeam(models.Model):
    team_season = models.ForeignKey(TeamsInSeason, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    is_captain = models.BooleanField(default=False)

    class Meta:
        unique_together = ("player", "team_season")
        # Make sure are players allowed to change team during the season?

    def __str__(self) -> str:
        return (
            f"{self.team_season.season.year} {self.team_season.current_abbreviation} "
            f"{self.player.first_name} {self.player.last_name}"
        )


class GameResult(models.TextChoices):
    NOT_PLAYED = "not_played"
    ON_GOING = "on_going"
    """"If match is on going. Maybe future use for live score updates."""
    HOME_WIN = "home_win"
    AWAY_WIN = "away_win"
    DRAW = "draw"
    HOME_WIN_BY_FORFEIT = "home_win_by_forfeit"
    """Counted as home win, but the forfeiting team points can be null. Match results should 
    not be counted towards Team result average, but the dividor should increase."""
    AWAY_WIN_BY_FORFEIT = "away_win_by_forfeit"
    """Counted as away win, but the forfeiting team points can be null. Match results should 
    not be counted towards Team result average, but the dividor should increase."""
    HOME_WIN_POINTLESS = "home_win_pointless"
    """Counted as home win, but no points are awarded. Council decides these"""
    AWAY_WIN_POINTLESS = "away_win_pointless"
    """Counted as away win, but no points are awarded. Council decides these"""


class Match(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    match_time = models.DateTimeField()
    field = models.IntegerField(blank=True, null=True)
    home_first_round_score = models.IntegerField(blank=True, null=True)
    home_second_round_score = models.IntegerField(blank=True, null=True)
    away_first_round_score = models.IntegerField(blank=True, null=True)
    away_second_round_score = models.IntegerField(blank=True, null=True)
    home_team = models.ForeignKey(
        TeamsInSeason, on_delete=models.CASCADE, related_name="home_matches"
    )
    away_team = models.ForeignKey(
        TeamsInSeason, on_delete=models.CASCADE, related_name="away_matches"
    )
    result = models.CharField(
        max_length=30,
        choices=GameResult.choices,
        null=True,
        default=GameResult.NOT_PLAYED,
    )
    is_validated = models.BooleanField(default=False)
    post_season = models.BooleanField(default=False)
    match_type = models.IntegerField(blank=True, null=True, choices=MatchTypes.choices)
    seriers = models.IntegerField(null=True, default=1)
    video_link = models.URLField(blank=True, null=True, max_length=100)
    stream_link = models.URLField(blank=True, null=True, max_length=100)

    class Meta:
        verbose_name_plural = "Matches"

    def get_opponent_team(self, team_id: int) -> TeamsInSeason:
        if team_id == self.home_team.team.pk:
            return self.away_team
        elif team_id == self.away_team.team.pk:
            return self.home_team
        else:
            raise ValueError("Team is not part of this match")

    def get_team_score_data(self, team_id: int) -> ScoreData:
        if team_id == self.home_team.team.pk:
            if (
                self.home_first_round_score is None
                and self.home_second_round_score is None
            ):
                total = None
            else:
                total = (self.home_first_round_score or 0) + (
                    self.home_second_round_score or 0
                )
            return {
                "first_round_score": self.home_first_round_score,
                "second_round_score": self.home_second_round_score,
                "total": total,
            }
        elif team_id == self.away_team.team.pk:
            if (
                self.away_first_round_score is None
                and self.away_second_round_score is None
            ):
                total = None
            else:
                total = (self.away_first_round_score or 0) + (
                    self.away_second_round_score or 0
                )
            return {
                "first_round_score": self.away_first_round_score,
                "second_round_score": self.away_second_round_score,
                "total": total,
            }
        else:
            raise ValueError("Team is not part of this match")

    def __str__(self):
        match_type = (
            "Ei tyyppiä"
            if self.match_type is None
            else MatchTypes(self.match_type).label
        )
        return (
            f"{self.match_time.strftime('%m/%d/%Y, %H:%M')} | {self.home_team} - "
            f"{self.away_team} | {match_type}"
        )


class Throw(models.Model):
    """
    throw_round determines is it first(1) or second(2) round of the match.
    throw_turn determines players' throwing turn: 1, 2, 3 or 4.
    throw_number determines is it players' 1st, 2nd, 3rd or 4th throw.
    """

    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    team = models.ForeignKey(TeamsInSeason, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    throw_round = models.IntegerField(db_index=True)
    throw_turn = models.IntegerField(db_index=True)
    score_first = models.CharField(max_length=2, null=True, blank=True)
    score_second = models.CharField(max_length=2, null=True, blank=True)
    score_third = models.CharField(max_length=2, null=True, blank=True)
    score_fourth = models.CharField(max_length=2, null=True, blank=True)

    def __str__(self):
        match_name = (
            MatchTypes(self.match.match_type).label
            if self.match.match_type in MatchTypes.values
            else "Ei valittu"
        )
        return (
            f"{self.match.home_team.current_abbreviation} vs. "
            f"{self.match.away_team.current_abbreviation} | "
            f"{match_name} | {self.team.current_abbreviation} | "
            f"{self.throw_round}. erä {self.throw_turn}. Heittopaikka"
        )


class ExtraBracketStagePlacement(models.Model):
    """Records the placements of teams in non-last bracket stage, if there are more than 1 stage.

    This can be merged to `TeamsInSeason` model if this format becomes frequent. This is done in
    this way to avoid mostly empty column in said model.

    Could also include other other placements aswell. (SuperWeekend + last stage + playoff)
    """

    team_in_season = models.ForeignKey(TeamsInSeason, on_delete=models.CASCADE)
    placement = models.IntegerField(null=True, blank=True)
    stage = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.team_in_season.season} : {self.team_in_season.current_abbreviation} : {self.stage}. vaihe: {self.placement}. Sija"

    class Meta:
        ordering = ("team_in_season", "stage", "placement")
        constraints = [
            models.UniqueConstraint(
                fields=["team_in_season", "stage"], name="unique_team_stage"
            )
        ]


class News(models.Model):
    header = models.TextField()
    writer = models.TextField(default="Anon")
    date = models.DateTimeField()
    text = models.TextField()

    class Meta:
        verbose_name_plural = "News"

    def __str__(self):
        return f"{self.date.strftime('%d-%m-%y')} {self.header}"


class PlacementOptions(models.IntegerChoices):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    TOP8 = 8
    TOP16 = 16
    TOP22 = 22
    TOP30 = 30


class Accolade(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)
    is_player_accolade = models.BooleanField(default=True)
    """If true, accolade is given to player, otherwise to team"""

    def __str__(self):
        return self.name


class PlayerAccolade(models.Model):
    accolade = models.ForeignKey(Accolade, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    justification = models.TextField(blank=True, null=True)
    placement = models.IntegerField(
        choices=PlacementOptions.choices, blank=True, null=True
    )

    def __str__(self):
        return f"{self.player} {self.season.year} {self.accolade.name}"


class TeamAccolade(models.Model):
    accolade = models.ForeignKey(Accolade, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    team = models.ForeignKey(
        TeamsInSeason, on_delete=models.CASCADE, blank=True, null=True
    )
    non_team_name = models.CharField(max_length=128, blank=True, null=True)
    """In case of accolade given to non-serious tournament like SM-kyykkä. Also unknown team 
    can be marked with this field."""
    placement = models.IntegerField(
        choices=PlacementOptions.choices, blank=True, null=True
    )

    def __str__(self):
        return f"{self.team} {self.season.year} {self.accolade.name}"


@receiver(post_save, sender=Match)
def match_post_save_handler(sender, instance, created, **kwargs):
    if created and instance:
        for team in [instance.home_team, instance.away_team]:
            for r in range(1, 3):
                for turn in range(1, 5):
                    Throw.objects.create(
                        match=instance,
                        team=team,
                        season=instance.season,
                        throw_turn=turn,
                        throw_round=r,
                    )
    # Update match when validation status changes from False to True
    elif (
        not created
        and instance.is_validated
        and instance.result == GameResult.NOT_PLAYED
    ):
        # Calculate scores directly (can't use properties in signal handlers)
        home_score = (instance.home_first_round_score or 0) + (
            instance.home_second_round_score or 0
        )
        away_score = (instance.away_first_round_score or 0) + (
            instance.away_second_round_score or 0
        )

        if home_score == away_score:
            instance.result = GameResult.DRAW.value
        elif home_score < away_score:
            instance.result = GameResult.HOME_WIN.value
        else:
            instance.result = GameResult.AWAY_WIN.value
        instance.save()

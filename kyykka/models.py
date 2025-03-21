from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# from utils.caching import reset_player_cache

MATCH_TYPES = {
    1: "Runkosarja",
    2: "Finaali",
    3: "Pronssi",
    4: "Välierä",
    5: "Puolivälierä",
    6: "Neljännesvälierä",
    7: "Kahdeksannesvälierä",
    8: "2. Kierros",
    9: "1. Kierros",
    10: "Runkosarjafinaali",
    11: "Jatkosarja",
    20: "Putoamiskarsinta",
    31: "SuperWeekend: Alkulohko",
    32: "SuperWeekend: Finaali",
    33: "SuperWeekend: Pronssi",
    34: "SuperWeekend: Välierä",
    35: "SuperWeekend: Puolivälierä",
    36: "SuperWeekend: Neljännesvälierä",
    37: "SuperWeekend: Kahdeksannesvälierä",
}

MATCH_TYPES_TUPLES = [(key, val) for key, val in MATCH_TYPES.items()]

PLAYOFF_FORMAT = {
    0: "Ei vielä päätetty / Undefined",
    1: "Kiinteä 16 joukkueen Cup",
    2: "Kiinteä 8 joukkueen Cup",
    3: "Kiinteä 4 joukkueen Cup",
    4: "Kiinteä 22 joukkueen Cup",
    5: "1.Kierroksen Seedaus 6 joukkueen Cup",
    6: "1.Kierroksen Seedaus 12 joukkueen Cup",
    7: "SuperWeekend OKA seedaus 15 joukkueen Cup",
    8: "Kiinteä 30 joukkueen Cup",
}

PLAYOFF_FORMAT_TUPLES = [(key, val) for key, val in PLAYOFF_FORMAT.items()]


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="player")
    number = models.CharField(max_length=2, default=99)


class Team(models.Model):
    name = models.CharField(max_length=128, unique=True)
    abbreviation = models.CharField(max_length=15)

    def __str__(self):
        return "%s" % (self.abbreviation)


class Season(models.Model):
    year = models.CharField(max_length=4, unique=True)
    no_brackets = models.IntegerField(default=1, blank=False)
    playoff_format = models.IntegerField(
        default=0, blank=False, choices=PLAYOFF_FORMAT_TUPLES
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
        default=0, blank=True, null=True, choices=PLAYOFF_FORMAT_TUPLES
    )

    def __str__(self):
        return f"SuperWeekend {self.season.year}"


class PlayersInTeam(models.Model):
    team_season = models.ForeignKey(TeamsInSeason, on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_captain = models.BooleanField(default=False)

    class Meta:
        unique_together = ("player", "team_season")
        # Make sure are players allowed to change team during the season?

    def __str__(self):
        return "%s %s %s %s" % (
            self.team_season.season.year,
            self.team_season.current_abbreviation,
            self.player.first_name,
            self.player.last_name,
        )


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
    is_validated = models.BooleanField(default=False)
    post_season = models.BooleanField(default=False)
    match_type = models.IntegerField(blank=True, null=True, choices=MATCH_TYPES_TUPLES)
    seriers = models.IntegerField(null=True, default=1)
    video_link = models.URLField(blank=True, null=True, max_length=100)
    stream_link = models.URLField(blank=True, null=True, max_length=100)

    class Meta:
        verbose_name_plural = "Matches"

    def __str__(self):
        if self.match_type is None:
            print_string = "Matsi tyyppi ei valittu"
        else:
            print_string = MATCH_TYPES[self.match_type]
        return (
            f"{self.match_time.strftime('%m/%d/%Y, %H:%M')} | {self.home_team} - "
            f"{self.away_team} | {print_string}"
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
            MATCH_TYPES[self.match.match_type]
            if self.match.match_type in MATCH_TYPES
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

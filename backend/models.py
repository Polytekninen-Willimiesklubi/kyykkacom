from typing import Any
from django.db import models
from django.db.models import F, Q
from django.db.models.constraints import UniqueConstraint, CheckConstraint
from django.utils.timezone import now
from django.contrib.auth.models import User
from backend.utils import (
    MATCH_TYPES,
    PLAYOFF_FORMAT,
    DIVISIONS,
    SUPER_WEEKEND_MATCHES,
    scaled_points
)


class News(models.Model):
    """Simple news object. Contains information shown at the front-page.
    """
    header = models.TextField(max_length=40)
    writer = models.TextField(blank=True)
    date = models.DateTimeField(default=now, editable=True)
    text = models.TextField()

class Player(models.Model):
    """User accounts actual information. Works as a handle. This is done 
    to make possible to remove the account and leave statistics behind. 
    """
    first_name = models.CharField(max_length=32, blank=False, default="")
    last_name = models.CharField(max_length=32, blank=False, default="")
    user = models.OneToOneField(User, null=True, blank=True) # Optional
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Team(models.Model):
    """Team model that is consistent year-to-year basis. In effect allows to map all-time statistics
    """
    name = models.CharField(max_length=128, unique=True, blank=False)
    abbreviation = models.CharField(max_length=15, blank=False)

    def __str__(self):
        return f"{self.abbreviation}"

class Season(models.Model):
    """Annual season model that defines season's year and superweekend information.
    """
    year = models.IntegerField(primary_key=True)
    super_weekend_no_brackets = models.IntegerField(default=0, blank=True, null=True)
    super_weekend_playoff_format = models.IntegerField(
        default=0, 
        blank=True, 
        null=True, 
        choices=SUPER_WEEKEND_MATCHES,
    )
    super_weekend_winner = models.IntegerField('TeamsInSeason', blank=True, null=True)

    def __str__(self):
        return f"Kausi {self.year}"
    
class CurrentSeason(models.Model):
    """Current Season model. One-to-one relationship with 'Season'-model.
    Only one season should be the "Current" at a time. 
    """
    season = models.OneToOneField(Season, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Current Season'

    def __str__(self):
        return 'Season %s' % (self.season.year)


class Division(models.Model):
    """Season's different seriers. 'Level' indicates the difference with in a year's season. 
    Includes information regarding brackets and playoff format
    """
    season: Season = models.ForeignKey(Season, blank=False)
    level = models.IntegerField(default=0, blank=False, choices=DIVISIONS)
    no_brackets = models.IntegerField(default=1, blank=False)
    playoff_format = models.IntegerField(default=0, blank=False, choices=PLAYOFF_FORMAT)
    season_winner = models.OneToOneField(Team, blank=True, null=True)
    bracket_stage_winner = models.OneToOneField(Team, blank=True, null=True)
    teams = models.ManyToManyField(Team, through='TeamsInSeason')

    def __str__(self):
        return f"Kausi {self.season} {self.level}"

    class Meta:
        constraints = [
            UniqueConstraint('level', 'season', name="unique_division")
        ]

class TeamsInSeason(models.Model):
    """Teams in season. Breaks down Many-to-many relationship with 'Teams' and 'Season'. This also
    allows teams have different names between years but still have consitent all-time record.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    players = models.ManyToManyField(Player, through='PlayersInTeam')
    captain = models.OneToOneField(Player, blank=True)
    name =  models.CharField(max_length=128)
    abbreviation = models.CharField(max_length=15)
    bracket = models.IntegerField(blank=False, default=1)
    bracket_placement = models.IntegerField(blank=True, null=True)  # Winner is marked with 0 
    super_weekend_bracket = models.IntegerField(blank=True, null=True)
    super_weekend_bracket_placement = models.IntegerField(blank=True, null=True)
    super_weekend_playoff_seed = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return f'{self.abbreviation} {self.division.season.year}'

    def save(self, *args, **kwargs):
        # If this is the most recent iteration of this team, change the name of the 'Team-model'
        instance_year = self.division.season.year
        most_recent_saved = TeamsInSeason.objects.filter(
            team=self.team
        ).order_by("-division__season__year").first()
        
        if instance_year > most_recent_saved.division.season.year:
            t: Team = self.team
            t.name = self.name
            t.abbreviation = self.abbreviation
            t.save()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('season', 'team')
        ordering = ("bracket", "bracket_placement")

class PlayersInTeam(models.Model):
    """Breaks Many-to-Many relationship to One-to-Many with `TeamsInSeason` and `Player` models.
    The model is needed for tracking possible player transfer within season.   

    In the case where `Player` will tranfer from `Team` A to B and then back, no new 
    record should be created when player is 'coming' back to A-team and existing should be used.
    `active`-field shall imply what player instance is currently in use.
    NOTE: This mighty be place to use `PlayerInSeason` kind a of relationship
    """
    team_in_season = models.ForeignKey(TeamsInSeason, on_delete=models.DO_NOTHING, null=True)
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING, null=True, related_name="all_teams")
    stats = models.OneToOneField('SeasonStats', on_delete=models.DO_NOTHING, null=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return (
            f"{self.team_in_season.division.season.year} {self.team_in_season.abbreviation} "   
            f"{self.player.first_name} {self.player.last_name}"
        )

    def save(self, **kwargs):
        # Makes SeasonStats instance if `save()` is also creating  
        if self._state.adding is True:
            SeasonStats.objects.create(player=self)
        # Unless it wasn't spesified that added player is non-active in saving 
        # process assume trasfer process between players
        if self.active:
            PlayersInTeam.objects.filter(
                teams_in_season__division__season=self.team_in_season__division__season
            ).update(active=False)
        super().save(**kwargs)

    class Meta:
        constraints = [
            UniqueConstraint('team_in_season', 'player', name="unique_player")
        ]

class TransferRecord(models.Model):
    """Contains all the transfer logs within seasons barring 
    the initial reservations in the begin of season.

    Null value in one of the 'team' fields means 'free agent' status.

    Quarantine period, if it's deemed apporiate by admin with "can_play_from" field.
    TODO: Player ---?
    """
    timestamp = models.DateTimeField(default=now, editable=True, blank=False)
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING, blank=False)
    from_team = models.ForeignKey(TeamsInSeason, on_delete=models.DO_NOTHING, blank=True, null=True)
    to_team = models.ForeignKey(TeamsInSeason, on_delete=models.DO_NOTHING, blank=True, null=True)
    can_play_from = models.DateTimeField(default=now, editable=True, blank=True)

    def __str__(self):
        return (
                f"{self.player_in_team.player} {self.from_team.abbreviation} -> "
                f"{self.to_team.abbreviation}"
            )
    
    def save(self, **kwargs):
        # deactivate former and activate current team player_in_team model
        former_handle = PlayersInTeam.objects.get(team_in_season=self.from_team, player=self.player)
        former_handle.active = False
        former_handle.save()
        PlayersInTeam.objects.update_or_create(
            team_in_season=self.to_team,
            player=self.player,
            default={"active" : True},
            crete_defaults={"active": True}
        )
        super().save(**kwargs)

    class Meta:
        constraints = [
            # Forbid transfer A to A
            CheckConstraint(name="not_same", check=~Q(from_team=F("to_team")))
        ]

class Match(models.Model):
    """Models one NKL match. 
    
    NOTE for dev: Match type choises comes from hardcoded list. Model+ForeignKey could be 
    considered here, but reasoning is that current playoff logic need already also refactoring 
    (most likely) if new playoff numbers etc. would be added. So there is no value for modifing it 
    in runtime if logic should be also added.

    Matches link together (in playoffs) with 'Seriers'-field.

    """
    division = models.ForeignKey(Division, on_delete=models.DO_NOTHING, related_name="matches")
    match_time = models.DateTimeField()
    field = models.IntegerField(blank=True, null=True)
    home_first_round_score = models.IntegerField(blank=True, null=True)
    home_second_round_score = models.IntegerField(blank=True, null=True)
    away_first_round_score = models.IntegerField(blank=True, null=True)
    away_second_round_score = models.IntegerField(blank=True, null=True)
    home_team = models.ForeignKey(
        TeamsInSeason, 
        on_delete=models.DO_NOTHING,
        related_name='home_matches'
    )
    away_team = models.ForeignKey(
        TeamsInSeason,
        on_delete=models.DO_NOTHING,
        related_name='away_matches'
    )
    is_validated = models.BooleanField(default=False)
    post_season = models.BooleanField(default=False)
    match_type = models.IntegerField(blank=True, null=True, choices=MATCH_TYPES)
    seriers = models.IntegerField(null=True, default=1)

    def __str__(self):
        return f"{self.match_time.strftime("%m/%d/%Y, %H:%M")} | {self.home_team} - {self.away_team}"

    def save(self, **kwargs):
        # Make the throws if saved Match is new (created)
        if self._state.adding is True:
            Throw.objects.bulk_create(
                [
                    Throw(
                        match=self,
                        team=team,
                        throw_turn=turn,
                        throw_round=_round,
                    ) 
                    for team in [self.home_team, self.away_team]
                    for _round in range(1,3)
                    for turn in range(1,5)
                ]
            )
        super().save(**kwargs)

    class Meta:
        verbose_name_plural = 'Matches'


class Throw(models.Model):
    """Set of 4 throws. Represents one player's one round throws in a match. There should be 4 
    of these in a round per team and in total 16 (2 rounds x 4 players x 2 teams). 
    
    `score_first` and `score_second` fields happen in a first half of the round. Check team rules 
    for more clarifaction. `throw_round` is the as a match round and `throw_turn` tells the players 
    order within in the team.

    Saving the model should automaticly update Season Statistics and Position Statistics
    """
    match = models.ForeignKey(Match, on_delete=models.DO_NOTHING, related_name="throws")
    player = models.ForeignKey(PlayersInTeam, null=True, on_delete=models.DO_NOTHING, related_name="throws")
    team = models.ForeignKey(TeamsInSeason, on_delete=models.DO_NOTHING, related_name="all_throws")
    throw_round = models.IntegerField(db_index=True)
    throw_turn = models.IntegerField(db_index=True)
    score_first = models.CharField(max_length=2, null=True, blank=True)
    score_second = models.CharField(max_length=2, null=True, blank=True)
    score_third = models.CharField(max_length=2, null=True, blank=True)
    score_fourth = models.CharField(max_length=2, null=True, blank=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(Throw, self).__init__(*args, **kwargs)
        self.__position = ['score_first', 'score_second', 'score_third', 'score_fourth']
        self.__orginal_player = None
        for field in self.__position:
            setattr(self, f'__original_{field}', None)

    def __str__(self) -> str:
        return (
            f"{self.match.division.season} {self.match.match_type} : "
            f"{self.throw_round}. Kierros Heittopaikka:{self.throw_turn}"
        )
    
    def save(self, **kwargs) -> None:
        # Update stats before saving
        def return_idx(score) -> int:
            if score == "h":
                return 7
            elif score < 6:
                return score
            else:
                return 6

        def aggragate_data(original:bool) -> list[int | float]:
            vector = [0] * 11
            for i, field in enumerate(self.__position):
                orig_score = getattr(self, f'{"__original_" if original else ""}{field}')
                orig_score = None if orig_score == 'e' else orig_score
                if isinstance(orig_score, int):
                    vector[return_idx(orig_score)] += 1
                    vector[8] += orig_score
                    vector[9] += scaled_points(orig_score, i)
                    vector[10] += 1
                elif orig_score == "h":
                    vector[return_idx(orig_score)] += 1
                    vector[10] += 1
            return vector
        
        # First remove stats from original player. 
        if self.__orginal_player is not None:
            *throw_results, score, scaled, total_throws = aggragate_data(True)
            season_stats = SeasonStats.objects.get(player=self.__orginal_player)
            position_stats = PositionStats.objects.get(
                ss=season_stats, 
                position=self.throw_turn
            )

            position_stats.zeros -= throw_results[0]
            position_stats.ones -= throw_results[1]
            position_stats.twos -= throw_results[2]
            position_stats.threes -= throw_results[3]
            position_stats.fours -= throw_results[4]
            position_stats.fives -= throw_results[5]
            position_stats.gte_six -= throw_results[6]
            position_stats.pikes -= throw_results[7]
            position_stats.kyykat -= score 
            position_stats.scaled_points -= scaled
            position_stats.throws -= total_throws

            season_stats.zeros -= throw_results[0]
            season_stats.ones -= throw_results[1]
            season_stats.twos -= throw_results[2]
            season_stats.threes -= throw_results[3]
            season_stats.fours -= throw_results[4]
            season_stats.fives -= throw_results[5]
            season_stats.gte_six -= throw_results[6]
            season_stats.pikes -= throw_results[7]
            season_stats.kyykat -= score 
            season_stats.scaled_points -= scaled
            season_stats.throws -= total_throws
        
        # Then add the stats to other player. This means we might do some unneccesary calculations
        # But this IMO this is less convoluted way of doing this
        if self.player is not None:
            *throw_results, score, scaled, total_throws = aggragate_data(False)
            season_stats = SeasonStats.objects.get(player=self.player)
            position_stats, _ = PositionStats.objects.get_or_create(
                ss=season_stats, 
                position=self.throw_turn
            )

            position_stats.zeros += throw_results[0]
            position_stats.ones += throw_results[1]
            position_stats.twos += throw_results[2]
            position_stats.threes += throw_results[3]
            position_stats.fours += throw_results[4]
            position_stats.fives += throw_results[5]
            position_stats.gte_six += throw_results[6]
            position_stats.pikes += throw_results[7]
            position_stats.kyykat += score
            position_stats.scaled_points += scaled
            position_stats.throws += total_throws

            season_stats.zeros += throw_results[0]
            season_stats.ones += throw_results[1]
            season_stats.twos += throw_results[2]
            season_stats.threes += throw_results[3]
            season_stats.fours += throw_results[4]
            season_stats.fives += throw_results[5]
            season_stats.gte_six += throw_results[6]
            season_stats.pikes += throw_results[7]
            season_stats.kyykat += score
            season_stats.scaled_points += scaled
            season_stats.throws += total_throws

        super().save(**kwargs)

class SeasonStats(models.Model):
    """Season Statistics for player with One-to-one relationship. This is summary model and should 
    sum of all `PositionStats` instances that have this key. `PositionStats` should be created only 
    when it's needed to avoid reduntant zero rows.
    """
    player = models.OneToOneField(PlayersInTeam, primary_key=True, on_delete=models.DO_NOTHING)
    periods = models.IntegerField(default=0)
    kyykat = models.IntegerField(default=0)
    throws = models.IntegerField(default=0)
    pikes = models.IntegerField(default=0)
    zeros = models.IntegerField(default=0)
    ones = models.IntegerField(default=0)
    twos = models.IntegerField(default=0)
    threes = models.IntegerField(default=0)
    fours = models.IntegerField(default=0)
    fives = models.IntegerField(default=0)
    gte_six = models.IntegerField(default=0)
    scaled_points = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Seasons Stats'

    def __str__(self):
        return (
            f"{self.player.player.first_name} "
            f"{self.player.player.last_name} "
            f"{self.player.team_season.season.year} "
            f"{self.player.team_season.current_abbreviation}"
        )

class PositionStats(models.Model):
    """Position spesific statistics. Only if player has played in the position, only then should
    a dataclass of this be created. This is to avoid reduntant zero rows. This data should be 
    updated when saving `Throws` class. 
    """
    seasons_stats = models.ForeignKey(SeasonStats, on_delete=models.DO_NOTHING)
    position = models.IntegerField(default=1)
    periods = models.IntegerField(default=0)
    kyykat = models.IntegerField(default=0)
    throws = models.IntegerField(default=0)
    pikes = models.IntegerField(default=0)
    zeros = models.IntegerField(default=0)
    ones = models.IntegerField(default=0)
    twos = models.IntegerField(default=0)
    threes = models.IntegerField(default=0)
    fours = models.IntegerField(default=0)
    fives = models.IntegerField(default=0)
    gte_six = models.IntegerField(default=0)
    scaled_points = models.IntegerField(default=0)

    def __str__(self):
        return (
            f"{self.seasons_stats.player.player.first_name} "
            f"{self.seasons_stats.player.player.last_name} "
            f"{self.seasons_stats.player.team_season.season.year} "
            f"{self.seasons_stats.player.team_season.current_abbreviation} {self.position}"
        )
    class Meta:
        verbose_name_plural = 'Positions Stats'


class Seriers(models.Model):
    """TODO make a doctstring"""
    seriers_type = models.IntegerField(blank=True, null=True, choices=MATCH_TYPES)
    matches_to_win = models.IntegerField(blank=False, default=2)
    team_A = models.ForeignKey(TeamsInSeason, null=True, on_delete=models.DO_NOTHING)
    team_B = models.ForeignKey(TeamsInSeason, null=True, on_delete=models.DO_NOTHING)
    winner = models.ForeignKey(TeamsInSeason, null=True, on_delete=models.DO_NOTHING)
    matches = models.ManyToManyField(Match, through='MatchesInSeriers') # This is for convinience ('Related manager')


    def save(self, **kwargs):
        # TODO Make this do automatically at least matches_to_win amount of games if created.
        super().save(**kwargs)

    class Meta:
        constraints = [
            # Forbid team playing against itself
            CheckConstraint(name="not_same", check=~Q(team_A=F("team_B")))
        ]

class MatchesInSeriers(models.Model):
    """TODO make a doctstring"""
    seriers = models.ForeignKey(Seriers, on_delete=models.DO_NOTHING, blank=False)
    match = models.OneToOneField(Match, primary_key=True, on_delete=models.DO_NOTHING, blank=False)
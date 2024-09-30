import typing as t
from django.db import models

from django.db.models import (
    F, 
    Q,
    Model,
    TextField,
    DateTimeField,
    CharField,
    OneToOneField,
    IntegerField,
    ForeignKey,
    ManyToManyField,
)
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


class News(Model):
    """Simple news object. Contains information shown at the front-page.
    """
    header = TextField(max_length=40)
    writer = TextField(blank=True)
    date = DateTimeField(default=now, editable=True)
    text = TextField()

class Player(Model):
    """User accounts actual information. Works as a handle. This is done 
    to make possible to remove the account and leave statistics behind. 
    """
    first_name = CharField(max_length=32, blank=False, default="")
    last_name = CharField(max_length=32, blank=False, default="")
    user = OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE) # Optional
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Team(Model):
    """Team model that is consistent year-to-year basis. In effect allows to map all-time statistics
    """
    name = CharField(max_length=128, unique=True, blank=False)
    abbreviation = CharField(max_length=15, blank=False)

    def __str__(self):
        return f"{self.abbreviation}"

class Season(Model):
    """Annual season model that defines season's year and superweekend information.
    """
    year = IntegerField(primary_key=True)
    super_weekend_no_brackets = IntegerField(default=0, blank=True, null=True)
    super_weekend_playoff_format = IntegerField(
        default=0, 
        blank=True, 
        null=True, 
        choices=SUPER_WEEKEND_MATCHES,
    )
    super_weekend_winner = IntegerField('TeamsInSeason', blank=True, null=True)

    def __str__(self):
        return f"Kausi {self.year}"
    
class CurrentSeason(Model):
    """Current Season model. One-to-one relationship with 'Season'-model.
    Only one season should be the "Current" at a time. 
    """
    season = OneToOneField(Season, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Current Season'

    def __str__(self):
        return 'Season %s' % (self.season.year)


class Division(Model):
    """Season's different seriers. 'Level' indicates the difference with in a year's season. 
    Includes information regarding brackets and playoff format
    """
    season: Season = ForeignKey(Season, blank=False, on_delete=models.CASCADE)
    level = IntegerField(default=0, blank=False, choices=DIVISIONS)
    no_brackets = IntegerField(default=1, blank=False)
    playoff_format = IntegerField(default=0, blank=False, choices=PLAYOFF_FORMAT)
    season_winner = OneToOneField('TeamsInSeason', blank=True, null=True, on_delete=models.CASCADE, related_name="division_winner")
    bracket_stage_winner = OneToOneField('TeamsInSeason', blank=True, null=True, on_delete=models.CASCADE, related_name="bracket_stage_winner")

    def __str__(self):
        return f"Kausi {self.season} {self.level}"

    class Meta:
        constraints = [
            UniqueConstraint('level', 'season', name="unique_division")
        ]

class TeamsInSeason(Model):
    """Teams in season. Breaks down Many-to-many relationship with 'Teams' and 'Season'. This also
    allows teams have different names between years but still have consitent all-time record.
    """
    team = ForeignKey(Team, on_delete=models.CASCADE, related_name="season_teams")
    division = ForeignKey(Division, on_delete=models.CASCADE, related_name="teams")
    players = ManyToManyField(Player, through='PlayersInTeam', related_name="teams")
    captain = OneToOneField(Player, blank=True, on_delete=models.CASCADE)
    name =  CharField(max_length=128)
    abbreviation = CharField(max_length=15)
    bracket = IntegerField(blank=False, default=1)
    bracket_placement = IntegerField(blank=True, null=True)  # Winner is marked with 0 

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
        unique_together = ('division', 'team')
        ordering = ("bracket", "bracket_placement")

class PlayersInTeam(Model):
    """Breaks Many-to-Many relationship to One-to-Many with `TeamsInSeason` and `Player` models.
    The model is needed for tracking possible player transfer within season.   

    In the case where `Player` will tranfer from `Team` A to B and then back, no new 
    record should be created when player is 'coming' back to A-team and existing should be used.
    `active`-field shall imply what player instance is currently in use.
    NOTE: This mighty be place to use `PlayerInSeason` kind a of relationship
    """
    team_in_season = ForeignKey(TeamsInSeason, on_delete=models.CASCADE, null=True)
    player = ForeignKey(Player, on_delete=models.CASCADE, null=True, related_name="all_teams")
    stats = OneToOneField('SeasonStats', on_delete=models.CASCADE, null=True)
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

class Transfer(Model):
    """Contains all the transfer logs within seasons barring 
    the initial reservations in the begin of season.

    Null value in one of the 'team' fields means 'free agent' status.

    Quarantine period, if it's deemed apporiate by admin with "can_play_from" field.
    TODO: Player ---?
    """
    timestamp = DateTimeField(default=now, editable=True, blank=False)
    player_in_team = ForeignKey(PlayersInTeam, on_delete=models.CASCADE, blank=False)
    to_team = ForeignKey(TeamsInSeason, on_delete=models.CASCADE, blank=False, null=False)
    can_play_from = DateTimeField(default=now, editable=True, blank=True)

    def __str__(self):
        return (
                f"{self.player_in_team.player} {self.player_in_team.team_in_season.abbreviation} -> "
                f"{self.to_team.abbreviation}"
            )
    
    def save(self, **kwargs):
        # deactivate former and activate current team player_in_team model
        self.player_in_team.active = False
        self.player_in_team.save()
        PlayersInTeam.objects.update_or_create(
            team_in_season=self.to_team,
            player=self.player_in_team.player,
            default={"active" : True},
            crete_defaults={"active": True}
        )
        super().save(**kwargs)

class Match(Model):
    """Models one NKL match. 
    
    NOTE for dev: Match type choises comes from hardcoded list. Model+ForeignKey could be 
    considered here, but reasoning is that current playoff logic need already also refactoring 
    (most likely) if new playoff numbers etc. would be added. So there is no value for modifing it 
    in runtime if logic should be also added.

    Matches link together (in playoffs) with 'Seriers'-field.

    """
    division = ForeignKey(Division, on_delete=models.CASCADE, related_name="matches")
    seriers = ForeignKey('Seriers', null=True, on_delete=models.CASCADE, related_name="matches")
    home_team = ForeignKey(
        TeamsInSeason, 
        null=True,
        on_delete=models.CASCADE,
        related_name='home_matches'
    )
    away_team = ForeignKey(
        TeamsInSeason,
        null=True,
        on_delete=models.CASCADE,
        related_name='away_matches'
    )
    match_time = DateTimeField()
    field = IntegerField(blank=True, null=True)
    home_first_round_score = IntegerField(blank=True, null=True)
    home_second_round_score = IntegerField(blank=True, null=True)
    away_first_round_score = IntegerField(blank=True, null=True)
    away_second_round_score = IntegerField(blank=True, null=True)
    is_validated = models.BooleanField(default=False)
    post_season = models.BooleanField(default=False)
    match_type = IntegerField(blank=True, null=True, choices=MATCH_TYPES)

    def __str__(self):
        return f"{self.match_time.strftime('%m/%d/%Y, %H:%M')} | {self.home_team} - {self.away_team}"

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


class Throw(Model):
    """Set of 4 throws. Represents one player's one round throws in a match. There should be 4 
    of these in a round per team and in total 16 (2 rounds x 4 players x 2 teams). 
    
    `score_first` and `score_second` fields happen in a first half of the round. Check team rules 
    for more clarifaction. `throw_round` is the as a match round and `throw_turn` tells the players 
    order within in the team.

    Saving the model should automaticly update Season Statistics and Position Statistics
    """
    match = ForeignKey(Match, on_delete=models.CASCADE, related_name="throws")
    player = ForeignKey(PlayersInTeam, null=True, on_delete=models.CASCADE, related_name="throws")
    team = ForeignKey(TeamsInSeason, on_delete=models.CASCADE, related_name="all_throws")
    throw_round = IntegerField(db_index=True)
    throw_turn = IntegerField(db_index=True)
    score_first = CharField(max_length=2, null=True, blank=True)
    score_second = CharField(max_length=2, null=True, blank=True)
    score_third = CharField(max_length=2, null=True, blank=True)
    score_fourth = CharField(max_length=2, null=True, blank=True)

    def __init__(self, *args, **kwargs) -> None:
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

class SeasonStats(Model):
    """Season Statistics for player with One-to-one relationship. This is summary model and should 
    sum of all `PositionStats` instances that have this key. `PositionStats` should be created only 
    when it's needed to avoid reduntant zero rows.
    """
    player = OneToOneField(PlayersInTeam, primary_key=True, on_delete=models.CASCADE)
    periods = IntegerField(default=0)
    kyykat = IntegerField(default=0)
    throws = IntegerField(default=0)
    pikes = IntegerField(default=0)
    zeros = IntegerField(default=0)
    ones = IntegerField(default=0)
    twos = IntegerField(default=0)
    threes = IntegerField(default=0)
    fours = IntegerField(default=0)
    fives = IntegerField(default=0)
    gte_six = IntegerField(default=0)
    scaled_points = IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Seasons Stats'

    def __str__(self):
        return (
            f"{self.player.player.first_name} "
            f"{self.player.player.last_name} "
            f"{self.player.team_in_season.division.season.year} "
            f"{self.player.team_in_season.abbreviation}"
        )

class PositionStats(Model):
    """Position spesific statistics. Only if player has played in the position, only then should
    a dataclass of this be created. This is to avoid reduntant zero rows. This data should be 
    updated when saving `Throws` class. 
    """
    seasons_stats = ForeignKey(SeasonStats, on_delete=models.CASCADE)
    position = IntegerField(default=1)
    periods = IntegerField(default=0)
    kyykat = IntegerField(default=0)
    throws = IntegerField(default=0)
    pikes = IntegerField(default=0)
    zeros = IntegerField(default=0)
    ones = IntegerField(default=0)
    twos = IntegerField(default=0)
    threes = IntegerField(default=0)
    fours = IntegerField(default=0)
    fives = IntegerField(default=0)
    gte_six = IntegerField(default=0)
    scaled_points = IntegerField(default=0)

    def __str__(self):
        return (
            f"{self.seasons_stats.player.player.first_name} "
            f"{self.seasons_stats.player.player.last_name} "
            f"{self.seasons_stats.player.team_season.season.year} "
            f"{self.seasons_stats.player.team_season.current_abbreviation} {self.position}"
        )
    class Meta:
        verbose_name_plural = 'Positions Stats'


class Seriers(Model):
    """Connects different `Match` instances to e.g. one playoff seriers. Matches should be carefully
    dated so that the order of the matches is conserved.

    Creates automatically the matches that are at least needed to win the seriers (`matches_to_win`)
    The match is missing the dates and field data. In the case where these are templated to the website
    and no actual teams are known, change to the fields `team_A` or `team_B` shall change the matches
    teams automatically IF the field was empty before.
    
    """
    division = ForeignKey(Division, blank=False, null=False, on_delete=models.CASCADE)
    team_A = ForeignKey(TeamsInSeason, null=True, on_delete=models.CASCADE, related_name="A_teams")
    team_B = ForeignKey(TeamsInSeason, null=True, on_delete=models.CASCADE, related_name="B_teams")
    winner = ForeignKey(TeamsInSeason, null=True, on_delete=models.CASCADE, related_name="winner")
    seriers_type = IntegerField(blank=True, null=True, choices=MATCH_TYPES)
    matches_to_win = IntegerField(blank=False, default=2)

    def __init__(self, *args, **kwargs) -> None:
        super(Seriers, self).__init__(*args, **kwargs)
        self.__original_team_A = None
        self.__original_team_B = None

    def save(self, **kwargs):
        if self._state.adding is True:
            post_season = self.seriers_type not in [1, 10, 20]
            Match.objects.bulk_create(
                [
                    Match(
                        division=self.division,
                        seriers=self,
                        time="",
                        home_team=self.team_A if i % 2 else self.team_B,
                        away_team=self.team_B if i % 2 else self.team_A, 
                        post_season=post_season,
                        match_type=self.seriers_type,
                    ) for i in range(1, self.matches_to_win+1)
                ]
            )
        else:
            matches: t.Iterable[Match] = self.matches.all().order_by("pk")
            if self.__original_team_A is None and self.team_A is not None:
                for i, match in enumerate(matches, 1):
                    if i % 2:
                        match.home_team = self.team_A
                    else:
                        match.away_team = self.team_A

            if self.__original_team_B is None and self.team_B is not None:
                for i, match in enumerate(matches, 1):
                    if i % 2:
                        match.home_team = self.team_B
                    else:
                        match.away_team = self.team_B

        super().save(**kwargs)

    class Meta:
        constraints = [
            CheckConstraint(condition=~Q(team_A=F("team_B")), name="seriers_not_same_team"),
            CheckConstraint(condition=Q(matches_to_win__gte=1), name="to_win_gte_1"),
        ]

class TeamsInSuperWeekend(Model):
    """One-to-one field to reduce reduntant null columns in `TeamsInSeason` -table. Includes
    SuperWeekend format related information.
    """
    teams_in_season = OneToOneField(TeamsInSeason, primary_key=True, on_delete=models.CASCADE)
    super_weekend_bracket = IntegerField(blank=True, null=True)
    super_weekend_bracket_placement = IntegerField(blank=True, null=True)
    super_weekend_playoff_seed = IntegerField(blank=True, null=True)

    def __str__(self):
        return (
            f"{self.teams_in_season.division.season.year} "
            f"{self.teams_in_season.abbreviation} "
            f"Lohko: {self.super_weekend_bracket}"
        )
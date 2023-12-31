from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.cache import cache

from utils.caching import reset_player_cache


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    number = models.CharField(max_length=2, default=99)


class Team(models.Model):
    name = models.CharField(max_length=128, unique=True)
    abbreviation = models.CharField(max_length=15)

    def __str__(self):
        return '%s' % (self.abbreviation)

class Season(models.Model):
    year = models.CharField(max_length=4, unique=True)
    no_brackets = models.IntegerField(default=1, blank=False)

    def __str__(self):
        return f'Kausi {self.year}'

class CurrentSeason(models.Model):
    season = models.OneToOneField(Season, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Current Season'

    def __str__(self):
        return 'Season %s' % (self.season.year)

class TeamsInSeason(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    current_name =  models.CharField(max_length=128)
    current_abbreviation = models.CharField(max_length=15)
    players = models.ManyToManyField(User, through='PlayersInTeam')
    bracket = models.IntegerField(null=True)
    
    class Meta:
        unique_together = ('season', 'team')

    def __str__(self):
        return f'{self.current_abbreviation} {self.season.year}'

class PlayersInTeam(models.Model):
    team_season = models.ForeignKey(TeamsInSeason, on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_captain = models.BooleanField(default=False)

    class Meta:
        unique_together = ('player', 'team_season')
        # Make sure are players allowed to change team during the season?

    def __str__(self):
        return '%s %s %s %s' % (self.team_season.season.year, self.team_season.current_abbreviation, self.player.first_name, self.player.last_name)


class Match(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    match_time = models.DateTimeField()
    field = models.IntegerField(blank=True, null=True)
    home_first_round_score = models.IntegerField(blank=True, null=True)
    home_second_round_score = models.IntegerField(blank=True, null=True)
    away_first_round_score = models.IntegerField(blank=True, null=True)
    away_second_round_score = models.IntegerField(blank=True, null=True)
    home_team = models.ForeignKey(TeamsInSeason, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(TeamsInSeason, on_delete=models.CASCADE, related_name='away_matches')
    is_validated = models.BooleanField(default=False)
    post_season = models.BooleanField(default=False)
    match_type = models.IntegerField(blank=True, null=True)
    seriers = models.IntegerField(null=True, default=1)

    class Meta:
        verbose_name_plural = 'Matches'

    def __str__(self):
        return '%s | %s - %s' % (self.match_time.strftime("%m/%d/%Y, %H:%M"), self.home_team, self.away_team,)


class Throw(models.Model):
    '''
    throw_round determines is it first(1) or second(2) round of the match.
    throw_turn determines players' throwing turn: 1, 2, 3 or 4.
    throw_number determines is it players' 1st, 2nd, 3rd or 4th throw.
    '''
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    team = models.ForeignKey(TeamsInSeason, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    throw_round = models.IntegerField()
    throw_turn = models.IntegerField()
    score_first = models.CharField(max_length=2, null=True, blank=True, db_index=True)
    score_second = models.CharField(max_length=2, null=True, blank=True, db_index=True)
    score_third = models.CharField(max_length=2, null=True, blank=True, db_index=True)
    score_fourth = models.CharField(max_length=2, null=True, blank=True, db_index=True)


class News(models.Model):
    header = models.TextField()
    date = models.DateTimeField()
    text = models.TextField()


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
                        throw_round=r
                    )

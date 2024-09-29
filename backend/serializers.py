from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from backend.models import (
    SuperWeekend, 
    Team, 
    Season, 
    PlayersInTeam, 
    Match, 
    Throw, 
    CurrentSeason, 
    TeamsInSeason, 
    News,
    SeasonStats,
    PositionStats,
)
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.models import Count, Sum, F, Q, IntegerField
from django.db import IntegrityError
from django.db.models.functions import Cast, Substr

from utils.caching import getFromCache, setToCache


def required(value):
    if value is None:
        raise serializers.ValidationError('This field is required')
    
def format_scores(scores:list):
    return_list = []
    number_of_zeros = 0
    h = 0
    for score in scores:
        if score is None: continue
        elif score == "h" or score == "e" : continue
        elif ord(score[0]) != 8722: continue # ascii 8722 is minus sign
        else:
            number_of_zeros +=1
            tmp = int(score[1:]) * -1
            h = abs(tmp)
    text = f"h{h}0{number_of_zeros-h}"
    for score in scores:
        if score is None: return_list.append(score)
        elif score == "h" or score == "e": return_list.append(score)
        elif ord(score[0]) != 8722: return_list.append(score)
        else: return_list.append(text)
    return return_list


def count_throw_results(obj, season, result, throws=None, key="player"):
    key = f'{key}_{str(obj.id)}_{str(result)}_total'
    result_total = getFromCache(key, season.year)
    if result_total is None:
        throws = Throw.objects.filter(match__is_validated=True, season=season, player=obj) if throws is None else throws
        result_total = throws.annotate(
            count = Count('pk', filter=Q(score_first=result)) + 
                    Count('pk', filter=Q(score_second=result)) +
                    Count('pk', filter=Q(score_third=result)) + 
                    Count('pk', filter=Q(score_fourth=result))
        ).aggregate(Sum('count'))['count__sum']
        if result_total is None:
            result_total = 0
        setToCache(key, result_total, season_year=season.year)
    return result_total

def count_gte_six_throw_results(obj, season, throws=None, key="player"):
    key = f'{key}_{str(obj.id)}_gteSix_total'
    result_total = getFromCache(key, season.year)
    if result_total is None:
        throws = Throw.objects.filter(match__is_validated=True, season=season, player=obj) if throws is None else throws
        result_total = throws.annotate(
                st = Cast("score_first", output_field=IntegerField()),
                nd = Cast("score_second", output_field=IntegerField()),
                rd = Cast("score_third", output_field=IntegerField()),
                th = Cast("score_fourth", output_field=IntegerField()),
            ).annotate(
            count = Count('pk', filter=Q(st__gte=6)) + 
                    Count('pk', filter=Q(nd__gte=6)) +
                    Count('pk', filter=Q(rd__gte=6)) + 
                    Count('pk', filter=Q(th__gte=6))
        ).aggregate(Sum('count'))['count__sum']
        if result_total is None:
            result_total = 0
        setToCache(key, result_total, season_year=season.year)
    return result_total

def count_score_total(obj, season, throws, key='player'):
    key = f'{key}_{str(obj.id)}_score_total'
    score_total = getFromCache(key, season.year)
    if score_total is None:
        score_total = throws.annotate(
            st = Cast("score_first", output_field=IntegerField()),
            nd = Cast("score_second", output_field=IntegerField()),
            rd = Cast("score_third", output_field=IntegerField()),
            th = Cast("score_fourth", output_field=IntegerField()),
        ).annotate(
            score= F('st') + F('nd') + F('rd') + F('th')
        ).aggregate(Sum('score'))['score__sum']
        if score_total is None:
            score_total = 0
        #setToCache(key, score_total, season_year=season.year)
    return score_total

class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(validators=[required], max_length=30)
    last_name = serializers.CharField(validators=[required], max_length=150)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data['username'],
                                        validated_data['password'])
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.save()
        msg = ""
        return True, msg, user


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField() # .EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")



class SharedPlayerInTeamSerializer(serializers.ModelSerializer):
    def get_player_name(self, obj: PlayersInTeam):
        return f"{obj.player.first_name} {obj.player.last_name}"
    
    def get_team(self, obj: PlayersInTeam):
        return TeamSerializer(obj.team_season).data

    def get_season_statistics(self, obj: PlayersInTeam):
        season_stats = SeasonStats.objects.get(player=obj)
        return SeasonStatsSerializer(season_stats).data
    class Meta:
        model = PlayersInTeam

class SharedPlayerSerializer(serializers.ModelSerializer):
    def get_player_name(self, obj):
        return obj.first_name + " " + obj.last_name

    def get_team(self, obj):
        try:
            season = self.context.get('season')
            t = TeamsInSeason.objects.filter(season=season, playersinteam__player=obj).first()
            team = TeamSerializer(t).data
        except TeamsInSeason.DoesNotExist:
            team = None
        return team
    class Meta:
        model = User


class UserSerializer(SharedPlayerSerializer):
    player_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'player_name')


class ReserveListSerializer(SharedPlayerSerializer):
    player_name = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'player_name', 'team')


# TODO Figure a proper way to validate Unique Together between season and player
class ReserveCreateSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(validators=[required], queryset=User.objects.all())
    # season = serializers.SerializerMethodField()
    #
    # def get_season(self):
    #     return CurrentSeason.objects.first().season

    class Meta:
        model = PlayersInTeam
        fields = ('id', 'player')
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=PlayersInTeam.objects.all(),
        #         fields=["season", "player"]
        #     )
        # ]

    def create(self, validated_data):
        user = self.context.get("request").user
        add_player = validated_data['player']
        season = CurrentSeason.objects.first().season
        try:
            team = user.teamsinseason_set.get(season=season)
            PlayersInTeam.objects.create(team_season=team, player=add_player)
        except IntegrityError:
            print('reserve duplicate', user.id, add_player)
            return False, "DUPLICATE"
        except Team.DoesNotExist:
            print('reserve team 404', user.id, add_player)
            return False, "USER_TEAM_404"
        return True, ""


class SimplePlayerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    player_name = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    season_statistics = serializers.SerializerMethodField()

    def get_id(self, obj: PlayersInTeam):
        return obj.player.id

    def get_player_name(self, obj: PlayersInTeam):
        return f"{obj.player.first_name} {obj.player.last_name}"
    
    def get_team(self, obj: PlayersInTeam):
        return TeamNameSerializer(obj.team_season).data

    def get_season_statistics(self, obj: PlayersInTeam):
        season_stats = SeasonStats.objects.get(player=obj)
        return SimpleSeasonStatsSerializer(season_stats).data
    class Meta:
        model = PlayersInTeam
        exclude = 'is_captain', 'team_season', 'player'

class PlayerSerializer(SharedPlayerInTeamSerializer):
    team = serializers.SerializerMethodField()
    player_name = serializers.SerializerMethodField()
    season_statistics = serializers.SerializerMethodField()

    class Meta:
        model = PlayersInTeam
        exclude = ('team_season',)

class PlayerAllDetailSerializer(SharedPlayerSerializer):
    stats_per_seasons = serializers.SerializerMethodField() # Order matters here to make 'self' attributes
    season = serializers.SerializerMethodField()
    season_count = serializers.SerializerMethodField()
    player_name = serializers.SerializerMethodField()
    all_score_total = serializers.SerializerMethodField()
    all_match_count = serializers.SerializerMethodField()
    all_rounds_total = serializers.SerializerMethodField()
    all_pikes_total = serializers.SerializerMethodField()
    all_zeros_total = serializers.SerializerMethodField()
    all_ones_total = serializers.SerializerMethodField()
    all_twos_total = serializers.SerializerMethodField()
    all_threes_total = serializers.SerializerMethodField()
    all_fours_total = serializers.SerializerMethodField()
    all_fives_total = serializers.SerializerMethodField()
    all_throws_total = serializers.SerializerMethodField()
    all_gteSix_total = serializers.SerializerMethodField()
    total_zero_percentage = serializers.SerializerMethodField()
    total_pike_percentage = serializers.SerializerMethodField()
    total_average_throw = serializers.SerializerMethodField()
    total_average_throw_turn = serializers.SerializerMethodField()

    def get_stats_per_seasons(self, obj):
        players_teams_per_season = PlayersInTeam.objects.filter(player=obj)
        self.stats_per_seasons = PlayerSerializer(players_teams_per_season, many=True).data
        # print(self.stats_per_seasons)
        return self.stats_per_seasons
    
    def get_all_score_total(self, obj):
        self.score_total = sum([s["season_statistics"]["kyykat"] for s in self.stats_per_seasons])
        return self.score_total
    
    def get_all_match_count(self, obj):
        return sum([s["season_statistics"]["match_count"] for s in self.stats_per_seasons])

    def get_all_rounds_total(self, obj):
        return sum([s["season_statistics"]["periods"] for s in self.stats_per_seasons])

    def get_all_pikes_total(self, obj):
        self.pikes = sum([s["season_statistics"]["pikes"] for s in self.stats_per_seasons])
        return self.pikes

    def get_all_zeros_total(self, obj):
        self.zeros = sum([s["season_statistics"]["zeros"] for s in self.stats_per_seasons])
        return self.zeros
    
    def get_all_ones_total(self, obj):
        return sum([s["season_statistics"]["ones"] for s in self.stats_per_seasons])
    
    def get_all_twos_total(self, obj):
        return sum([s["season_statistics"]["twos"] for s in self.stats_per_seasons])

    def get_all_threes_total(self, obj):
        return sum([s["season_statistics"]["threes"] for s in self.stats_per_seasons])
    
    def get_all_fours_total(self, obj):
        return sum([s["season_statistics"]["fours"] for s in self.stats_per_seasons])

    def get_all_fives_total(self, obj):
        return sum([s["season_statistics"]["fives"] for s in self.stats_per_seasons])

    def get_all_throws_total(self, obj):
        self.throws = sum([s["season_statistics"]["throws"] for s in self.stats_per_seasons])
        return self.throws
    
    def get_all_gteSix_total(self, obj):
        return sum([s["season_statistics"]["gte_six"] for s in self.stats_per_seasons])
    
    def get_total_zero_percentage(self, obj):
        if self.throws == 0:
            return 0
        return round((self.zeros / self.throws) * 100, 2)
    
    def get_total_pike_percentage(self, obj):
        if self.throws == 0:
            return 0
        return round((self.pikes / self.throws) * 100, 2)

    def get_total_average_throw(self, obj):
        if self.throws == 0:
            return 0
        return round((self.score_total / self.throws), 2)
    
    def get_total_average_throw_turn(self,obj):
        if self.throws == 0:
            return 0
        return round(sum([s["season_statistics"]["throws"] * s["season_statistics"]["avg_throw_turn"] for s in self.stats_per_seasons]) / self.throws ,2)
    
    def get_season(self, obj):
        return "All-Time"

    def get_season_count(self, obj):
        return len(self.stats_per_seasons)

    class Meta:
        model = User
        exclude = 'password', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions'


class UserMatchSerializer(serializers.ModelSerializer):
    opponent_name = serializers.SerializerMethodField()
    opponent_score = serializers.SerializerMethodField()
    own_score = serializers.SerializerMethodField()
    score_first = serializers.SerializerMethodField()
    score_second = serializers.SerializerMethodField()
    score_third = serializers.SerializerMethodField()
    score_fourth = serializers.SerializerMethodField()
    score_fifth = serializers.SerializerMethodField()
    score_sixth = serializers.SerializerMethodField()
    score_seventh = serializers.SerializerMethodField()
    score_eighth = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()
    score_average_round_one = serializers.SerializerMethodField()
    score_average_round_two = serializers.SerializerMethodField()
    score_average_match = serializers.SerializerMethodField()
    opponent_score_first = serializers.SerializerMethodField()
    opponent_score_second = serializers.SerializerMethodField()
    own_score_first = serializers.SerializerMethodField()
    own_score_second = serializers.SerializerMethodField()
    throw_turn_one = serializers.SerializerMethodField()
    throw_turn_two = serializers.SerializerMethodField()
    score_total_one = serializers.SerializerMethodField()
    score_total_two = serializers.SerializerMethodField()

    # We define almost everything in here. This works only if the dependent fields are
    # defined after the 'score_total' field in the Meta class
    def get_score_total(self, obj):
        user = self.context.get('user_id')
        rounds = obj.throw_set.filter(player=user)
        round_one_no_throws, round_two_no_throws = 0, 0
        self.player_first = '-'
        self.player_second = '-'
        self.player_third = '-'
        self.player_fourth = '-'
        self.player_fifth = '-'
        self.player_sixth = '-'
        self.player_seventh = '-'
        self.player_eighth = '-'
        self.round_one_total = 0
        self.round_two_total = 0
        self.throw_average_one = 0
        self.throw_average_two = 0
        self.throw_turn_one = '-'
        self.throw_turn_two = '-'
        for r in rounds:
            st = int(r.score_first) if r.score_first is not None and r.score_first.isnumeric() else 0
            nd = int(r.score_second) if r.score_second is not None and r.score_second.isnumeric() else 0
            rd = int(r.score_third) if r.score_third is not None and r.score_third.isnumeric() else 0
            th = int(r.score_fourth) if r.score_fourth is not None and r.score_fourth.isnumeric() else 0
            no_throws = (r.score_first == 'e') + (r.score_second == 'e') 
            + (r.score_third == 'e') + (r.score_fourth == 'e')

            scores = format_scores([r.score_first, r.score_second, r.score_third, r.score_fourth])
            if r.throw_round == 1:
                self.player_first = scores[0]
                self.player_second = scores[1]
                self.player_third = scores[2]
                self.player_fourth = scores[3]
                self.round_one_total = st + nd + rd + th
                self.throw_turn_one = r.throw_turn
                round_one_no_throws = no_throws
                self.throw_average_one = round(self.round_one_total / (4- round_one_no_throws),2)
            else:
                self.player_fifth = scores[0]
                self.player_sixth = scores[1]
                self.player_seventh = scores[2]
                self.player_eighth = scores[3]
                self.round_two_total = st + nd + rd + th
                self.throw_turn_two = r.throw_turn
                round_two_no_throws = no_throws
                self.throw_average_two = round(self.round_two_total / (4- round_two_no_throws),2)
        score_total = self.round_one_total + self.round_two_total
        number_of_throws = 8 if type(self.throw_turn_one) is int and type(self.throw_turn_two) is int else 4
        self.throw_average_match = round(score_total / (number_of_throws - round_one_no_throws - round_two_no_throws),2)
        return score_total

    def get_opponent_name(self, obj):
        def inner_get_team(obj_team):
            key = 'team_' + str(obj_team.id)
            team = getFromCache(key)
            if team is None:
                team = TeamSerializer(obj_team).data
                setToCache(key, team, 3600)
            return team

        home_team = inner_get_team(obj.home_team)
        away_team = inner_get_team(obj.away_team)

        opponent_team = None
        if self.context.get('user_id') in home_team['players']:
            opponent_team = away_team['current_abbreviation']
            self.opp_score_first = int(obj.away_first_round_score)
            self.opp_score_second = int(obj.away_second_round_score)
            self.own_score_first = int(obj.home_first_round_score)
            self.own_score_second = int(obj.home_second_round_score)
        elif self.context.get('user_id') in away_team['players']:
            opponent_team = home_team['current_abbreviation']
            self.opp_score_first = int(obj.home_first_round_score)
            self.opp_score_second = int(obj.home_second_round_score)
            self.own_score_first = int(obj.away_first_round_score)
            self.own_score_second = int(obj.away_second_round_score)
        else:
            print("jotain meni vikaan etsiessä vastustaja joukkueen nimeä")

        return opponent_team

    def get_opponent_score(self, obj):
        return self.opp_score_first + self.opp_score_second
    
    def get_own_score(self, obj):
        return self.own_score_first + self.own_score_second
    
    def get_opponent_score_first(self, obj):
        return self.opp_score_first
    
    def get_own_score_first(self, obj):
        return self.own_score_first
    
    def get_opponent_score_second(self, obj):
        return self.opp_score_second
    
    def get_own_score_second(self, obj):
        return self.own_score_second

    def get_score_first(self, obj):
        return self.player_first

    def get_score_second(self, obj):
        return self.player_second

    def get_score_third(self, obj):
        return self.player_third

    def get_score_fourth(self, obj):
        return self.player_fourth

    def get_score_fifth(self, obj):
        return self.player_fifth

    def get_score_sixth(self, obj):
        return self.player_sixth

    def get_score_seventh(self, obj):
        return self.player_seventh

    def get_score_eighth(self, obj):
        return self.player_eighth
    
    def get_score_average_round_one(self, obj):
        return self.throw_average_one
    
    def get_score_average_round_two(self, obj):
        return self.throw_average_two
    
    def get_score_average_match(self, obj):
        return self.throw_average_match
    
    def get_throw_turn_one(self, obj):
        return self.throw_turn_one
    
    def get_throw_turn_two(self, obj):
        return self.throw_turn_two

    def get_score_total_one(self, obj):
        return self.round_one_total
    
    def get_score_total_two(self, obj):
        return self.round_two_total
    class Meta:
        model = Match
        fields = ('id', 'match_time', 'home_team', 'away_team', 'opponent_name', 'score_total', 'opponent_score_first', 'own_score_first',
                  'opponent_score_second', 'own_score_second', "score_average_round_one", 'score_average_round_two',
                  'score_average_match', 'opponent_score', 'own_score', 'score_first', 'score_second', 
                  'score_third', 'score_fourth', 'score_fifth', 'score_sixth', 'score_seventh','score_eighth',
                  'throw_turn_one', 'throw_turn_two', 'score_total_one', 'score_total_two')

class PlayerNameSerializer(SharedPlayerSerializer):
    player_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'player_name')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamsInSeason
        fields = ('id', 'current_name', 'season', 'current_abbreviation', 'players', 'bracket')

class TeamNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamsInSeason
        fields = ('id', 'current_name', 'current_abbreviation',)

class SeasonSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return str(obj)

    def get_value(self, obj):
        return str(obj.id)

    class Meta:
        model = Season
        fields = ('id', 'name', 'value', 'no_brackets', 'playoff_format')


class TeamListSerializer(serializers.ModelSerializer):
    matches_won = serializers.SerializerMethodField()
    matches_lost = serializers.SerializerMethodField()
    matches_tie = serializers.SerializerMethodField()
    matches_played = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()
    points_total = serializers.SerializerMethodField()
    match_average = serializers.SerializerMethodField()
    points_average = serializers.SerializerMethodField()

    def count_match_results(self, obj):
        results_home =  obj.home_matches.filter(
            is_validated=True, 
            season=self.context.get('season'),
            match_type__lt=30                                        
        )
        results_away = obj.away_matches.filter(
            is_validated=True, 
            season=self.context.get('season'),
            match_type__lt=30
        )
        if self.context.get('post_season') is not None:
            results_home =  results_home.filter(post_season=self.context.get('post_season'))
            results_away = results_away.filter(post_season=self.context.get('post_season'))

        results_home = results_home.annotate(
                home=F('home_first_round_score') + F('home_second_round_score'),
                away=F('away_first_round_score') + F('away_second_round_score')
        )
        results_away = results_away.annotate(
                home=F('home_first_round_score') + F('home_second_round_score'),
                away=F('away_first_round_score') + F('away_second_round_score')
        )

        self.matches_won = results_home.filter(home__lt=F('away')).count() + results_away.filter(away__lt=F('home')).count()
        self.matches_lost = results_home.filter(away__lt=F('home')).count() + results_away.filter(home__lt=F('away')).count()
        self.matches_tie = results_home.filter(home__exact=F('away')).count() + results_away.filter(home__exact=F('away')).count()
        self.matches_played = self.matches_lost + self.matches_tie + self.matches_won

        match_score_home = results_home.aggregate(Sum('home'))['home__sum']
        match_score_away = results_away.aggregate(Sum('away'))['away__sum']
        if match_score_home is None and match_score_away is None:
            self.match_average = 'NaN'
            return
        elif match_score_home is None:
            match_score_home = 0
        elif match_score_away is None:
            match_score_away = 0
        match_score_total = match_score_home + match_score_away 
        self.match_average = round(match_score_total / self.matches_played , 2) if self.matches_played else 'NaN'

    def get_matches_played(self, obj):
        return self.matches_played
    
    def get_matches_won(self, obj):
        self.count_match_results(obj)
        return self.matches_won

    def get_matches_lost(self, obj):
        # Should be initialized in 'get_matches_won' - function
        return self.matches_lost

    def get_matches_tie(self, obj):
        # Should be initialized in 'get_matches_won' - function
        return self.matches_tie
    
    def get_points_total(self, obj):
        self.points_total = (self.matches_won * 2) + (self.matches_tie)
        return self.points_total
    
    def get_match_average(self, obj):
        return self.match_average
    
    def get_points_average(self, obj):
        return round(self.points_total / self.matches_played,2) if self.matches_played else "NaN"

    def get_score_total(self, obj):
        season = self.context.get('season')
        throws = Throw.objects.filter(match__is_validated=True, team=obj, season=season) 
        return count_score_total(obj, season, throws, key='team')

    class Meta:
        model = TeamsInSeason
        fields = ('id', 'current_name', 'current_abbreviation', 'matches_won', 'matches_lost', 'matches_tie',
                  'matches_played', 'match_average', 'points_total', 'points_average', 'score_total', 'bracket', 'bracket_placement')


class TeamDetailSerializer(serializers.ModelSerializer):
    score_total = serializers.SerializerMethodField()
    match_count = serializers.SerializerMethodField()
    pikes_total = serializers.SerializerMethodField()
    zeros_total = serializers.SerializerMethodField()
    zero_or_pike_first_throw_total = serializers.SerializerMethodField()
    throws_total = serializers.SerializerMethodField()
    gteSix_total = serializers.SerializerMethodField()
    pike_percentage = serializers.SerializerMethodField()
    zero_percentage = serializers.SerializerMethodField()
    match_average = serializers.SerializerMethodField()
    matches = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()

    def get_score_total(self, obj):
        throws = self.context.get('throws')
        self.score_total = count_score_total(obj, self.context.get('season'), throws)
        return self.score_total

    def get_match_count(self, obj):
        self.match_count = Match.objects.filter(is_validated=True, season=self.context.get('season'), throw__team=obj).distinct().count()
        return self.match_count

    def get_throws_total(self, obj):
        throws = self.context.get('throws')
        throw_rounds = throws.count()
        if throw_rounds is None:
            self.throws_total = 0
        else:
            throws_total = throw_rounds * 4
            no_throws = count_throw_results(obj, self.context.get('season'), 'e', throws=throws, key='team')
            self.throws_total = throws_total - no_throws
        return self.throws_total

    def get_pikes_total(self, obj):
        self.pikes_total = count_throw_results(obj, self.context.get('season'), 'h', throws=self.context.get('throws'), key='team')
        return self.pikes_total

    def get_zeros_total(self, obj):
        self.zeros_total = count_throw_results(obj, self.context.get('season'), 0, throws=self.context.get('throws'), key='team')
        return self.zeros_total

    def get_zero_or_pike_first_throw_total(self, obj):
        throws = self.context.get('throws')
        return throws.filter(Q(throw_turn=1) & (Q(score_first=0) | Q(score_first='h'))).count()

    def get_gteSix_total(self, obj):
        return count_gte_six_throw_results(obj, self.context.get('season'), throws=self.context.get('throws'), key='team')

    def get_pike_percentage(self, obj):
        try:
            pike_percentage = round((self.pikes_total / self.throws_total) * 100, 2)
        except (ZeroDivisionError, TypeError):
            pike_percentage = 0
        return pike_percentage

    def get_zero_percentage(self, obj):
        try:
            zero_percentage = round((self.zeros_total / self.throws_total) * 100, 2)
        except (ZeroDivisionError, TypeError):
            zero_percentage = 0
        return zero_percentage

    def get_match_average(self, obj):
        try:
            score_home = obj.home_matches.filter(is_validated=True, season=self.context.get('season')).annotate(
            score=F('home_first_round_score') + F('home_second_round_score') ).aggregate(Sum('score'))['score__sum']
            score_away = obj.away_matches.filter(is_validated=True, season=self.context.get('season')).annotate(
            score=F('away_first_round_score') + F('away_second_round_score') ).aggregate(Sum('score'))['score__sum']
            match_score_total = score_home + score_away
            match_average = round(match_score_total/ self.match_count, 2)
        except (ZeroDivisionError, TypeError):
            match_average = 0
        return match_average

    def get_matches(self, obj):
        matches = Match.objects.filter(Q(home_team=obj) | Q(away_team=obj), is_validated=True)
        return Match2ListSerializer(matches, many=True, context= {'team': obj}).data

    def get_players(self, obj: TeamsInSeason):
        players_in_team = PlayersInTeam.objects.filter(player__in=obj.players)
        return PlayerSerializer(players_in_team, many=True)

    class Meta:
        model = TeamsInSeason
        fields = ('id', 'current_name', 'current_abbreviation', 'score_total', 'match_count', 'pikes_total',
                  'zeros_total', 'zero_or_pike_first_throw_total', 'throws_total', 
                  'gteSix_total', 'pike_percentage', 'zero_percentage',
                  'match_average', 'matches', 'players')


class SharedMatchSerializer(serializers.ModelSerializer):
    def get_home_score_total(self, obj):
        key = 'match_' + str(obj.id) + '_home_score_total'
        home_score_total = getFromCache(key, self.context.get('season').year)
        if home_score_total is None:
            try:
                home_score_total = obj.home_first_round_score + obj.home_second_round_score
            except TypeError:
                home_score_total = None
            setToCache(key, home_score_total, season_year=self.context.get('season').year)
        return home_score_total

    def get_away_score_total(self, obj):
        key = 'match_' + str(obj.id) + '_away_score_total'
        away_score_total = getFromCache(key, self.context.get('season').year)
        if away_score_total is None:
            try:
                away_score_total = obj.away_first_round_score + obj.away_second_round_score
            except TypeError:
                away_score_total = None
            setToCache(key, away_score_total, season_year=self.context.get('season').year)
        return away_score_total


class MatchListSerializer(SharedMatchSerializer):
    home_score_total = serializers.SerializerMethodField()
    away_score_total = serializers.SerializerMethodField()
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()

    def get_home_team(self, obj):
        key = 'team_' + str(obj.home_team.id)
        team = getFromCache(key)
        if team is None:
            team = TeamSerializer(obj.home_team).data
            setToCache(key, team, 3600)
        return team

    def get_away_team(self, obj):
        key = 'team_' + str(obj.away_team.id)
        team = getFromCache(key)
        if team is None:
            team = TeamSerializer(obj.away_team).data
            setToCache(key, team, 3600)
        return team

    class Meta:
        model = Match
        fields = ('id', 'match_time', 'field', 'home_team', 'away_team', 'home_score_total', 'away_score_total',
                  'post_season',  'is_validated', 'match_type', 'seriers')
        
class Match2ListSerializer(serializers.ModelSerializer):
    own_first = serializers.SerializerMethodField()
    own_second = serializers.SerializerMethodField()
    opp_first = serializers.SerializerMethodField()
    opp_second = serializers.SerializerMethodField()
    own_team_total = serializers.SerializerMethodField()
    opposite_team_total = serializers.SerializerMethodField()
    opposite_team = serializers.SerializerMethodField()
    match_type = serializers.SerializerMethodField()

    def get_opposite_team(self, obj):
        self.own_team = (obj.home_team == self.context.get('team')) # Home Team = 1, Away Team = 0
        key = 'team_' + str(obj.away_team.id) if self.own_team else 'team_' + str(obj.home_team.id)
        team = getFromCache(key)
        if team is None:
            team = TeamSerializer(obj.away_team).data if self.own_team else TeamSerializer(obj.home_team).data
            setToCache(key, team, 3600)
        return team['current_abbreviation']
    
    def get_own_team_total(self, obj):
        key = 'match_' + str(obj.id) + '_own_score_total'
        own_score_total = getFromCache(key)
        if own_score_total is None:
            try:
                if self.own_team:
                    own_score_total = obj.home_first_round_score + obj.home_second_round_score
                else:
                    own_score_total = obj.away_first_round_score + obj.away_second_round_score
            except TypeError:
                own_score_total = None
            setToCache(key, own_score_total)
        return own_score_total

    def get_opposite_team_total(self, obj):
        key = 'match_' + str(obj.id) + '_opposite_score_total'
        opp_score_total = getFromCache(key)
        if opp_score_total is None:
            try:
                if self.own_team:
                    opp_score_total = obj.away_first_round_score + obj.away_second_round_score
                else:
                    opp_score_total = obj.home_first_round_score + obj.home_second_round_score
            except TypeError:
                opp_score_total = None
            setToCache(key, opp_score_total)
        return opp_score_total
    
    def get_match_type(self, obj):
        game = {
            1 : "Runkosarja",
            2 : "Finaali",
            3 : "Pronssi",
            4 : "Välierä",
            5 : "Puolivälierä",
            6 : "Neljännesvälierä",
            7 : "Kahdeksannesvälierä",
            10 : "Runkosarjafinaali",
            20 : "Jumbofinaali",
            31: "SuperWeekend: Alkulohko",
            32: "SuperWeekend: Finaali",
            33: "SuperWeekend: Pronssi",
            34: "SuperWeekend: Välierä",
            35: "SuperWeekend: Puolivälierä",
            36: "SuperWeekend: Neljännesvälierä",
            37: "SuperWeekend: Kahdeksannesvälierä",
        }
        try:
            return game[obj.match_type] if obj.match_type is not None else ''
        except:
            print(obj.match_type)
    
    def get_own_first(self, obj):
        return obj.home_first_round_score if self.own_team else obj.away_first_round_score
    def get_own_second(self, obj):
        return obj.home_second_round_score if self.own_team else obj.away_second_round_score
    def get_opp_first(self, obj):
        return obj.home_first_round_score if not self.own_team else obj.away_first_round_score
    def get_opp_second(self, obj):
        return obj.home_second_round_score if not self.own_team else obj.away_second_round_score
    
    class Meta:
        model = Match
        fields = ('id', 'match_time', 'opposite_team', 'away_team', 'opposite_team_total', 'own_team_total',
                  'post_season',  'is_validated', 'match_type', 'seriers', 'own_first', 'own_second', 
                  'opp_first', 'opp_second')

class MatchDetailSerializer(SharedMatchSerializer):
    home_score_total = serializers.SerializerMethodField()
    away_score_total = serializers.SerializerMethodField()
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()
    first_round = serializers.SerializerMethodField()
    second_round = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()

    def get_first_round(self, obj: Match):
        return MatchRoundSerializer(obj.throw_set.filter(throw_round=1),
                                    context={'home_team': obj.home_team, 'away_team': obj.away_team}).data
    
    def get_second_round(self, obj: Match):
        return MatchRoundSerializer(obj.throw_set.filter(throw_round=2),
                                    context={'home_team': obj.home_team, 'away_team': obj.away_team}).data

    def get_home_team(self, obj: Match):
        return MatchTeamSerializer(obj.home_team).data

    def get_away_team(self, obj: Match):
        return MatchTeamSerializer(obj.away_team).data
    
    def get_type_name(self, obj: Match):
        game = {
            1 : "Runkosarja",
            2 : "Finaali",
            3 : "Pronssi",
            4 : "Välierä",
            5 : "Puolivälierä",
            6 : "Neljännesvälierä",
            7 : "Kahdeksannesvälierä",
            10 : "Runkosarjafinaali",
            20 : "Jumbofinaali",
            31: "SuperWeekend: Alkulohkopeli",
            32: "SuperWeekend: Finaali",
            33: "SuperWeekend: Pronssi",
            34: "SuperWeekend: Välierä",
            35: "SuperWeekend: Puolivälierä",
            36: "SuperWeekend: Neljännesvälierä",
            37: "SuperWeekend: Kahdeksannesvälierä",
        }
        try:
            return game[obj.match_type] if obj.match_type is not None else ''
        except:
            print(obj.match_type)
    class Meta:
        model = Match
        fields = (
            'id', 'match_time', 'field', 'home_score_total', 'away_score_total', 
            'home_first_round_score','home_second_round_score','away_first_round_score',
            'away_second_round_score', 'first_round', 'second_round', 'home_team',
            'away_team', 'is_validated', 'post_season', 'match_type', 'type_name', 'seriers')


class MatchTeamSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField()

    def get_players(self, obj: TeamsInSeason):
        return PlayerNameSerializer(obj.players, many=True).data
    class Meta:
        model = TeamsInSeason
        fields = ('id', 'current_name', 'current_abbreviation', 'players')


class MatchRoundSerializer(serializers.ModelSerializer):
    home = serializers.SerializerMethodField()
    away = serializers.SerializerMethodField()

    def get_home(self, qs):
        home_throws = qs.filter(team=self.context.get('home_team'))
        return ThrowScoreSerializer(home_throws, many=True).data

    def get_away(self, qs):
        away_throws = qs.filter(team=self.context.get('away_team'))
        return ThrowScoreSerializer(away_throws, many=True).data

    class Meta:
        model = Throw
        fields = ('home', 'away')


class MatchScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('home_first_round_score', 'home_second_round_score',
                  'away_first_round_score', 'away_second_round_score',
                  'is_validated')


class ThrowScoreSerializer(serializers.ModelSerializer):
    player = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()
    score_first = serializers.SerializerMethodField()
    score_second = serializers.SerializerMethodField()
    score_third = serializers.SerializerMethodField()
    score_fourth = serializers.SerializerMethodField()

    def get_player(self, obj):
        return UserSerializer(obj.player).data
    
    def get_score_first(self, obj: Throw):
        scores = format_scores([obj.score_first, obj.score_second, obj.score_third, obj.score_fourth])
        self.score_first, self.score_second, self.score_third, self.score_fourth = scores
        return self.score_first

    def get_score_second(self, obj: Throw):
        return self.score_second

    def get_score_third(self, obj: Throw):
        return self.score_third

    def get_score_fourth(self, obj: Throw):
        return self.score_fourth

    def get_score_total(self, obj: Throw):
        st = int(obj.score_first) if obj.score_first is not None and obj.score_first.isnumeric() else 0
        nd = int(obj.score_second) if obj.score_second is not None and obj.score_second.isnumeric() else 0
        rd = int(obj.score_third) if obj.score_third is not None and obj.score_third.isnumeric() else 0
        th = int(obj.score_fourth) if obj.score_fourth is not None and obj.score_fourth.isnumeric() else 0
        return st + nd + rd + th

    class Meta:
        model = Throw
        fields = ('id', 'player', 'score_first', 'score_second', 'score_third', 'score_fourth', 'score_total','throw_turn')


class ThrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Throw
        fields = ('score_first', 'score_second', 'score_third', 'score_fourth', 'player')

class TeamsInSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamsInSeason
        fields = ('id', 'bracket_placement', 'super_weekend_bracket', 'super_weekend_bracket_placement', 'super_weekend_playoff_seed')

class SuperWeekendSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperWeekend
        fields = ('id', 'season', 'winner', 'super_weekend_no_brackets', 'super_weekend_playoff_format')

class TeamListSuperWeekendSerializer(serializers.ModelSerializer):
    matches_won = serializers.SerializerMethodField()
    matches_lost = serializers.SerializerMethodField()
    matches_tie = serializers.SerializerMethodField()
    matches_played = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()
    points_total = serializers.SerializerMethodField()
    match_average = serializers.SerializerMethodField()

    def count_match_results(self, obj):
        results_home =  obj.home_matches.filter(is_validated=True, season=self.context.get('season'), match_type=31).annotate(
            home=F('home_first_round_score') + F('home_second_round_score'),
            away=F('away_first_round_score') + F('away_second_round_score'))
        results_away = obj.away_matches.filter(is_validated=True, season=self.context.get('season'), match_type=31).annotate(
            home=F('home_first_round_score') + F('home_second_round_score'),
            away=F('away_first_round_score') + F('away_second_round_score'))

        self.matches_won = results_home.filter(home__lt=F('away')).count() + results_away.filter(away__lt=F('home')).count()
        self.matches_lost = results_home.filter(away__lt=F('home')).count() + results_away.filter(home__lt=F('away')).count()
        self.matches_tie = results_home.filter(home__exact=F('away')).count() + results_away.filter(home__exact=F('away')).count()
        self.matches_played = self.matches_lost + self.matches_tie + self.matches_won

        match_score_home = results_home.aggregate(Sum('home'))['home__sum']
        match_score_away = results_away.aggregate(Sum('away'))['away__sum']
        if match_score_home is None and match_score_away is None:
            self.match_average = 'NaN'
            return
        elif match_score_home is None:
            match_score_home = 0
        elif match_score_away is None:
            match_score_away = 0
        match_score_total = match_score_home + match_score_away 
        self.match_average = round(match_score_total / self.matches_played , 2) if self.matches_played else 'NaN'

    def get_matches_played(self, obj):
        return self.matches_played
    
    def get_matches_won(self, obj):
        self.count_match_results(obj)
        return self.matches_won

    def get_matches_lost(self, obj):
        # Should be initialized in 'get_matches_won' - function
        return self.matches_lost

    def get_matches_tie(self, obj):
        # Should be initialized in 'get_matches_won' - function
        return self.matches_tie
    
    def get_points_total(self, obj):
        self.points_total = (self.matches_won * 2) + (self.matches_tie)
        return self.points_total
    
    def get_match_average(self, obj):
        return self.match_average
    
    def get_points_average(self, obj):
        return round(self.points_total / self.matches_played,2) if self.matches_played else "NaN"

    def get_score_total(self, obj):
        season = self.context.get('season')
        throws = Throw.objects.filter(match__is_validated=True, team=obj, season=season) 
        return count_score_total(obj, season, throws, key='team')

    class Meta:
        model = TeamsInSeason
        fields = ('id', 'current_name', 'current_abbreviation', 'matches_won', 'matches_lost', 
                  'matches_tie', 'matches_played','score_total', 'points_total', 'match_average', 
                  'super_weekend_bracket', 'super_weekend_bracket_placement', 'super_weekend_playoff_seed')
        
class AdminMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'

class SeasonStatsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField() 
    match_count = serializers.SerializerMethodField()
    pike_percentage = serializers.SerializerMethodField()
    zero_percentage = serializers.SerializerMethodField()
    score_per_throw = serializers.SerializerMethodField()
    avg_throw_turn = serializers.SerializerMethodField()
    avg_scaled_points = serializers.SerializerMethodField()
    average_score_position_one = serializers.SerializerMethodField()
    average_score_position_two = serializers.SerializerMethodField()
    average_score_position_three = serializers.SerializerMethodField()
    average_score_position_four = serializers.SerializerMethodField()
    matches = serializers.SerializerMethodField()
    season = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()

    def get_id(self, obj: SeasonStats):
        return int(obj.player.team_season.season.year)
    
    def get_match_count(self, obj: SeasonStats):
        user: User = obj.player.player
        season: Season = obj.player.team_season.season
        key = f'player_{str(user.id)}_match_count'
        match_count = getFromCache(key, season.year)
        if match_count is None:
            match_count = Match.objects.filter(season=season, throw__player=user).distinct().count()
            if match_count is None:
                match_count = 0
            setToCache(key, match_count, season_year=season.year)
        return match_count

    def get_pike_percentage(self, obj: SeasonStats):
        return round(obj.pikes / obj.throws * 100, 2) if obj.throws else 0

    def get_zero_percentage(self, obj: SeasonStats):
        return round(obj.zeros / obj.throws * 100, 2) if obj.throws else 0
    
    def get_score_per_throw(self, obj: SeasonStats):
        return round(obj.kyykat / obj.throws, 2) if obj.throws else 0

    def get_avg_throw_turn(self, obj: SeasonStats):
        if obj.throws == 0: # Catch zero division early
            return 0
        user: User = obj.player.player
        season: Season = obj.player.team_season.season
        key = f'player_{str(user.id)}_avg_throw_turn'
        avg_throw_turn = getFromCache(key, season.year)
        if avg_throw_turn is None:
            all_positions = PositionStats.objects.filter(seasons_stats=obj)
            total_sum = sum([pos.throws * pos.position for pos in all_positions])
            avg_throw_turn = round(total_sum / obj.throws, 2)
            setToCache(key, avg_throw_turn, season_year=season.year)
        return avg_throw_turn
    
    def get_avg_scaled_points(self, obj: SeasonStats):
        return round(obj.scaled_points / obj.throws, 2) if obj.throws else 0
    
    def get_average_score_position_one(self, obj: SeasonStats):
        pos = PositionStats.objects.get(seasons_stats__player=obj.player, position=1)
        return round(pos.kyykat / pos.throws, 2) if pos.throws else 0
    
    def get_average_score_position_two(self, obj: SeasonStats):
        pos = PositionStats.objects.get(seasons_stats__player=obj.player, position=2)
        return round(pos.kyykat / pos.throws, 2) if pos.throws else 0
    
    def get_average_score_position_three(self, obj: SeasonStats):
        pos = PositionStats.objects.get(seasons_stats__player=obj.player, position=3)
        return round(pos.kyykat / pos.throws, 2) if pos.throws else 0
    
    def get_average_score_position_four(self, obj: SeasonStats):
        pos = PositionStats.objects.get(seasons_stats__player=obj.player, position=4)
        return round(pos.kyykat / pos.throws, 2) if pos.throws else 0
    
    def get_season(self, obj: SeasonStats):
        return obj.player.team_season.season.year
    
    def get_team_name(self, obj: SeasonStats):
        return obj.player.team_season.current_abbreviation
    
    def get_matches(self, obj: SeasonStats):
        try:
            season: Season = obj.player.team_season.season
            user: User = obj.player.player
            throws = Match.objects.filter(throw__player=user, season=season, is_validated=True).distinct()
            matches = UserMatchSerializer(throws, many=True, context={'user_id': user.id, 'season' : season}).data
        except Match.DoesNotExist:
            matches = None
        return matches

    class Meta:
        model = SeasonStats
        fields = '__all__'


class SimpleSeasonStatsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField() 
    pike_percentage = serializers.SerializerMethodField()
    zero_percentage = serializers.SerializerMethodField()
    score_per_throw = serializers.SerializerMethodField()
    avg_throw_turn = serializers.SerializerMethodField()
    avg_scaled_points = serializers.SerializerMethodField()
    average_score_position_one = serializers.SerializerMethodField()
    average_score_position_two = serializers.SerializerMethodField()
    average_score_position_three = serializers.SerializerMethodField()
    average_score_position_four = serializers.SerializerMethodField()

    def get_id(self, obj: SeasonStats):
        return int(obj.player.team_season.season.year)

    def get_pike_percentage(self, obj: SeasonStats):
        return round(obj.pikes / obj.throws * 100, 2) if obj.throws else 0

    def get_zero_percentage(self, obj: SeasonStats):
        return round(obj.zeros / obj.throws * 100, 2) if obj.throws else 0
    
    def get_score_per_throw(self, obj: SeasonStats):
        return round(obj.kyykat / obj.throws, 2) if obj.throws else 0

    def get_avg_throw_turn(self, obj: SeasonStats):
        if obj.throws == 0: # Catch zero division early
            return 0
        user: User = obj.player.player
        season: Season = obj.player.team_season.season
        key = f'player_{str(user.id)}_avg_throw_turn'
        avg_throw_turn = getFromCache(key, season.year)
        if avg_throw_turn is None:
            all_positions = PositionStats.objects.filter(seasons_stats=obj)
            total_sum = sum([pos.throws * pos.position for pos in all_positions])
            avg_throw_turn = round(total_sum / obj.throws, 2)
            setToCache(key, avg_throw_turn, season_year=season.year)
        return avg_throw_turn
    
    def get_avg_scaled_points(self, obj: SeasonStats):
        return round(obj.scaled_points / obj.throws, 2) if obj.throws else 0
    
    def get_average_score_position_one(self, obj: SeasonStats):
        pos = PositionStats.objects.get(seasons_stats__player=obj.player, position=1)
        return round(pos.kyykat / pos.throws, 2) if pos.throws else 0
    
    def get_average_score_position_two(self, obj: SeasonStats):
        pos = PositionStats.objects.get(seasons_stats__player=obj.player, position=2)
        return round(pos.kyykat / pos.throws, 2) if pos.throws else 0
    
    def get_average_score_position_three(self, obj: SeasonStats):
        pos = PositionStats.objects.get(seasons_stats__player=obj.player, position=3)
        return round(pos.kyykat / pos.throws, 2) if pos.throws else 0
    
    def get_average_score_position_four(self, obj: SeasonStats):
        pos = PositionStats.objects.get(seasons_stats__player=obj.player, position=4)
        return round(pos.kyykat / pos.throws, 2) if pos.throws else 0

    class Meta:
        model = SeasonStats
        exclude = ('ones', 'twos', 'threes', 'fours', 'fives', 'player')
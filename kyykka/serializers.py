from rest_framework import serializers
from kyykka.models import Team, Season, PlayersInTeam, Match, Throw, CurrentSeason, Player
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.models import Avg, Count, Min, Sum, F, Q, Case, Value, When, IntegerField
from django.db import IntegrityError
from django.core.cache import cache


def required(value):
    if value is None:
        raise serializers.ValidationError('This field is required')

def getFromCache(key):
    # print("Get cache", key)
    return cache.get(key)

def setToCache(key, value, timeout=300):
    # print("Set cache", key)
    if value is None:
        value = 0
    cache.set(key, value, timeout)

class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.EmailField()
    first_name = serializers.CharField(validators=[required], max_length=30)
    last_name = serializers.CharField(validators=[required], max_length=150)
    number = serializers.CharField(validators=[required], max_length=2)

    class Meta:
        model = User
        fields = ('id', 'username', 'number', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        try:
            user = User.objects.create_user(validated_data['username'],
                                            validated_data['username'],
                                            validated_data['password'])
            user.first_name = validated_data['first_name']
            user.last_name = validated_data['last_name']
            user.save()
            Player.objects.create(user=user, number=validated_data['number'])
            msg = ""
            return True, msg
        except IntegrityError as e:
            return False, "Email is already taken"


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    # username = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")

class SharedPlayerSerializer(serializers.ModelSerializer):
    def get_player_name(self,obj):
        return obj.first_name + " " + obj.last_name

    def get_number(self, obj):
        try:
            return obj.player.number
        except:
            return None

    def get_score_total(self, obj):
        # return int(Throw.objects.filter(player=obj).annotate(score = F('score_first') + F('score_second')+ F('score_third')+ F('score_fourth')).aggregate(Sum('score'))['score__sum'])
        try:

            key = 'player_' + str(obj.id) + '_score_total'
            score_total = getFromCache(key)
            if score_total is None:
                score_total = Throw.objects.filter(player=obj, match__is_validated=True).annotate(
                    score = Case(
                        When(score_first__gt=0, then='score_first'),
                        default=Value('0'),
                        output_field=IntegerField(),
                    ) + Case(
                        When(score_second__gt=0, then='score_second'),
                        default=Value('0'),
                        output_field=IntegerField(),
                    ) + Case(
                        When(score_third__gt=0, then='score_third'),
                        default=Value('0'),
                        output_field=IntegerField(),
                    ) + Case(
                        When(score_fourth__gt=0, then='score_fourth'),
                        default=Value('0'),
                        output_field=IntegerField(),
                    )
                ).aggregate(Sum('score'))['score__sum']
                setToCache(key, score_total)
            # return int(Throw.objects.filter(season=self.context.get('season'), player=obj, score__gt=0).aggregate(Sum('score'))['score__sum'])
        except TypeError:
            setToCache(key, 0)
            return 0
        return score_total

    def get_match_count(self, obj):

        key = 'player_' + str(obj.id) + '_match_count'
        match_count = getFromCache(key)
        if match_count is None:
            match_count = Match.objects.filter(season=self.context.get('season'), throw__player=obj).distinct().count()
            setToCache(key, match_count)
        return match_count

    def get_rounds_total(self, obj):

        key = 'player_' + str(obj.id) + '_rounds_total'
        rounds_total = getFromCache(key)
        if rounds_total is None:
            rounds_total = obj.throw_set.count()
            setToCache(key, rounds_total)
        return rounds_total
        # return obj.throw_set.count() // 4

    def get_team(self, obj):
        try:
            team = TeamSerializer(obj.team_set.get(playersinteam__season=self.context.get('season'))).data
        except Team.DoesNotExist:
            team = None
        return team

    def get_pikes_total(self, obj):

        key = 'player_' + str(obj.id) + '_pikes_total'
        pikes_total = getFromCache(key)
        if pikes_total is None:
            pikes_total = Throw.objects.filter(season=self.context.get('season'), player=obj).annotate(count=Count('pk',filter=Q(score_first=-1)) + Count('pk',filter=Q(score_second=-1)) + Count('pk',filter=Q(score_third=-1)) + Count('pk',filter=Q(score_fourth=-1))).aggregate(Sum('count'))['count__sum']
            setToCache(key, pikes_total)
        # pikes = Throw.objects.filter(season=self.context.get('season'), player=obj).aggregate(first=Count('pk',filter=Q(score_first=-1)),second=Count('pk',filter=Q(score_second=-1)),third=Count('pk',filter=Q(score_third=-1)),fourth=Count('pk',filter=Q(score_fourth=-1)))
        # self.pikes = pikes['first'] + pikes['second'] + pikes['third'] + pikes['fourth']
        self.pikes = pikes_total
        return self.pikes

    def get_zeros_total(self, obj):

        key = 'player_' + str(obj.id) + '_zeros_total'
        zeros_total = getFromCache(key)
        if zeros_total is None:
            zeros_total = Throw.objects.filter(season=self.context.get('season'), player=obj).annotate(count=Count('pk',filter=Q(score_first=0)) + Count('pk',filter=Q(score_second=0)) + Count('pk',filter=Q(score_third=0)) + Count('pk',filter=Q(score_fourth=0))).aggregate(Sum('count'))['count__sum']
            setToCache(key, zeros_total)
        # zeros = Throw.objects.filter(season=self.context.get('season'), player=obj).aggregate(first=Count('pk',filter=Q(score_first=0)),second=Count('pk',filter=Q(score_second=0)),third=Count('pk',filter=Q(score_third=0)),fourth=Count('pk',filter=Q(score_fourth=0)))
        # self.zeros = zeros['first'] + zeros['second'] + zeros['third'] + zeros['fourth']
        self.zeros = zeros_total
        return self.zeros

    def get_gteSix_total(self, obj):

        key = 'player_' + str(obj.id) + '_gteSix_total'
        gteSix_total = getFromCache(key)
        if gteSix_total is None:
            gteSix_total = Throw.objects.filter(season=self.context.get('season'), player=obj).annotate(count=Count('pk',filter=Q(score_first__gte=6)) + Count('pk',filter=Q(score_second__gte=6)) + Count('pk',filter=Q(score_third__gte=6)) + Count('pk',filter=Q(score_fourth__gte=6))).aggregate(Sum('count'))['count__sum']
            if gteSix_total is None:
                setToCache(key, 0)
            else:
                setToCache(key, gteSix_total)
        # sixes = Throw.objects.filter(season=self.context.get('season'), player=obj).aggregate(first=Count('pk',filter=Q(score_first__gte=6)),second=Count('pk',filter=Q(score_second__gte=6)),third=Count('pk',filter=Q(score_third__gte=6)),fourth=Count('pk',filter=Q(score_fourth__gte=6)))
        # return sixes['first'] + sixes['second'] + sixes['third'] + sixes['fourth']
        return  gteSix_total

    def get_throws_total(self, obj):

        key = 'player_' + str(obj.id) + '_throws_total'
        throws_total = getFromCache(key)
        if throws_total is None:
            throws_total = Throw.objects.filter(season=self.context.get('season'), player=obj).count() * 4
            setToCache(key, throws_total)
        self.throws = throws_total
        return self.throws

    def get_pike_percentage(self, obj):

        key = 'player_' + str(obj.id) + '_pike_percentage'
        pike_percentage = getFromCache(key)
        if pike_percentage is None:
            pike_count = self.pikes
            total_count = self.throws
            try:
                pike_percentage = round((pike_count / total_count)*100, 2)
            except (ZeroDivisionError, TypeError):
                pike_percentage = 0
            setToCache(key, pike_percentage)
        return pike_percentage

    def get_score_per_throw(self, obj):
        return None

    def get_avg_throw_turn(self, obj):
        return None

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
    number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'number', 'player_name', 'team')

class ReserveCreateSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(validators=[required], queryset=User.objects.all())

    class Meta:
        model = PlayersInTeam
        fields = ('id', 'player')

    def create(self, validated_data):
        print(self.context.get("request").user)
        user = self.context.get("request").user
        add_player = validated_data['player']
        season = CurrentSeason.objects.first().season
        try:
            team = user.team_set.get(playersinteam__season=season)
            PlayersInTeam.objects.create(season=season, team=team, player=add_player)
        except IntegrityError:
            return False, "DUPLICATE"
        except Team.DoesNotExist:
            return False, "USER_TEAM_404"
        return True, ""


class PlayerListSerializer(SharedPlayerSerializer):
    team = serializers.SerializerMethodField()
    player_name = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()
    rounds_total = serializers.SerializerMethodField()
    pikes_total = serializers.SerializerMethodField()
    zeros_total = serializers.SerializerMethodField()
    gteSix_total = serializers.SerializerMethodField()
    throws_total = serializers.SerializerMethodField()
    pike_percentage = serializers.SerializerMethodField()
    score_per_throw = serializers.SerializerMethodField()
    avg_throw_turn = serializers.SerializerMethodField()
    scaled_points = serializers.SerializerMethodField()
    scaled_points_per_round = serializers.SerializerMethodField()
    def get_scaled_points(self, obj):
        return None
    def get_scaled_points_per_round(self, obj):
        return None
    class Meta:
        model = User
        fields = ('id', 'player_name', 'team', 'score_total', 'rounds_total',
                    'pikes_total', 'zeros_total', 'gteSix_total', 'throws_total', 'pike_percentage',
                    'score_per_throw', 'scaled_points', 'scaled_points_per_round', 'avg_throw_turn')

class PlayerDetailSerializer(SharedPlayerSerializer):
    team = serializers.SerializerMethodField()
    player_name = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()
    match_count = serializers.SerializerMethodField()
    rounds_total = serializers.SerializerMethodField()
    pikes_total = serializers.SerializerMethodField()
    zeros_total = serializers.SerializerMethodField()
    ones_total = serializers.SerializerMethodField()
    twos_total = serializers.SerializerMethodField()
    threes_total = serializers.SerializerMethodField()
    fours_total = serializers.SerializerMethodField()
    fives_total = serializers.SerializerMethodField()
    throws_total = serializers.SerializerMethodField()
    gteSix_total = serializers.SerializerMethodField()
    pike_percentage = serializers.SerializerMethodField()
    zero_percentage = serializers.SerializerMethodField()
    score_per_throw = serializers.SerializerMethodField()
    avg_throw_turn = serializers.SerializerMethodField()
    matches = serializers.SerializerMethodField()

    def get_ones_total(self, obj):
        # return Throw.objects.filter(season=self.context.get('season'), player=obj).aggregate(first=Count('pk',filter=Q(score==1)),second=Count('pk',filter=Q(score==1)),third=Count('pk',filter=Q(score==1)),fourth=Count('pk',filter=Q(score==1)))
        return Throw.objects.filter(season=self.context.get('season'), player=obj).annotate(count=Count('pk',filter=Q(score_first=1)) + Count('pk',filter=Q(score_second=1)) + Count('pk',filter=Q(score_third=1)) + Count('pk',filter=Q(score_fourth=1))).aggregate(Sum('count'))['count__sum']

    def get_twos_total(self, obj):
        # return Throw.objects.filter(season=self.context.get('season'), player=obj).aggregate(first=Count('pk',filter=Q(score==2)),second=Count('pk',filter=Q(score==2)),third=Count('pk',filter=Q(score==2)),fourth=Count('pk',filter=Q(score==2)))
        return Throw.objects.filter(season=self.context.get('season'), player=obj).annotate(count=Count('pk',filter=Q(score_first=2)) + Count('pk',filter=Q(score_second=2)) + Count('pk',filter=Q(score_third=2)) + Count('pk',filter=Q(score_fourth=2))).aggregate(Sum('count'))['count__sum']

    def get_threes_total(self, obj):
        # return Throw.objects.filter(season=self.context.get('season'), player=obj).aggregate(first=Count('pk',filter=Q(score==3)),second=Count('pk',filter=Q(score==3)),third=Count('pk',filter=Q(score==3)),fourth=Count('pk',filter=Q(score==3)))
        return Throw.objects.filter(season=self.context.get('season'), player=obj).annotate(count=Count('pk',filter=Q(score_first=3)) + Count('pk',filter=Q(score_second=3)) + Count('pk',filter=Q(score_third=3)) + Count('pk',filter=Q(score_fourth=3))).aggregate(Sum('count'))['count__sum']

    def get_fours_total(self, obj):
        # return Throw.objects.filter(season=self.context.get('season'), player=obj).aggregate(first=Count('pk',filter=Q(score==4)),second=Count('pk',filter=Q(score==4)),third=Count('pk',filter=Q(score==4)),fourth=Count('pk',filter=Q(score==4)))
        return Throw.objects.filter(season=self.context.get('season'), player=obj).annotate(count=Count('pk',filter=Q(score_first=4)) + Count('pk',filter=Q(score_second=4)) + Count('pk',filter=Q(score_third=4)) + Count('pk',filter=Q(score_fourth=4))).aggregate(Sum('count'))['count__sum']

    def get_fives_total(self, obj):
        # return Throw.objects.filter(season=self.context.get('season'), player=obj).aggregate(first=Count('pk',filter=Q(score==5)),second=Count('pk',filter=Q(score==5)),third=Count('pk',filter=Q(score==5)),fourth=Count('pk',filter=Q(score==5)))
        return Throw.objects.filter(season=self.context.get('season'), player=obj).annotate(count=Count('pk',filter=Q(score_first=5)) + Count('pk',filter=Q(score_second=5)) + Count('pk',filter=Q(score_third=5)) + Count('pk',filter=Q(score_fourth=5))).aggregate(Sum('count'))['count__sum']


    # def get_gteSix_total(self, obj):
    #     self.throws = Throw.objects.filter(season=self.context.get('season'), player=obj, score__gte=6).count()
    #     return self.throws

    def get_zero_percentage(self, obj):
        zero_count = self.zeros
        total_count = self.throws
        try:
            pike_percentage = round((zero_count / total_count)*100, 2)
        except ZeroDivisionError:
            pike_percentage = 0
        return pike_percentage

    def get_matches(self, obj):
        try:
            matches = Match.objects.filter(throw__player=obj, season=self.context.get('season')).distinct()
            matches = UserMatchSerializer(matches, many=True, context={'user_id':obj.id}).data
        except Match.DoesNotExist:
            matches = None
        return matches

    class Meta:
        model = User
        fields = (
                'id', 'player_name', 'team', 'score_total', 'match_count',
                'rounds_total', 'zeros_total', 'ones_total', 'twos_total', 'threes_total',
                'fours_total', 'fives_total', 'gteSix_total', 'pikes_total', 'throws_total', 'pike_percentage',
                'zero_percentage', 'score_per_throw', 'avg_throw_turn', 'matches',
                  )

class UserMatchSerializer(serializers.ModelSerializer):
    throws = serializers.SerializerMethodField()


    def get_throws(self, obj):
        try:
            user = self.context.get('user_id')
            throws = obj.throw_set.filter(player=user)
            rounds = UserThrowSerializer(throws, many=True).data
        except Throw.DoesNotExist:
            rounds = None
        return rounds

    class Meta:
        model = Match
        fields = ('id', 'match_time', 'home_team', 'away_team', 'throws')

class UserThrowSerializer(serializers.ModelSerializer):
    score_total = serializers.SerializerMethodField()

    def get_score_total(self, obj):
        return None

    class Meta:
        model = Throw
        fields = ('id', 'throw_round', 'throw_turn', 'score_first','score_second','score_third','score_fourth', 'score_total')

class PlayerNameSerializer(SharedPlayerSerializer):
    player_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'player_name')


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ('id', 'name', 'abbreviation')

class TeamListSerializer(serializers.ModelSerializer):
    matches_won = serializers.SerializerMethodField()
    matches_lost = serializers.SerializerMethodField()
    matches_tie = serializers.SerializerMethodField()
    matches_played = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()

    def get_matches_won(self, obj):
        home_wins = obj.home_matches.filter(season=self.context.get('season')).annotate(home = F('home_first_round_score') + F('home_second_round_score'), \
         away = F('away_first_round_score') + F('away_second_round_score')).filter(home__gt=F('away')).count()
        away_wins = obj.away_matches.filter(season=self.context.get('season')).annotate(home = F('home_first_round_score') + F('home_second_round_score'), \
         away = F('away_first_round_score') + F('away_second_round_score')).filter(away__gt=F('home')).count()
        return home_wins + away_wins

    def get_matches_lost(self, obj):
        home_loses = obj.home_matches.filter(season=self.context.get('season')).annotate(home = F('home_first_round_score') + F('home_second_round_score'), \
         away = F('away_first_round_score') + F('away_second_round_score')).filter(away__gt=F('home')).count()
        away_loses = obj.away_matches.filter(season=self.context.get('season')).annotate(home = F('home_first_round_score') + F('home_second_round_score'), \
         away = F('away_first_round_score') + F('away_second_round_score')).filter(home__gt=F('away')).count()
        return home_loses + away_loses
    def get_matches_tie(self, obj):
        home_ties = obj.home_matches.filter(season=self.context.get('season')).annotate(home = F('home_first_round_score') + F('home_second_round_score'), \
         away = F('away_first_round_score') + F('away_second_round_score')).filter(home__exact=F('away')).count()
        away_ties = obj.away_matches.filter(season=self.context.get('season')).annotate(home = F('home_first_round_score') + F('home_second_round_score'), \
         away = F('away_first_round_score') + F('away_second_round_score')).filter(away__exact=F('home')).count()
        return home_ties + away_ties
    def get_matches_played(self, obj):
        return Match.objects.filter(season=self.context.get('season')).filter(Q(home_team=obj) | Q(away_team=obj)).count()
    def get_score_total(self, obj):
        return Throw.objects.filter(team=obj, season=self.context.get('season')).annotate(
            score = Case(
                When(score_first__gt=0, then='score_first'),
                default=Value('0'),
                output_field=IntegerField(),
            ) + Case(
                When(score_second__gt=0, then='score_second'),
                default=Value('0'),
                output_field=IntegerField(),
            ) + Case(
                When(score_third__gt=0, then='score_third'),
                default=Value('0'),
                output_field=IntegerField(),
            ) + Case(
                When(score_fourth__gt=0, then='score_fourth'),
                default=Value('0'),
                output_field=IntegerField(),
            )
        ).aggregate(Sum('score'))['score__sum']
        # return Throw.objects.filter(score__gt=0, team=obj, season=self.context.get('season')).aggregate(Sum('score'))['score__sum']

    class Meta:
        model = Team
        fields = ('id', 'name', 'abbreviation', 'matches_won', 'matches_lost', 'matches_tie',
                    'matches_played', 'score_total')

class TeamDetailSerializer(serializers.ModelSerializer):
    score_total = serializers.SerializerMethodField()
    match_count = serializers.SerializerMethodField()
    pikes_total = serializers.SerializerMethodField()
    zeros_total = serializers.SerializerMethodField()
    zero_first_throw_total = serializers.SerializerMethodField()
    pike_first_throw_total = serializers.SerializerMethodField()
    throws_total = serializers.SerializerMethodField()
    gteSix_total = serializers.SerializerMethodField()
    pike_percentage = serializers.SerializerMethodField()
    zero_percentage = serializers.SerializerMethodField()
    score_per_throw = serializers.SerializerMethodField()
    matches = serializers.SerializerMethodField()
    players = serializers.SerializerMethodField()


    def get_score_total(self, obj):
        return Throw.objects.filter(team=obj, season=self.context.get('season')).annotate(
            score = Case(
                When(score_first__gt=0, then='score_first'),
                default=Value('0'),
                output_field=IntegerField(),
            ) + Case(
                When(score_second__gt=0, then='score_second'),
                default=Value('0'),
                output_field=IntegerField(),
            ) + Case(
                When(score_third__gt=0, then='score_third'),
                default=Value('0'),
                output_field=IntegerField(),
            ) + Case(
                When(score_fourth__gt=0, then='score_fourth'),
                default=Value('0'),
                output_field=IntegerField(),
            )
        ).aggregate(Sum('score'))['score__sum']
    def get_match_count(self, obj):
        return Match.objects.filter(season=self.context.get('season'), throw__team=obj).distinct().count()
    def get_throws_total(self, obj):
        return self.context.get('throws_total')
    def get_pikes_total(self, obj):
        return self.context.get('pikes_total')
    def get_zeros_total(self, obj):
        return self.context.get('zeros_total')
    def get_zero_first_throw_total(self, obj):
        return Throw.objects.filter(season=self.context.get('season'), team=obj, score_first=0, throw_turn=1).count()
    def get_pike_first_throw_total(self, obj):
        return Throw.objects.filter(season=self.context.get('season'), team=obj, score_first=-1, throw_turn=1).count()
    def get_gteSix_total(self, obj):
        return Throw.objects.filter(season=self.context.get('season'), team=obj).annotate(count=Count('pk',filter=Q(score_first__gte=6)) + Count('pk',filter=Q(score_second__gte=6)) + Count('pk',filter=Q(score_third__gte=6)) + Count('pk',filter=Q(score_fourth__gte=6))).aggregate(Sum('count'))['count__sum']
    def get_pike_percentage(self, obj):
        try:
            pike_percentage = round((self.context.get('pikes_total') / self.context.get('throws_total'))*100, 2)
        except ZeroDivisionError:
            pike_percentage = 0
        return pike_percentage
    def get_zero_percentage(self, obj):
        try:
            zero_percentage = round((self.context.get('zeros_total') / self.context.get('throws_total'))*100, 2)
        except ZeroDivisionError:
            zero_percentage = 0
        return zero_percentage
    def get_score_per_throw(self, obj):
        return None
    def get_matches(self, obj):
        return None
    def get_players(self, obj):
        users = obj.players
        return PlayerListSerializer(users,many=True, context={'season': self.context.get('season')}).data


    class Meta:
        model = Team
        fields = ('id', 'name', 'abbreviation', 'score_total', 'match_count', 'pikes_total',
                    'zeros_total', 'zero_first_throw_total', 'pike_first_throw_total',
                    'throws_total', 'gteSix_total', 'pike_percentage', 'zero_percentage',
                    'score_per_throw', 'matches', 'players')

class SharedMatchSerializer(serializers.ModelSerializer):
    def get_home_score_total(self, obj):
        try:
            return obj.home_first_round_score + obj.home_second_round_score
        except TypeError:
            return None

    def get_away_score_total(self, obj):
        try:
            return obj.away_first_round_score + obj.away_second_round_score
        except TypeError:
            return None

class MatchListSerializer(SharedMatchSerializer):
    home_score_total = serializers.SerializerMethodField()
    away_score_total = serializers.SerializerMethodField()
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()

    def get_home_team(self, obj):
        return TeamSerializer(obj.home_team).data

    def get_away_team(self, obj):
        return TeamSerializer(obj.away_team).data

    class Meta:
        model = Match
        fields = ('id', 'match_time', 'home_team', 'away_team', 'home_score_total', 'away_score_total')

class MatchDetailSerializer(SharedMatchSerializer):
    home_score_total = serializers.SerializerMethodField()
    away_score_total = serializers.SerializerMethodField()
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()
    first_round = serializers.SerializerMethodField()
    second_round = serializers.SerializerMethodField()

    def get_second_round(self, obj):
        return MatchRoundSerializer(obj.throw_set.filter(throw_round=2), context={'home_team':obj.home_team, 'away_team':obj.away_team}).data

    def get_first_round(self, obj):
        return MatchRoundSerializer(obj.throw_set.filter(throw_round=1), context={'home_team':obj.home_team, 'away_team':obj.away_team}).data

    def get_home_team(self, obj):
        return MatchTeamSerializer(obj.home_team, context={'season': self.context.get('season')}).data

    def get_away_team(self, obj):
        return MatchTeamSerializer(obj.away_team, context={'season': self.context.get('season')}).data

    class Meta:
        model = Match
        fields = ('id', 'match_time', 'home_score_total', 'away_score_total', 'home_first_round_score', 'home_second_round_score',
                    'away_first_round_score', 'away_second_round_score', 'first_round', 'second_round', 'home_team', 'away_team', 'is_validated')

class MatchTeamSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField()

    def get_players(self, obj):
        return PlayerNameSerializer(obj.players.filter(playersinteam__season=self.context.get('season')), many=True).data

    class Meta:
        model = Team
        fields = ('id', 'name', 'abbreviation', 'players')

class MatchRoundSerializer(serializers.ModelSerializer):
    home = serializers.SerializerMethodField()
    away = serializers.SerializerMethodField()

    def get_home(self, qs):
        home_throws = qs.filter(team=self.context.get('home_team'))
        return ThrowScoreSerialzier(home_throws, many=True).data


    def get_away(self, qs):
        away_throws = qs.filter(team=self.context.get('away_team'))
        return ThrowScoreSerialzier(away_throws, many=True).data

    class Meta:
        model = Throw
        fields = ('home', 'away')

class ThrowScoreSerialzier(serializers.ModelSerializer):
    player = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()

    def get_player(self, obj):
        return UserSerializer(obj.player).data

    def get_score_total(self, obj):
        score_total = 0
        for score in [obj.score_first, obj.score_second, obj.score_third, obj.score_fourth]:
            if score is not None and score > 0:
                score_total += score
        return score_total

    class Meta:
        model = Throw
        fields = ('player', 'score_total', 'score_first','score_second','score_third','score_fourth', 'throw_turn')

# class ThrowSerializer(serializers.ModelSerializer)

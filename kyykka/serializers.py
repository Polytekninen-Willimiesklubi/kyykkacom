from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Case, Count, F, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Cast, Substr
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from kyykka.models import (
    CurrentSeason,
    ExtraBracketStagePlacement,
    Match,
    News,
    Player,
    PlayersInTeam,
    Season,
    SuperWeekend,
    Team,
    TeamsInSeason,
    Throw,
)
from utils.caching import getFromCache, setToCache


def required(value):
    if value is None:
        raise serializers.ValidationError("This field is required")


def score_format(scores: list):
    return_list = []
    number_of_zeros = 0
    h = 0
    for score in scores:
        if score is None:
            continue
        elif score == "h" or score == "e":
            continue
        elif ord(score[0]) != 8722:  # ascii 8722 is minus sign
            continue
        else:
            number_of_zeros += 1
            tmp = int(score[1:]) * -1
            h = abs(tmp)
    text = f"h{h}0{number_of_zeros - h}"
    for score in scores:
        if score is None:
            return_list.append(score)
        elif score == "h" or score == "e":
            return_list.append(score)
        elif ord(score[0]) != 8722:
            return_list.append(score)
        else:
            return_list.append(text)
    return return_list


def count_negative_values(obj, season, throws=None, key="player"):
    if int(season.year) > 2012:
        return (0, 0)
    key = f"{key}_{str(obj.id)}_{season.year}_negative_total"
    result_total = getFromCache(key, season.year)
    if result_total is None:
        throws = (
            Throw.objects.filter(match__is_validated=True, season=season, player=obj)
            if throws is None
            else throws
        )
        result_total = throws.annotate(
            count=Count("pk", filter=Q(score_first__contains=chr(8722)))
            + Count("pk", filter=Q(score_second__contains=chr(8722)))
            + Count("pk", filter=Q(score_third__contains=chr(8722)))
            + Count("pk", filter=Q(score_fourth__contains=chr(8722))),
            h=(
                Case(
                    When(
                        score_first__contains=chr(8722),
                        then=Substr("score_first", 2, 1),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                )
                + Case(
                    When(
                        score_second__contains=chr(8722),
                        then=Substr("score_second", 2, 1),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                )
                + Case(
                    When(
                        score_third__contains=chr(8722),
                        then=Substr("score_third", 2, 1),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                )
                + Case(
                    When(
                        score_fourth__contains=chr(8722),
                        then=Substr("score_fourth", 2, 1),
                    ),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            / (
                Count("pk", filter=Q(score_first__contains=chr(8722)))
                + Count("pk", filter=Q(score_second__contains=chr(8722)))
                + Count("pk", filter=Q(score_third__contains=chr(8722)))
                + Count("pk", filter=Q(score_fourth__contains=chr(8722)))
            ),
        ).aggregate(Sum("h"), Sum("count"))
        pikes = result_total["h__sum"]
        pikes = pikes if pikes is not None else 0
        zero = result_total["count__sum"]
        zero = zero if zero is not None else 0
        zeros = zero - pikes
        result_total = (pikes, zeros)
        setToCache(key, result_total, season_year=season.year)
    return result_total


def count_throw_results(obj, season, result, throws=None, key="player"):
    key = f"{key}_{str(obj.id)}_{str(result)}_total"
    result_total = getFromCache(key, season.year)
    if result_total is None:
        throws = (
            Throw.objects.filter(match__is_validated=True, season=season, player=obj)
            if throws is None
            else throws
        )
        result_total = throws.annotate(
            count=Count("pk", filter=Q(score_first=result))
            + Count("pk", filter=Q(score_second=result))
            + Count("pk", filter=Q(score_third=result))
            + Count("pk", filter=Q(score_fourth=result))
        ).aggregate(Sum("count"))["count__sum"]
        if result_total is None:
            result_total = 0
        setToCache(key, result_total, season_year=season.year)
    return result_total


def count_gte_six_throw_results(obj, season, throws=None, key="player"):
    key = f"{key}_{str(obj.id)}_gteSix_total"
    result_total = getFromCache(key, season.year)
    if result_total is None:
        throws = (
            Throw.objects.filter(match__is_validated=True, season=season, player=obj)
            if throws is None
            else throws
        )
        result_total = (
            throws.annotate(
                st=Cast("score_first", output_field=IntegerField()),
                nd=Cast("score_second", output_field=IntegerField()),
                rd=Cast("score_third", output_field=IntegerField()),
                th=Cast("score_fourth", output_field=IntegerField()),
            )
            .annotate(
                count=Count("pk", filter=Q(st__gte=6))
                + Count("pk", filter=Q(nd__gte=6))
                + Count("pk", filter=Q(rd__gte=6))
                + Count("pk", filter=Q(th__gte=6))
            )
            .aggregate(Sum("count"))["count__sum"]
        )
        if result_total is None:
            result_total = 0
        setToCache(key, result_total, season_year=season.year)
    return result_total


def count_score_total(obj, season, throws, key="player"):
    key = f"{key}_{str(obj.id)}_score_total"
    score_total = getFromCache(key, season.year)
    if score_total is None:
        score_total = (
            throws.annotate(
                st=Cast("score_first", output_field=IntegerField()),
                nd=Cast("score_second", output_field=IntegerField()),
                rd=Cast("score_third", output_field=IntegerField()),
                th=Cast("score_fourth", output_field=IntegerField()),
            )
            .annotate(score=F("st") + F("nd") + F("rd") + F("th"))
            .aggregate(Sum("score"))["score__sum"]
        )
        if score_total is None:
            score_total = 0
        setToCache(key, score_total, season_year=season.year)
    return score_total


class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(validators=[required], max_length=30)
    last_name = serializers.CharField(validators=[required], max_length=150)
    number = serializers.IntegerField(validators=[required], min_value=0, max_value=99)

    class Meta:
        model = User
        fields = ("id", "username", "number", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"],
            validated_data["username"],
            validated_data["password"],
        )
        user.first_name = validated_data["first_name"]
        user.last_name = validated_data["last_name"]
        user.save()
        Player.objects.create(user=user, number=validated_data["number"])
        msg = ""
        return True, msg, user


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()  # .EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")


class SharedPlayerSerializer(serializers.ModelSerializer):
    def get_player_name(self, obj: User):
        return f"{obj.first_name} {obj.last_name}"

    def get_player_number(self, obj):
        try:
            return obj.player.number
        except Exception:
            return None

    def get_score_total(self, obj):
        self.throw_set = obj.throw_set.filter(
            season=self.context.get("season"), match__is_validated=True
        )
        if (post_season := self.context.get("post_season", None)) is False:
            self.throw_set = self.throw_set.filter(
                match__match_type__lt=31, match__post_season=False
            )
        elif post_season:
            self.throw_set = self.throw_set.filter(match__post_season=True)

        if position := self.context.get("throw_turn", None):
            self.throw_set = self.throw_set.filter(throw_turn=position)
        self.score_total = count_score_total(
            obj, self.context.get("season"), self.throw_set
        )
        return self.score_total

    def get_match_count(self, obj):
        key = f"player_{str(obj.id)}_match_count"
        match_count = getFromCache(key, self.context.get("season").year)
        if match_count is None:
            match_count = self.throw_set.values("match").distict().count()
            if match_count is None:
                match_count = 0
            setToCache(key, match_count, season_year=self.context.get("season").year)
        return match_count

    def get_rounds_total(self, obj):
        key = f"player_{str(obj.id)}_rounds_total"
        rounds_total = getFromCache(key, self.context.get("season").year)
        if rounds_total is None:
            rounds_total = self.throw_set.count()
            setToCache(key, rounds_total, season_year=self.context.get("season").year)
        self.rounds_total = rounds_total
        return self.rounds_total

    def get_team(self, obj):
        try:
            t = TeamsInSeason.objects.filter(
                season=self.context.get("season"), playersinteam__player=obj
            ).first()
            team = TeamSerializer(t).data
        except TeamsInSeason.DoesNotExist:
            team = None
        return team

    def get_pikes_total(self, obj):
        season = self.context.get("season")
        self.pikes = count_throw_results(obj, season, "h", self.throw_set)
        pikes, zeros = count_negative_values(obj, season, self.throw_set)
        self.z = zeros
        self.pikes += pikes
        return self.pikes

    def get_zeros_total(self, obj):
        self.zeros = count_throw_results(
            obj, self.context.get("season"), 0, self.throw_set
        )
        self.zeros += self.z
        return self.zeros

    def get_gteSix_total(self, obj):
        return count_gte_six_throw_results(
            obj, self.context.get("season"), self.throw_set
        )

    def get_throws_total(self, obj):
        key = f"player_{str(obj.id)}_throws_total"
        throws_total = getFromCache(key, self.context.get("season").year)
        if throws_total is None:
            throws_total = self.rounds_total * 4 - count_throw_results(
                obj, self.context.get("season"), "e", self.throw_set
            )
            if throws_total is None:
                throws_total = 0
            setToCache(key, throws_total, season_year=self.context.get("season").year)
        self.throws = throws_total
        return self.throws

    def get_pike_percentage(self, obj):
        key = f"player_{str(obj.id)}_pike_percentage"
        pike_percentage = getFromCache(key, self.context.get("season").year)
        if pike_percentage is None:
            try:
                pike_percentage = round((self.pikes / self.throws) * 100, 2)
            except (ZeroDivisionError, TypeError):
                pike_percentage = 0
            setToCache(
                key, pike_percentage, season_year=self.context.get("season").year
            )
        return pike_percentage

    def get_score_per_throw(self, obj):
        key = f"player_{str(obj.id)}_score_per_throw"
        score_per_throw = getFromCache(key, self.context.get("season").year)
        if score_per_throw is None:
            try:
                score_per_throw = round(self.score_total / self.throws, 2)
            except (ZeroDivisionError, TypeError):
                score_per_throw = 0
            setToCache(
                key, score_per_throw, season_year=self.context.get("season").year
            )
        return score_per_throw

    def get_avg_throw_turn(self, obj):
        key = f"player_{str(obj.id)}_avg_throw_turn"
        avg_throw_turn = getFromCache(key, self.context.get("season").year)
        if avg_throw_turn is None:
            try:
                avg_throw_turn_sum = self.throw_set.aggregate(Sum("throw_turn"))[
                    "throw_turn__sum"
                ]
                no_throws_turn_sum = (
                    self.throw_set.filter(
                        Q(score_first="e")
                        | Q(score_second="e")
                        | Q(score_third="e")
                        | Q(score_fourth="e")
                    )
                    .annotate(
                        count=F("throw_turn")
                        * (
                            Count("pk", filter=Q(score_first="e"))
                            + Count("pk", filter=Q(score_second="e"))
                            + Count("pk", filter=Q(score_third="e"))
                            + Count("pk", filter=Q(score_fourth="e"))
                        )
                    )
                    .aggregate(Sum("count"))["count__sum"]
                )
                if no_throws_turn_sum is None:
                    no_throws_turn_sum = 0
                avg_throw_turn = round(
                    (avg_throw_turn_sum * 4 - no_throws_turn_sum) / self.throws, 2
                )
            except (ZeroDivisionError, TypeError):
                avg_throw_turn = 0
            setToCache(key, avg_throw_turn, season_year=self.context.get("season").year)
        return avg_throw_turn

    class Meta:
        model = User


class UserSerializer(SharedPlayerSerializer):
    player_name = serializers.SerializerMethodField()
    player_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "player_name", "player_number")


class ReserveListSerializer(SharedPlayerSerializer):
    player_name = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    player_number = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "player_number", "player_name", "team")


# TODO Figure a proper way to validate Unique Together between season and player
class ReserveCreateSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(
        validators=[required], queryset=User.objects.all()
    )
    # season = serializers.SerializerMethodField()
    #
    # def get_season(self):
    #     return CurrentSeason.objects.first().season

    class Meta:
        model = PlayersInTeam
        fields = ("id", "player")
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=PlayersInTeam.objects.all(),
        #         fields=["season", "player"]
        #     )
        # ]

    def create(self, validated_data):
        user = self.context.get("request").user
        add_player = validated_data["player"]
        season = CurrentSeason.objects.first().season
        try:
            team = user.teamsinseason_set.get(season=season)
            PlayersInTeam.objects.create(team_season=team, player=add_player)
        except IntegrityError:
            print("reserve duplicate", user.id, add_player)
            return False, "DUPLICATE"
        except Team.DoesNotExist:
            print("reserve team 404", user.id, add_player)
            return False, "USER_TEAM_404"
        return True, ""


class PlayerListSerializer(SharedPlayerSerializer):
    team = serializers.SerializerMethodField()
    player_name = serializers.SerializerMethodField()
    player_number = serializers.SerializerMethodField()
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
    scaled_points_per_throw = serializers.SerializerMethodField()
    is_captain = serializers.SerializerMethodField()

    # The orignal formula from Henna Pekkala's under grad: 'https://urn.fi/URN:NBN:fi-fe2019062722140'
    #   points = 2n(w + h) / 10
    #       w:  scaling factor based on throw number: players 1. and 2. throws have
    #           factor 9 and 3. and 4. have 13
    #       h:  throw turn number (1-4)
    #       n:  scored kyykkas
    def scaled(self, result, throw_turn, throw_number):
        return (result * (9 + 4 * int((throw_number - 1) / 2) + throw_turn)) / 5

    def convert_score(self, score: str):
        return int(score) if score is not None and score.isnumeric() else 0

    def get_scaled_points(self, obj):
        self.scaled_points = (
            self.throw_set.annotate(
                st=Cast("score_first", output_field=IntegerField()),
                nd=Cast("score_second", output_field=IntegerField()),
                rd=Cast("score_third", output_field=IntegerField()),
                th=Cast("score_fourth", output_field=IntegerField()),
            )
            .annotate(
                scaled_points=(F("st") * (9 + F("throw_turn"))) / 5
                + (F("nd") * (9 + F("throw_turn"))) / 5
                + (F("rd") * (13 + F("throw_turn"))) / 5
                + (F("th") * (13 + F("throw_turn"))) / 5
            )
            .aggregate(Sum("scaled_points"))["scaled_points__sum"]
        )
        if not self.scaled_points:
            self.scaled_points = 0
        return self.scaled_points

    def get_scaled_points_per_throw(self, obj):
        return round(self.scaled_points / self.throws, 2) if self.throws != 0 else "NaN"

    def get_is_captain(self, obj):
        try:
            captain = obj.playerinteam_set.get(season=self.context.get("season"))
            if captain is None:
                return False
            return captain
        except Exception:
            return False

    class Meta:
        model = User
        fields = (
            "id",
            "player_name",
            "player_number",
            "team",
            "score_total",
            "rounds_total",
            "pikes_total",
            "zeros_total",
            "gteSix_total",
            "throws_total",
            "pike_percentage",
            "score_per_throw",
            "scaled_points",
            "scaled_points_per_throw",
            "avg_throw_turn",
            "is_captain",
        )


class PlayerListAllPositionSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    first_position = serializers.SerializerMethodField()
    second_position = serializers.SerializerMethodField()
    third_position = serializers.SerializerMethodField()
    fourth_position = serializers.SerializerMethodField()

    def get_total(self, obj: User):
        self.season = self.context["season"]
        self.post_season = self.context.get("post_season", None)
        return PlayerListSerializer(
            obj, context={"season": self.season, "post_season": self.post_season}
        ).data

    def get_first_position(self, obj: User):
        return PlayerListSerializer(
            obj,
            context={
                "season": self.season,
                "throw_turn": 1,
                "post_season": self.post_season,
            },
        ).data

    def get_second_position(self, obj: User):
        return PlayerListSerializer(
            obj,
            context={
                "season": self.season,
                "throw_turn": 2,
                "post_season": self.post_season,
            },
        ).data

    def get_third_position(self, obj: User):
        return PlayerListSerializer(
            obj,
            context={
                "season": self.season,
                "throw_turn": 3,
                "post_season": self.post_season,
            },
        ).data

    def get_fourth_position(self, obj: User):
        return PlayerListSerializer(
            obj,
            context={
                "season": self.season,
                "throw_turn": 4,
                "post_season": self.post_season,
            },
        ).data

    class Meta:
        model = User
        fields = (
            "id",
            "total",
            "first_position",
            "second_position",
            "third_position",
            "fourth_position",
        )


class PlayerAllDetailSerializer(SharedPlayerSerializer):
    season = serializers.SerializerMethodField()
    season_count = serializers.SerializerMethodField()
    player_name = serializers.SerializerMethodField()
    stats_per_seasons = serializers.SerializerMethodField()
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
        seasons = (
            Match.objects.filter(throw__player=obj, is_validated=True)
            .distinct()
            .values_list("season")
        )
        self.stats_per_seasons = []
        for s in seasons:
            s = s[0]
            self.stats_per_seasons.append(
                PlayerDetailSerializer(
                    obj, context={"season": Season.objects.get(id=s)}
                ).data
            )

        self.all_score_total = 0
        self.all_match_count = 0
        self.all_rounds_total = 0
        self.all_pikes_total = 0
        self.all_zeros_total = 0
        self.all_ones_total = 0
        self.all_twos_total = 0
        self.all_threes_total = 0
        self.all_fours_total = 0
        self.all_fives_total = 0
        self.all_throws_total = 0
        self.all_gteSix_total = 0
        self.average_throw_sum = 0
        for s in self.stats_per_seasons:
            self.all_score_total += s["score_total"]
            self.all_match_count += s["match_count"]
            self.all_rounds_total += s["rounds_total"]
            self.all_pikes_total += s["pikes_total"]
            self.all_zeros_total += s["zeros_total"]
            self.all_ones_total += s["ones_total"]
            self.all_twos_total += s["twos_total"]
            self.all_threes_total += s["threes_total"]
            self.all_fours_total += s["fours_total"]
            self.all_fives_total += s["fives_total"]
            self.all_throws_total += s["throws_total"]
            self.all_gteSix_total += s["gteSix_total"]
            self.average_throw_sum += s["throws_total"] * s["avg_throw_turn"]

        return self.stats_per_seasons

    def get_all_score_total(self, obj):
        return self.all_score_total

    def get_all_match_count(self, obj):
        return self.all_match_count

    def get_all_rounds_total(self, obj):
        return self.all_rounds_total

    def get_all_pikes_total(self, obj):
        return self.all_pikes_total

    def get_all_zeros_total(self, obj):
        return self.all_zeros_total

    def get_all_ones_total(self, obj):
        return self.all_ones_total

    def get_all_twos_total(self, obj):
        return self.all_twos_total

    def get_all_threes_total(self, obj):
        return self.all_threes_total

    def get_all_fours_total(self, obj):
        return self.all_fours_total

    def get_all_fives_total(self, obj):
        return self.all_fives_total

    def get_all_throws_total(self, obj):
        return self.all_throws_total

    def get_all_gteSix_total(self, obj):
        return self.all_gteSix_total

    def get_total_zero_percentage(self, obj):
        if self.all_throws_total == 0:
            return 0
        return round((self.all_zeros_total / self.all_throws_total) * 100, 2)

    def get_total_pike_percentage(self, obj):
        if self.all_throws_total == 0:
            return 0
        return round((self.all_pikes_total / self.all_throws_total) * 100, 2)

    def get_total_average_throw(self, obj):
        if self.all_throws_total == 0:
            return 0
        return round((self.all_score_total / self.all_throws_total), 2)

    def get_total_average_throw_turn(self, obj):
        if self.all_throws_total == 0:
            return 0
        return round(self.average_throw_sum / self.all_throws_total, 2)

    def get_season(self, obj):
        return "All-Time"

    def get_season_count(self, obj):
        return len(self.stats_per_seasons)

    class Meta:
        model = User
        fields = (
            "id",
            "season",
            "player_name",
            "stats_per_seasons",
            "all_score_total",
            "all_match_count",
            "all_rounds_total",
            "all_pikes_total",
            "all_zeros_total",
            "all_ones_total",
            "all_twos_total",
            "all_threes_total",
            "all_fours_total",
            "all_fives_total",
            "all_throws_total",
            "all_gteSix_total",
            "total_zero_percentage",
            "total_pike_percentage",
            "total_average_throw",
            "total_average_throw_turn",
            "season_count",
        )


class PlayerDetailSerializer(SharedPlayerSerializer):
    id = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    player_name = serializers.SerializerMethodField()
    player_number = serializers.SerializerMethodField()
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
    season = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    average_score_position_one = serializers.SerializerMethodField()
    average_score_position_two = serializers.SerializerMethodField()
    average_score_position_three = serializers.SerializerMethodField()
    average_score_position_four = serializers.SerializerMethodField()

    def get_id(self, obj):
        return int(self.season.year)

    def get_season(self, obj):
        self.season = self.context.get("season")
        return self.season.year

    def get_team_name(self, obj):
        return TeamsInSeason.objects.get(
            season=self.season, playersinteam__player=obj
        ).current_abbreviation

    def get_ones_total(self, obj):
        return count_throw_results(obj, self.season, 1, self.throw_set)

    def get_twos_total(self, obj):
        return count_throw_results(obj, self.season, 2, self.throw_set)

    def get_threes_total(self, obj):
        return count_throw_results(obj, self.season, 3, self.throw_set)

    def get_fours_total(self, obj):
        return count_throw_results(obj, self.season, 4, self.throw_set)

    def get_fives_total(self, obj):
        return count_throw_results(obj, self.season, 5, self.throw_set)

    def get_zero_percentage(self, obj):
        try:
            pike_percentage = round((self.zeros / self.throws) * 100, 2)
        except (ZeroDivisionError, TypeError):
            pike_percentage = None
        return pike_percentage

    def get_matches(self, obj):
        try:
            throws = Match.objects.filter(
                throw__player=obj, season=self.season, is_validated=True
            ).distinct()
            matches = UserMatchSerializer(
                throws, many=True, context={"user_id": obj.id, "season": self.season}
            ).data
        except Match.DoesNotExist:
            matches = None
        return matches

    def get_average_score_position_one(self, obj):
        throws_set = self.throw_set.filter(throw_turn=1)
        throw_count = throws_set.count() * 4
        no_throws = count_throw_results(obj, self.season, "e", throws_set)
        scores = count_score_total(obj, self.season, throws_set)
        return (
            round(scores / (throw_count - no_throws), 2)
            if throw_count - no_throws != 0
            else 0
        )

    def get_average_score_position_two(self, obj):
        throws_set = self.throw_set.filter(throw_turn=2)
        throw_count = throws_set.count() * 4
        no_throws = count_throw_results(obj, self.season, "e", throws_set)
        scores = count_score_total(obj, self.season, throws_set)
        return (
            round(scores / (throw_count - no_throws), 2)
            if throw_count - no_throws != 0
            else 0
        )

    def get_average_score_position_three(self, obj):
        throws_set = self.throw_set.filter(throw_turn=3)
        throw_count = throws_set.count() * 4
        no_throws = count_throw_results(obj, self.season, "e", throws_set)
        scores = count_score_total(obj, self.season, throws_set)
        return (
            round(scores / (throw_count - no_throws), 2)
            if throw_count - no_throws != 0
            else 0
        )

    def get_average_score_position_four(self, obj):
        throws_set = self.throw_set.filter(throw_turn=4)
        throw_count = throws_set.count() * 4
        no_throws = count_throw_results(obj, self.season, "e", throws_set)
        scores = count_score_total(obj, self.season, throws_set)
        return (
            round(scores / (throw_count - no_throws), 2)
            if throw_count - no_throws != 0
            else 0
        )

    class Meta:
        model = User
        fields = (
            "season",
            "id",
            "team_name",
            "player_name",
            "player_number",
            "team",
            "score_total",
            "match_count",
            "rounds_total",
            "pikes_total",
            "zeros_total",
            "ones_total",
            "twos_total",
            "threes_total",
            "fours_total",
            "fives_total",
            "throws_total",
            "gteSix_total",
            "pike_percentage",
            "zero_percentage",
            "score_per_throw",
            "avg_throw_turn",
            "matches",
            "average_score_position_one",
            "average_score_position_two",
            "average_score_position_three",
            "average_score_position_four",
        )


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
        user = self.context.get("user_id")
        rounds = obj.throw_set.filter(player=user)
        round_one_no_throws, round_two_no_throws = 0, 0
        self.player_first = "-"
        self.player_second = "-"
        self.player_third = "-"
        self.player_fourth = "-"
        self.player_fifth = "-"
        self.player_sixth = "-"
        self.player_seventh = "-"
        self.player_eighth = "-"
        self.round_one_total = 0
        self.round_two_total = 0
        self.throw_average_one = 0
        self.throw_average_two = 0
        self.throw_turn_one = "-"
        self.throw_turn_two = "-"
        for r in rounds:
            st = (
                int(r.score_first)
                if r.score_first is not None and r.score_first.isnumeric()
                else 0
            )
            nd = (
                int(r.score_second)
                if r.score_second is not None and r.score_second.isnumeric()
                else 0
            )
            rd = (
                int(r.score_third)
                if r.score_third is not None and r.score_third.isnumeric()
                else 0
            )
            th = (
                int(r.score_fourth)
                if r.score_fourth is not None and r.score_fourth.isnumeric()
                else 0
            )
            no_throws = (
                (r.score_first == "e")
                + (r.score_second == "e")
                + (r.score_third == "e")
                + (r.score_fourth == "e")
            )

            scores = score_format(
                [r.score_first, r.score_second, r.score_third, r.score_fourth]
            )
            if r.throw_round == 1:
                self.player_first = scores[0]
                self.player_second = scores[1]
                self.player_third = scores[2]
                self.player_fourth = scores[3]
                self.round_one_total = st + nd + rd + th
                self.throw_turn_one = r.throw_turn
                round_one_no_throws = no_throws
                self.throw_average_one = round(
                    self.round_one_total / (4 - round_one_no_throws), 2
                )
            else:
                self.player_fifth = scores[0]
                self.player_sixth = scores[1]
                self.player_seventh = scores[2]
                self.player_eighth = scores[3]
                self.round_two_total = st + nd + rd + th
                self.throw_turn_two = r.throw_turn
                round_two_no_throws = no_throws
                self.throw_average_two = round(
                    self.round_two_total / (4 - round_two_no_throws), 2
                )
        score_total = self.round_one_total + self.round_two_total
        number_of_throws = (
            8
            if type(self.throw_turn_one) is int and type(self.throw_turn_two) is int
            else 4
        )
        self.throw_average_match = round(
            score_total
            / (number_of_throws - round_one_no_throws - round_two_no_throws),
            2,
        )
        return score_total

    def get_opponent_name(self, obj):
        def inner_get_team(obj_team):
            key = "team_" + str(obj_team.id)
            team = getFromCache(key)
            if team is None:
                team = TeamSerializer(obj_team).data
                setToCache(key, team, 3600)
            return team

        home_team = inner_get_team(obj.home_team)
        away_team = inner_get_team(obj.away_team)

        opponent_team = None
        if self.context.get("user_id") in home_team["players"]:
            opponent_team = away_team["current_abbreviation"]
            self.opp_score_first = int(obj.away_first_round_score)
            self.opp_score_second = int(obj.away_second_round_score)
            self.own_score_first = int(obj.home_first_round_score)
            self.own_score_second = int(obj.home_second_round_score)
        elif self.context.get("user_id") in away_team["players"]:
            opponent_team = home_team["current_abbreviation"]
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
        fields = (
            "id",
            "match_time",
            "home_team",
            "away_team",
            "opponent_name",
            "score_total",
            "opponent_score_first",
            "own_score_first",
            "opponent_score_second",
            "own_score_second",
            "score_average_round_one",
            "score_average_round_two",
            "score_average_match",
            "opponent_score",
            "own_score",
            "score_first",
            "score_second",
            "score_third",
            "score_fourth",
            "score_fifth",
            "score_sixth",
            "score_seventh",
            "score_eighth",
            "throw_turn_one",
            "throw_turn_two",
            "score_total_one",
            "score_total_two",
        )


class PlayerNameSerializer(SharedPlayerSerializer):
    player_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "player_name")


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamsInSeason
        fields = (
            "id",
            "current_name",
            "season",
            "current_abbreviation",
            "players",
            "bracket",
        )


class SeasonSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return str(obj)

    def get_value(self, obj):
        return str(obj.id)

    class Meta:
        model = Season
        fields = ("id", "name", "value", "no_brackets", "playoff_format")


class TeamListSerializer(serializers.ModelSerializer):
    matches_won = serializers.SerializerMethodField()
    matches_lost = serializers.SerializerMethodField()
    matches_tie = serializers.SerializerMethodField()
    matches_played = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()
    points_total = serializers.SerializerMethodField()
    match_average = serializers.SerializerMethodField()
    points_average = serializers.SerializerMethodField()
    first_bracket_placement = serializers.SerializerMethodField()

    def count_match_results(self, obj):
        results_home = obj.home_matches.filter(
            is_validated=True, season=self.context.get("season"), match_type__lt=30
        )
        results_away = obj.away_matches.filter(
            is_validated=True, season=self.context.get("season"), match_type__lt=30
        )
        if self.context.get("post_season") is not None:
            results_home = results_home.filter(
                post_season=self.context.get("post_season")
            )
            results_away = results_away.filter(
                post_season=self.context.get("post_season")
            )

        if self.context.get("only_first_stage") is True:
            results_home = results_home.filter(match_type=1)
            results_away = results_away.filter(match_type=1)

        results_home = results_home.annotate(
            home=F("home_first_round_score") + F("home_second_round_score"),
            away=F("away_first_round_score") + F("away_second_round_score"),
        )
        results_away = results_away.annotate(
            home=F("home_first_round_score") + F("home_second_round_score"),
            away=F("away_first_round_score") + F("away_second_round_score"),
        )

        self.matches_won = (
            results_home.filter(home__lt=F("away")).count()
            + results_away.filter(away__lt=F("home")).count()
        )
        self.matches_lost = (
            results_home.filter(away__lt=F("home")).count()
            + results_away.filter(home__lt=F("away")).count()
        )
        self.matches_tie = (
            results_home.filter(home__exact=F("away")).count()
            + results_away.filter(home__exact=F("away")).count()
        )
        self.matches_played = self.matches_lost + self.matches_tie + self.matches_won

        match_score_home = results_home.aggregate(Sum("home"))["home__sum"]
        match_score_away = results_away.aggregate(Sum("away"))["away__sum"]
        if match_score_home is None and match_score_away is None:
            self.match_average = "NaN"
            return
        elif match_score_home is None:
            match_score_home = 0
        elif match_score_away is None:
            match_score_away = 0
        match_score_total = match_score_home + match_score_away
        self.match_average = (
            round(match_score_total / self.matches_played, 2)
            if self.matches_played
            else "NaN"
        )
        
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
        return (
            round(self.points_total / self.matches_played, 2)
            if self.matches_played
            else "NaN"
        )

    def get_score_total(self, obj):
        season = self.context.get("season")
        throws = Throw.objects.filter(match__is_validated=True, team=obj, season=season)
        return count_score_total(obj, season, throws, key="team")

    def get_first_bracket_placement(self, obj):
        seq = ExtraBracketStagePlacement.objects.filter(team_in_season=obj, stage=1)
        if len(seq):
            return seq[0].placement
        else:
            return None

    class Meta:
        model = TeamsInSeason
        fields = (
            "id",
            "team",
            "current_name",
            "current_abbreviation",
            "matches_won",
            "matches_lost",
            "matches_tie",
            "matches_played",
            "match_average",
            "points_total",
            "points_average",
            "score_total",
            "bracket",
            "bracket_placement",
            "second_stage_bracket",
            "first_bracket_placement",
        )


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
        throws = self.context.get("throws")
        self.score_total = count_score_total(obj, self.context.get("season"), throws)
        return self.score_total

    def get_match_count(self, obj):
        self.match_count = (
            Match.objects.filter(
                is_validated=True, season=self.context.get("season"), throw__team=obj
            )
            .distinct()
            .count()
        )
        return self.match_count

    def get_throws_total(self, obj):
        throws = self.context.get("throws")
        throw_rounds = throws.count()
        if throw_rounds is None:
            self.throws_total = 0
        else:
            throws_total = throw_rounds * 4
            no_throws = count_throw_results(
                obj, self.context.get("season"), "e", throws=throws, key="team"
            )
            self.throws_total = throws_total - no_throws
        return self.throws_total

    def get_pikes_total(self, obj):
        self.pikes_total = count_throw_results(
            obj,
            self.context.get("season"),
            "h",
            throws=self.context.get("throws"),
            key="team",
        )
        return self.pikes_total

    def get_zeros_total(self, obj):
        self.zeros_total = count_throw_results(
            obj,
            self.context.get("season"),
            0,
            throws=self.context.get("throws"),
            key="team",
        )
        return self.zeros_total

    def get_zero_or_pike_first_throw_total(self, obj):
        throws = self.context.get("throws")
        return throws.filter(
            Q(throw_turn=1) & (Q(score_first=0) | Q(score_first="h"))
        ).count()

    def get_gteSix_total(self, obj):
        return count_gte_six_throw_results(
            obj,
            self.context.get("season"),
            throws=self.context.get("throws"),
            key="team",
        )

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
            score_home = (
                obj.home_matches.filter(
                    is_validated=True, season=self.context.get("season")
                )
                .annotate(
                    score=F("home_first_round_score") + F("home_second_round_score")
                )
                .aggregate(Sum("score"))["score__sum"]
            )
            score_away = (
                obj.away_matches.filter(
                    is_validated=True, season=self.context.get("season")
                )
                .annotate(
                    score=F("away_first_round_score") + F("away_second_round_score")
                )
                .aggregate(Sum("score"))["score__sum"]
            )
            match_score_total = score_home + score_away
            match_average = round(match_score_total / self.match_count, 2)
        except (ZeroDivisionError, TypeError):
            match_average = 0
        return match_average

    def get_matches(self, obj):
        matches = Match.objects.filter(
            Q(home_team=obj) | Q(away_team=obj), is_validated=True
        )
        return Match2ListSerializer(matches, many=True, context={"team": obj}).data

    def get_players(self, obj):
        return PlayerListSerializer(
            obj.players, many=True, context={"season": self.context.get("season")}
        ).data

    class Meta:
        model = TeamsInSeason
        fields = (
            "id",
            "current_name",
            "current_abbreviation",
            "score_total",
            "match_count",
            "pikes_total",
            "zeros_total",
            "zero_or_pike_first_throw_total",
            "throws_total",
            "gteSix_total",
            "pike_percentage",
            "zero_percentage",
            "match_average",
            "matches",
            "players",
        )


class SharedMatchSerializer(serializers.ModelSerializer):
    def get_home_score_total(self, obj: Match) -> int | None:
        if obj.home_first_round_score is None and obj.home_second_round_score is None:
            return None
        elif obj.home_first_round_score is None:
            return obj.home_second_round_score
        elif obj.home_second_round_score is None:
            return obj.home_first_round_score
        return obj.home_first_round_score + obj.home_second_round_score

    def get_away_score_total(self, obj: Match) -> int | None:
        if obj.away_first_round_score is None and obj.away_second_round_score is None:
            return None
        elif obj.away_first_round_score is None:
            return obj.away_second_round_score
        elif obj.away_second_round_score is None:
            return obj.away_first_round_score
        return obj.away_first_round_score + obj.away_second_round_score


class MatchListSerializer(SharedMatchSerializer):
    home_score_total = serializers.SerializerMethodField()
    away_score_total = serializers.SerializerMethodField()
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()

    def get_home_team(self, obj):
        key = "team_" + str(obj.home_team.id)
        team = getFromCache(key)
        if team is None:
            team = TeamSerializer(obj.home_team).data
            setToCache(key, team, 3600)
        return team

    def get_away_team(self, obj):
        key = "team_" + str(obj.away_team.id)
        team = getFromCache(key)
        if team is None:
            team = TeamSerializer(obj.away_team).data
            setToCache(key, team, 3600)
        return team

    class Meta:
        model = Match
        fields = (
            "id",
            "match_time",
            "field",
            "home_team",
            "away_team",
            "home_score_total",
            "away_score_total",
            "post_season",
            "is_validated",
            "match_type",
            "seriers",
            "video_link",
            "stream_link",
        )


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
        self.own_team = obj.home_team == self.context.get(
            "team"
        )  # Home Team = 1, Away Team = 0
        key = (
            "team_" + str(obj.away_team.id)
            if self.own_team
            else "team_" + str(obj.home_team.id)
        )
        team = getFromCache(key)
        if team is None:
            team = (
                TeamSerializer(obj.away_team).data
                if self.own_team
                else TeamSerializer(obj.home_team).data
            )
            setToCache(key, team, 3600)
        return team["current_abbreviation"]

    def get_own_team_total(self, obj):
        key = "match_" + str(obj.id) + "_own_score_total"
        own_score_total = getFromCache(key)
        if own_score_total is None:
            try:
                if self.own_team:
                    own_score_total = (
                        obj.home_first_round_score + obj.home_second_round_score
                    )
                else:
                    own_score_total = (
                        obj.away_first_round_score + obj.away_second_round_score
                    )
            except TypeError:
                own_score_total = None
            setToCache(key, own_score_total)
        return own_score_total

    def get_opposite_team_total(self, obj):
        key = "match_" + str(obj.id) + "_opposite_score_total"
        opp_score_total = getFromCache(key)
        if opp_score_total is None:
            try:
                if self.own_team:
                    opp_score_total = (
                        obj.away_first_round_score + obj.away_second_round_score
                    )
                else:
                    opp_score_total = (
                        obj.home_first_round_score + obj.home_second_round_score
                    )
            except TypeError:
                opp_score_total = None
            setToCache(key, opp_score_total)
        return opp_score_total

    def get_match_type(self, obj):
        game = {
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
        try:
            return game[obj.match_type] if obj.match_type is not None else ""
        except Exception as e:
            print(f"match_type in object: {obj.match_type}")
            print(f"General error: {e}")

    def get_own_first(self, obj):
        return (
            obj.home_first_round_score if self.own_team else obj.away_first_round_score
        )

    def get_own_second(self, obj):
        return (
            obj.home_second_round_score
            if self.own_team
            else obj.away_second_round_score
        )

    def get_opp_first(self, obj):
        return (
            obj.home_first_round_score
            if not self.own_team
            else obj.away_first_round_score
        )

    def get_opp_second(self, obj):
        return (
            obj.home_second_round_score
            if not self.own_team
            else obj.away_second_round_score
        )

    class Meta:
        model = Match
        fields = (
            "id",
            "match_time",
            "opposite_team",
            "away_team",
            "opposite_team_total",
            "own_team_total",
            "post_season",
            "is_validated",
            "match_type",
            "seriers",
            "own_first",
            "own_second",
            "opp_first",
            "opp_second",
        )


class MatchDetailSerializer(SharedMatchSerializer):
    home_score_total = serializers.SerializerMethodField()
    away_score_total = serializers.SerializerMethodField()
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()
    first_round = serializers.SerializerMethodField()
    second_round = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()

    def get_first_round(self, obj: Match):
        return MatchRoundSerializer(
            obj.throw_set.filter(throw_round=1), # type: ignore
            context={"home_team": obj.home_team, "away_team": obj.away_team},
        ).data

    def get_second_round(self, obj: Match):
        return MatchRoundSerializer(
            obj.throw_set.filter(throw_round=2), # type: ignore
            context={"home_team": obj.home_team, "away_team": obj.away_team},
        ).data

    def get_home_team(self, obj):
        return MatchTeamSerializer(obj.home_team).data

    def get_away_team(self, obj):
        return MatchTeamSerializer(obj.away_team).data

    def get_type_name(self, obj):
        game = {
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
        try:
            return game[obj.match_type] if obj.match_type is not None else ""
        except Exception:
            print(obj.match_type)

    class Meta:
        model = Match
        fields = (
            "id",
            "match_time",
            "field",
            "home_score_total",
            "away_score_total",
            "home_first_round_score",
            "home_second_round_score",
            "away_first_round_score",
            "away_second_round_score",
            "first_round",
            "second_round",
            "home_team",
            "away_team",
            "is_validated",
            "post_season",
            "match_type",
            "type_name",
            "seriers",
        )


class MatchTeamSerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField()

    def get_players(self, obj):
        return PlayerNameSerializer(
            obj.players.filter(
                playersinteam__team_season__season=self.context.get("season")
            ),
            many=True,
        ).data

    class Meta:
        model = TeamsInSeason
        fields = ("id", "current_name", "current_abbreviation", "players")


class MatchRoundSerializer(serializers.ModelSerializer):
    home = serializers.SerializerMethodField()
    away = serializers.SerializerMethodField()

    def get_home(self, qs):
        home_throws = qs.filter(team=self.context.get("home_team"))
        return ThrowScoreSerializer(home_throws, many=True).data

    def get_away(self, qs):
        away_throws = qs.filter(team=self.context.get("away_team"))
        return ThrowScoreSerializer(away_throws, many=True).data

    class Meta:
        model = Throw
        fields = ("home", "away")


class MatchScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = (
            "home_first_round_score",
            "home_second_round_score",
            "away_first_round_score",
            "away_second_round_score",
            "is_validated",
        )


class ThrowScoreSerializer(serializers.ModelSerializer):
    player = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()
    score_first = serializers.SerializerMethodField()
    score_second = serializers.SerializerMethodField()
    score_third = serializers.SerializerMethodField()
    score_fourth = serializers.SerializerMethodField()

    def get_player(self, obj):
        return UserSerializer(obj.player).data

    def get_score_first(self, obj):
        tmp_list = [
            obj.score_first,
            obj.score_second,
            obj.score_third,
            obj.score_fourth,
        ]
        scores = score_format(tmp_list)
        self.score_first, self.score_second, self.score_third, self.score_fourth = (
            scores
        )
        return self.score_first

    def get_score_second(self, obj):
        return self.score_second

    def get_score_third(self, obj):
        return self.score_third

    def get_score_fourth(self, obj):
        return self.score_fourth

    def get_score_total(self, obj):
        st = (
            int(obj.score_first)
            if obj.score_first is not None and obj.score_first.isnumeric()
            else 0
        )
        nd = (
            int(obj.score_second)
            if obj.score_second is not None and obj.score_second.isnumeric()
            else 0
        )
        rd = (
            int(obj.score_third)
            if obj.score_third is not None and obj.score_third.isnumeric()
            else 0
        )
        th = (
            int(obj.score_fourth)
            if obj.score_fourth is not None and obj.score_fourth.isnumeric()
            else 0
        )
        return st + nd + rd + th

    class Meta:
        model = Throw
        fields = (
            "id",
            "player",
            "score_first",
            "score_second",
            "score_third",
            "score_fourth",
            "score_total",
            "throw_turn",
        )


class ThrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Throw
        fields = (
            "score_first",
            "score_second",
            "score_third",
            "score_fourth",
            "player",
        )


class TeamsInSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamsInSeason
        fields = (
            "id",
            "bracket_placement",
            "super_weekend_bracket",
            "super_weekend_bracket_placement",
            "super_weekend_playoff_seed",
        )


class SuperWeekendSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperWeekend
        fields = (
            "id",
            "season",
            "winner",
            "super_weekend_no_brackets",
            "super_weekend_playoff_format",
        )


class TeamListSuperWeekendSerializer(serializers.ModelSerializer):
    matches_won = serializers.SerializerMethodField()
    matches_lost = serializers.SerializerMethodField()
    matches_tie = serializers.SerializerMethodField()
    matches_played = serializers.SerializerMethodField()
    score_total = serializers.SerializerMethodField()
    points_total = serializers.SerializerMethodField()
    match_average = serializers.SerializerMethodField()

    def count_match_results(self, obj):
        results_home = obj.home_matches.filter(
            is_validated=True, season=self.context.get("season"), match_type=31
        ).annotate(
            home=F("home_first_round_score") + F("home_second_round_score"),
            away=F("away_first_round_score") + F("away_second_round_score"),
        )
        results_away = obj.away_matches.filter(
            is_validated=True, season=self.context.get("season"), match_type=31
        ).annotate(
            home=F("home_first_round_score") + F("home_second_round_score"),
            away=F("away_first_round_score") + F("away_second_round_score"),
        )

        self.matches_won = (
            results_home.filter(home__lt=F("away")).count()
            + results_away.filter(away__lt=F("home")).count()
        )
        self.matches_lost = (
            results_home.filter(away__lt=F("home")).count()
            + results_away.filter(home__lt=F("away")).count()
        )
        self.matches_tie = (
            results_home.filter(home__exact=F("away")).count()
            + results_away.filter(home__exact=F("away")).count()
        )
        self.matches_played = self.matches_lost + self.matches_tie + self.matches_won

        match_score_home = results_home.aggregate(Sum("home"))["home__sum"]
        match_score_away = results_away.aggregate(Sum("away"))["away__sum"]
        if match_score_home is None and match_score_away is None:
            self.match_average = "NaN"
            return
        elif match_score_home is None:
            match_score_home = 0
        elif match_score_away is None:
            match_score_away = 0
        match_score_total = match_score_home + match_score_away
        self.match_average = (
            round(match_score_total / self.matches_played, 2)
            if self.matches_played
            else "NaN"
        )

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
        return (
            round(self.points_total / self.matches_played, 2)
            if self.matches_played
            else "NaN"
        )

    def get_score_total(self, obj):
        season = self.context.get("season")
        throws = Throw.objects.filter(match__is_validated=True, team=obj, season=season)
        return count_score_total(obj, season, throws, key="team")

    class Meta:
        model = TeamsInSeason
        fields = (
            "id",
            "current_name",
            "current_abbreviation",
            "matches_won",
            "matches_lost",
            "matches_tie",
            "matches_played",
            "score_total",
            "points_total",
            "match_average",
            "super_weekend_bracket",
            "super_weekend_bracket_placement",
            "super_weekend_playoff_seed",
        )


class AdminMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = "__all__"


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"

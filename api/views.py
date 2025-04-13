import json
from django.contrib.auth import login, logout
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, permissions, status, viewsets
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_swagger.views import get_swagger_view
from rest_framework.request import Request
import typing as t

from django.db.models.functions import Cast, Concat, Round

import kyykka.serializers as serializers
from kyykka.models import (
    CurrentSeason,
    Match,
    News,
    PlayersInTeam,
    Season,
    SuperWeekend,
    TeamsInSeason,
    Throw,
    User,
)
from django.core.cache import cache
from django.db.models import F, IntegerField, Sum, Q, Count, Case, When, Value, F, FloatField, CharField, SmallIntegerField, Max


from utils.caching import (
    cache_reset_key,
    getFromCache,
    reset_match_cache,
    reset_player_cache,
    setToCache,
)

schema_view = get_swagger_view(title="NKL API")

def get_current_season() -> Season:
    cache_value = cache.get("current_season", None)
    if cache_value is not None:
        return cache_value
    current = CurrentSeason.objects.first()
    if current is None:
        raise CurrentSeason.DoesNotExist
    cache.set("current_season", current.season, 60 * 60 * 12)
    return current.season


def getSeason(request: Request) -> Season | None:
    try:
        season_id = request.query_params.get("season", None)
        if season_id is None:
            return None
        season = cache.get(f"season_{season_id}", None)
        if season is not None:
            return season
        season = Season.objects.get(id=season_id)
        cache.set(f"season_{season_id}", season, 60 * 60 * 12)
        return season
    except (Season.DoesNotExist, ValueError):
        return None


def getPostseason(request: Request) -> bool | None:
    try:
        req_post_season = request.query_params.get("post_season", None)
        if req_post_season is None:
            return None
        return bool(int(req_post_season))
    except (ValueError, TypeError):
        return None

def getRole(user: User) -> t.Literal[0, 1, 2]:
    try:
        if user.is_superuser:
            return 2
        else:
            player_in_team: PlayersInTeam = user.playersinteam_set.get(  # type: ignore
                team_season__season=get_current_season()
            )
            assert isinstance(player_in_team, PlayersInTeam)
            if player_in_team.is_captain:
                return 1
            else:
                return 0
    except PlayersInTeam.DoesNotExist:
        return 0

def getSuper(request: Request) -> bool | None:
    try:
        request_param = request.query_params.get("super_weekend", None)
        if request_param is None:
            return None
        return bool(int(request_param))
    except (ValueError, TypeError):
        return None

@ensure_csrf_cookie
def csrf(request):
    return HttpResponse(status=status.HTTP_200_OK)


def ping(request):
    return JsonResponse({"result:": "pong"})


class IsCaptain(permissions.BasePermission):
    """
    Permission check to verify that user is captain in the right team.
    """

    def has_permission(self, request: Request, view):
        try:
            if request.user.is_superuser:
                return True
            return request.user.playersinteam_set.get(
                team_season__season=get_current_season()
            ).is_captain
        except PlayersInTeam.DoesNotExist:
            return False


class IsCaptainForThrow(permissions.BasePermission):
    """
    Permission check to verify if user is captain in the right team for updating throws

    Home team captain is only one allowed to modify the throws
    """

    def has_object_permission(self, request: Request, view, obj: Throw):
        try:
            if request.user.is_superuser:
                return True
            
            home_team_captain = obj.match.home_team.players.filter(is_captain=True).first()
            if home_team_captain is None:
                print(f"Team {obj.match.home_team} has no captain!")
                return False
            
            return request.user == home_team_captain.player
        except AttributeError:
            print("has_object_permission", request.user.id, obj)
            return False


class MatchDetailPermission(permissions.BasePermission):
    """
    If patching is_validated, user needs to be captain of the away_team
    Else user needs to be captain of the away_team (patchin round scores)
    """

    def has_object_permission(self, request:Request, view, obj: Throw):
        if request.user.is_superuser:
            return True
        if "is_validated" in request.data: # type: ignore
            away_captain = obj.match.away_team.players.filter(is_captain=True).first()
            if away_captain is None:
                print(f"Team {obj.match.away_team} has no captain!")
                return False
            return request.user == away_captain.player
        else:
            home_captain = obj.match.home_team.players.filter(is_captain=True).first()
            if home_captain is None:
                print(f"Team {obj.match.home_team} has no captain!")
                return False
            return request.user == home_captain.player


class IsSuperUserOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user.is_staff


class LoginAPI(generics.GenericAPIView):
    """
    Creates session for user upon successful login.
    This is per instance based. Logout in other
    browser does not end login session in other one.
    Set sessionid and CSRF to cookies
    Return User, role and team_id
    """

    serializer_class = serializers.LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        try:
            current = CurrentSeason.objects.first().season
            player_in_team = PlayersInTeam.objects.filter(
                player=user, team_season__season=current
            ).first()
            role = getRole(user)
            # role = '1' if player_in_team.is_captain else '0'
        except (PlayersInTeam.DoesNotExist, AttributeError):
            team_id = None
            role = 0
        response = Response(
            {
                "success": True,
                "user": serializers.UserSerializer(user).data,
                "role": role,
                "team_id": team_id,
            }
        )
        return response


class LogoutAPI(APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        response = HttpResponse(json.dumps({"success": True}))
        # response.delete_cookie('role')
        response.delete_cookie("csrftoken")
        return response


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = serializers.CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        success, message, user = serializer.save()
        login(request, user)
        return Response(
            {
                "success": success,
                "message": message,
                "user": serializers.UserSerializer(user).data,
                "role": "0",
            }
        )


class ReservePlayerAPI(generics.GenericAPIView):
    serializer_class = serializers.ReserveCreateSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsCaptain]

    def get(self, request):
        season = getSeason(request)
        queryset = User.objects.filter(is_superuser=False).order_by("first_name")
        serializer = serializers.ReserveListSerializer(
            queryset, many=True, context={"season": season}
        )
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        success, message = serializer.save()
        if success is False:
            return Response(
                {
                    "success": success,
                    "message": message,
                },
                status=400,
            )
        else:  # Success 200
            return Response(
                {
                    "success": success,
                    "message": message,
                }
            )


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all players that are in a team for the season beingh queried.
    """

    queryset = PlayersInTeam.objects.all()

    def list(self, request, format=None):
        season = getSeason(request)
        key = "all_players_" + str(season.year)
        all_data = getFromCache(key)
        if all_data is None:
            self.queryset = self.queryset.filter(team_season__season=season)
            data = serializers.PlayerListAllPositionSerializer(self.queryset, many=True).data
            total = serializers.PlayerListAllPositionSerializer(
                self.queryset, many=True, context={"season": season}
            ).data
            bracket = serializers.PlayerListAllPositionSerializer(
                self.queryset,
                many=True,
                context={"season": season, "post_season": False},
            ).data
            playoff = serializers.PlayerListAllPositionSerializer(
                self.queryset,
                many=True,
                context={"season": season, "post_season": True},
            ).data

            all_data = {
                "total": total,
                "bracket": bracket,
                "playoff": playoff,
            }
            setToCache(key, all_data)
        return Response(all_data)

    def retrieve(self, request, pk=None):
        # season = getSeason(request)
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = serializers.PlayerAllDetailSerializer(user)
        return Response(serializer.data)


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    queryset = TeamsInSeason.objects.all()

    def list(self, request):
        season = getSeason(request)
        post_season = getPostseason(request)
        super_weekend = getSuper(request)
        if post_season is None:
            if super_weekend is None:
                key = "all_teams_" + str(season.year)
                all_teams = getFromCache(key)
                if all_teams is None:
                    self.queryset = self.queryset.filter(season=season).distinct()
                    serializer = serializers.TeamListSerializer(
                        self.queryset, many=True, context={"season": season}
                    )
                    all_teams = serializer.data
                    setToCache(key, all_teams)
            else:
                key = "all_teams_super_weekend" + str(season.year)
                all_teams = getFromCache(key)
                if all_teams is None:
                    self.queryset = self.queryset.filter(
                        season=season, super_weekend_bracket__gte=1
                    ).distinct()
                    serializer = serializers.TeamListSuperWeekendSerializer(
                        self.queryset, many=True, context={"season": season}
                    )
                    all_teams = serializer.data
                    setToCache(key, all_teams)

        elif post_season is False:
            key = f"all_teams_{season.year}_regular_season"
            all_teams = getFromCache(key)
            if all_teams is None:
                self.queryset = self.queryset.filter(season=season).distinct()
                serializer = serializers.TeamListSerializer(
                    self.queryset,
                    many=True,
                    context={
                        "season": season,
                        "post_season": False,
                        "only_first_stage": True,
                    },
                )
                if season.playoff_format == 8:
                    seri = serializers.TeamListSerializer(
                        self.queryset,
                        many=True,
                        context={
                            "season": season,
                            "post_season": False,
                            "only_first_stage": False,
                        },
                    )
                    all_teams = [serializer.data, seri.data]
                else:
                    all_teams = serializer.data
                setToCache(key, all_teams)
        elif post_season is True:
            raise NotImplementedError
        return Response(all_teams)

    def retrieve(self, request, pk=None):
        try:
            # FIXME THIS should be done in some sort of serializer rather than here
            response_data = {
                "all_time": {
                    "score_total": 0,
                    "match_count": 0,
                    "pikes_total": 0,
                    "zeros_total": 0,
                    "throws_total": 0,
                    "gteSix_total": 0,
                    "zero_or_pike_first_throw_total": 0,
                    "players": [],
                    "matches": [],
                }
            }
            weighted_total = 0
            all_team_seasons = self.queryset.filter(team=team.first())
            players = {}
            player_weighted_total = {}
            for one_season in all_team_seasons.all():
                throws = Throw.objects.filter(match__is_validated=True, team=one_season)
                season = one_season.season
                context = {"season": season, "throws": throws}
                one_serializer = serializers.TeamDetailSerializer(
                    one_season, context=context
                )
                response_data[season.year] = one_serializer.data
                response_data["all_time"]["score_total"] += one_serializer.data[
                    "score_total"
                ]
                response_data["all_time"]["match_count"] += one_serializer.data[
                    "match_count"
                ]
                response_data["all_time"]["pikes_total"] += one_serializer.data[
                    "pikes_total"
                ]
                response_data["all_time"]["zeros_total"] += one_serializer.data[
                    "zeros_total"
                ]
                response_data["all_time"]["throws_total"] += one_serializer.data[
                    "throws_total"
                ]
                response_data["all_time"]["gteSix_total"] += one_serializer.data[
                    "gteSix_total"
                ]
                response_data["all_time"]["zero_or_pike_first_throw_total"] += (
                    one_serializer.data["zero_or_pike_first_throw_total"]
                )
                weighted_total += (
                    one_serializer.data["match_average"]
                    * one_serializer.data["match_count"]
                )
                response_data["all_time"]["matches"].extend(
                    one_serializer.data["matches"]
                )

                for player in one_serializer.data["players"]:
                    if player["player_name"] not in players:
                        players[player["player_name"]] = {
                            "id": player["id"],
                            "player_number": player["player_number"],
                            "score_total": 0,
                            "rounds_total": 0,
                            "pikes_total": 0,
                            "zeros_total": 0,
                            "throws_total": 0,
                            "scaled_points": 0,
                            "gteSix_total": 0,
                        }
                        player_weighted_total[player["player_name"]] = 0
                    players[player["player_name"]]["score_total"] += player[
                        "score_total"
                    ]
                    players[player["player_name"]]["rounds_total"] += player[
                        "rounds_total"
                    ]
                    players[player["player_name"]]["pikes_total"] += player[
                        "pikes_total"
                    ]
                    players[player["player_name"]]["zeros_total"] += player[
                        "zeros_total"
                    ]
                    players[player["player_name"]]["throws_total"] += player[
                        "throws_total"
                    ]
                    players[player["player_name"]]["scaled_points"] += (
                        player["scaled_points"]
                        if player["scaled_points"] is not None
                        else 0
                    )
                    players[player["player_name"]]["gteSix_total"] += player[
                        "gteSix_total"
                    ]
                    player_weighted_total[player["player_name"]] += (
                        player["throws_total"] * player["avg_throw_turn"]
                    )

            for name, stats in players.items():
                players[name]["score_per_throw"] = (
                    round(stats["score_total"] / stats["throws_total"], 2)
                    if stats["throws_total"]
                    else "NaN"
                )
                players[name]["avg_throw_turn"] = (
                    round(player_weighted_total[name] / stats["throws_total"], 2)
                    if stats["throws_total"]
                    else "NaN"
                )
                players[name]["scaled_points_per_throw"] = (
                    round(stats["scaled_points"] / stats["throws_total"], 2)
                    if stats["throws_total"]
                    else "NaN"
                )
                players[name]["pike_percentage"] = (
                    round(stats["pikes_total"] / stats["throws_total"] * 100, 2)
                    if stats["throws_total"]
                    else "NaN"
                )

            for name, stats in players.items():
                response_data["all_time"]["players"].append(
                    {"player_name": name, **stats}
                )
            response_data["all_time"]["match_average"] = (
                round(weighted_total / response_data["all_time"]["match_count"], 2)
                if response_data["all_time"]["match_count"]
                else "NaN"
            )
            response_data["all_time"]["pike_percentage"] = (
                round(
                    response_data["all_time"]["pikes_total"]
                    / response_data["all_time"]["throws_total"]
                    * 100,
                    2,
                )
                if response_data["all_time"]["throws_total"]
                else "NaN"
            )
            response_data["all_time"]["zero_percentage"] = (
                round(
                    response_data["all_time"]["zeros_total"]
                    / response_data["all_time"]["throws_total"]
                    * 100,
                    2,
                )
                if response_data["all_time"]["throws_total"]
                else "NaN"
            )
        except ValueError:
            # pk probably not integer?
            raise Http404
        # Do these querys only once here, instead of doing them 2 times at serializer.
        return Response(response_data)


class MatchList(APIView):
    """
    List all matches
    """

    # throttle_classes = [AnonRateThrottle]
    # queryset = Match.objects.filter(match_time__lt=datetime.datetime.now() + datetime.timedelta(weeks=2))
    queryset = Match.objects.all()

    def get(self, request):
        season = getSeason(request)
        super_weekend = getSuper(request)
        if not super_weekend:
            post_season = getPostseason(request)
            key = "all_matches_" + str(season.year)
            if post_season is not None:
                key += "_post_season" if post_season else "_regular_season"
            all_matches = getFromCache(key)
            if all_matches is None:
                if post_season is None:
                    self.queryset = self.queryset.filter(season=season)
                else:
                    self.queryset = self.queryset.filter(
                        season=season, post_season=post_season, match_type__lte=29
                    )
                serializer = serializers.MatchListSerializer(
                    self.queryset, many=True, context={"season": season}
                )
                all_matches = serializer.data
                setToCache(key, all_matches)
        else:
            key = "all_matches_super_weekend" + str(season.year)
            all_matches = getFromCache(key)
            if all_matches is None:
                self.queryset = self.queryset.filter(
                    season=season, match_type__gte=32
                ).filter(match_type__lte=39)
                serializer = serializers.MatchListSerializer(
                    self.queryset, many=True, context={"season": season}
                )
                all_matches = serializer.data
                setToCache(key, all_matches)

        return Response(all_matches)


class MatchDetail(APIView):
    """
    Retrieve or update a Match instance
    """

    # throttle_classes = [AnonRateThrottle]
    queryset = Match.objects.all()
    permission_classes = [MatchDetailPermission]

    def get(self, request, pk):
        season = getSeason(request)
        match = get_object_or_404(self.queryset, pk=pk)
        serializer = serializers.MatchDetailSerializer(
            match, context={"season": season}
        )
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        season = getSeason(request)
        match = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(request, match)
        # Update user session (so that it wont expire..)
        request.session.modified = True
        serializer = serializers.MatchScoreSerializer(
            match, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            player_ids = (
                match.throw_set.all().values_list("player__id", flat=True).distinct()
            )
            for id in player_ids:
                reset_player_cache(id, str(season.year))
            reset_match_cache(match, season_year=str(season.year))
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ThrowAPI(generics.GenericAPIView, UpdateModelMixin):
    serializer_class = serializers.ThrowSerializer
    queryset = Throw.objects.all()
    permission_classes = [IsAuthenticated, IsCaptain, IsCaptainForThrow]

    def patch(self, request, *args, **kwargs):
        cache_reset_key(
            "all_teams"
        )  # Updating throw score affects total score of team.
        return self.partial_update(request, *args, **kwargs)


class SeasonsAPI(generics.GenericAPIView):
    queryset = Season.objects.all()

    def get(self, request):
        key = "all_seasons"
        all_seasons = getFromCache(key)
        if all_seasons is None:
            all_seasons = serializers.SeasonSerializer(
                self.queryset.all(), many=True
            ).data
            print(all_seasons)
            setToCache(key, all_seasons)

        key = "current_season_ser"
        current_season = get_current_season()
        # TODO this serialzer maybe should be cached instead, but that's not that big deal IMO.
        current = serializers.SeasonSerializer(current_season).data

        return Response((all_seasons, current))


class SuperWeekendAPI(generics.GenericAPIView):
    queryset = SuperWeekend.objects.all()

    def get(self, request):
        try:
            season_id = request.query_params.get("season")
            if season_id:
                season = Season.objects.get(id=season_id)
            else:
                raise Season.DoesNotExist
        except (Season.DoesNotExist, ValueError):
            season = None
        if season is None:
            key = "all_superweekends"
            super_weekends = getFromCache(key)

            if super_weekends is None:
                super_weekends = serializers.SuperWeekendSerializer(
                    self.queryset, many=True
                ).data
                setToCache(key, super_weekends)
        else:
            key = f"superweekend_{str(season.year)}"
            super_weekends = getFromCache(key)

            if super_weekends is None:
                self.queryset = self.queryset.get(season=season)
                super_weekends = serializers.SuperWeekendSerializer(self.queryset).data
                setToCache(key, super_weekends)
        return Response(super_weekends)


class KyykkaAdminViewSet(generics.GenericAPIView, UpdateModelMixin):
    serializer_class = serializers.TeamsInSeasonSerializer
    queryset = TeamsInSeason.objects.all()
    permission_classes = [IsSuperUserOrAdmin]

    def patch(self, request, *args, **kwargs):
        cache_reset_key("all_teams")
        return self.partial_update(request, *args, **kwargs)


class KyykkaAdminMatchViewSet(generics.GenericAPIView):
    serializer_class = serializers.AdminMatchSerializer
    permission_classes = [IsSuperUserOrAdmin]

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"success": True, "message": ""})
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Something failed: {e}",
                },
                status=400,
            )


class KyykkaAdminSuperViewSet(generics.GenericAPIView, UpdateModelMixin):
    serializer_class = serializers.SuperWeekendSerializer
    queryset = SuperWeekend.objects.all()
    permission_classes = [IsSuperUserOrAdmin]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class NewsAPI(generics.GenericAPIView, UpdateModelMixin):
    serializer_class = serializers.NewsSerializer
    queryset = News.objects.all()

    def get(self, request):
        serializer = serializers.NewsSerializer(self.queryset.all(), many=True)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"success": True, "message": "Uusi uutinen onnistuneesti tehty!"}
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Something failed: {e}",
                },
                status=400,
            )


class ThrowsAPI(viewsets.ReadOnlyModelViewSet):
    queryset = Throw.objects.select_related("season", "team", "match").exclude(player__isnull=True)
    serializer_class = serializers.PlayerListSerializer

    def list(self, request: Request, format=None) -> Response:
        season_id = request.query_params.get("season", None)
        season: Season | None = None
        if season_id is not None:
            season = getSeason(request)
            self.queryset = self.queryset.filter(season=season)
        # TODO cache this bitch if already calculated once
        # TODO superweekend should be ignored
        throws = self.queryset.filter(match__match_type__lt=31, match__is_validated=True).alias(
            st=Cast("score_first", IntegerField()),
            nd=Cast("score_second", IntegerField()),
            rd=Cast("score_third", IntegerField()),
            th=Cast("score_fourth", IntegerField()),
            non_throws=Case(When(score_first='e', then=1), default=0)
                + Case(When(score_second='e', then=1), default=0)
                + Case(When(score_third='e', then=1), default=0)
                + Case(When(score_fourth='e', then=1), default=0),
            weighted_throw_count=F('throw_turn') * (4 - F('non_throws')),
            _scaled_points=(
                  (F("st") + F("nd")) * (9 + F("throw_turn"))
                + (F("rd") + F("th")) * (13 + F("throw_turn"))
            ) / 5,
        ).values("player").annotate(
            player_name=Concat("player__first_name", Value(" "), "player__last_name"),
            team_name=F("team__current_abbreviation"),
            throw_turn=F("throw_turn"),
            playoff=F("match__post_season"),
            score_total=Sum("st") + Sum("nd") + Sum("rd") + Sum("th"),
            pikes_total=Count("pk", filter=Q(score_first='h'))
                      + Count("pk", filter=Q(score_second='h'))
                      + Count("pk", filter=Q(score_third='h'))
                      + Count("pk", filter=Q(score_fourth='h')),
            zeros_total=Count("pk", filter=Q(score_first='0'))
                      + Count("pk", filter=Q(score_second='0'))
                      + Count("pk", filter=Q(score_third='0'))
                      + Count("pk", filter=Q(score_fourth='0')),
            gte_six_total=Count("pk", filter=Q(st__gte=6))
                        + Count("pk", filter=Q(nd__gte=6))
                        + Count("pk", filter=Q(rd__gte=6))
                        + Count("pk", filter=Q(th__gte=6)),
            match_count=Count("match", distinct=True),
            rounds_total=Count("pk"),
            throws_total=Count("pk") * 4 -Sum("non_throws"),
            scaled_points=Sum('_scaled_points'),
            weighted_throw_total=Sum("weighted_throw_count"),
            season=F("season__year")
        )
        ids = set([result["player"] for result in throws])
        
        # Add the players that haven't thrown at all
        players = PlayersInTeam.objects.select_related(
            "team_season__season", "player", "team_season"
        )
        
        throws = list(throws)

        if season is not None:
            players = players.filter(team_season__season=season)
        players = players.exclude(player__in=ids)
        for player in players:
            throws.append({
                "player": player.player.id, # type: ignore
                "player_name": f"{player.player.first_name} {player.player.last_name}",
                "team_name": player.team_season.current_abbreviation,
                "season": player.team_season.season.year,
                "playoff": False,
            })

        return Response(throws)
    
    def retrieve(self, request: Request, pk=None) -> Response | None:
        assert pk is not None
        players_data = self.queryset.filter(
            player=pk, match__match_type__lt=31, match__is_validated=True
        ).alias(
            st=Cast("score_first", IntegerField()),
            nd=Cast("score_second", IntegerField()),
            rd=Cast("score_third", IntegerField()),
            th=Cast("score_fourth", IntegerField()),
            non_throws=Case(When(score_first='e', then=1), default=0)
                     + Case(When(score_second='e', then=1), default=0)
                     + Case(When(score_third='e', then=1), default=0)
                     + Case(When(score_fourth='e', then=1), default=0),
            weighted_throw_count=F('throw_turn') * (4 - F('non_throws')),
            _scaled_points=(
                  (F("st") + F("nd")) * (9 + F("throw_turn"))
                + (F("rd") + F("th")) * (13 + F("throw_turn"))
            ) / 5,
            _score_total=F("st") + F("nd") + F("rd") + F("th"),
            _avg_round_score=F('_score_total') / (4 - F('non_throws')),
        )

        season_data = players_data.values("player").annotate(
            team_name=F("team__current_abbreviation"),
            score_total=Sum("_score_total"),
            pikes_total=Count("pk", filter=Q(score_first='h'))
                      + Count("pk", filter=Q(score_second='h'))
                      + Count("pk", filter=Q(score_third='h'))
                      + Count("pk", filter=Q(score_fourth='h')),
            zeros_total=Count("pk", filter=Q(score_first='0'))
                      + Count("pk", filter=Q(score_second='0'))
                      + Count("pk", filter=Q(score_third='0'))
                      + Count("pk", filter=Q(score_fourth='0')),
            ones_total=Count("pk", filter=Q(st=1))
                        + Count("pk", filter=Q(nd=1))
                        + Count("pk", filter=Q(rd=1))
                        + Count("pk", filter=Q(th=1)),
            twos_total=Count("pk", filter=Q(st=2))
                        + Count("pk", filter=Q(nd=2))
                        + Count("pk", filter=Q(rd=2))
                        + Count("pk", filter=Q(th=2)),
            threes_total=Count("pk", filter=Q(st=3))
                        + Count("pk", filter=Q(nd=3))
                        + Count("pk", filter=Q(rd=3))
                        + Count("pk", filter=Q(th=3)),
            fours_total=Count("pk", filter=Q(st=4))
                        + Count("pk", filter=Q(nd=4))
                        + Count("pk", filter=Q(rd=4))
                        + Count("pk", filter=Q(th=4)), 
            fives_total=Count("pk", filter=Q(st=5))
                        + Count("pk", filter=Q(nd=5))
                        + Count("pk", filter=Q(rd=5))
                        + Count("pk", filter=Q(th=5)),         
            gte_six_total=Count("pk", filter=Q(st__gte=6))
                        + Count("pk", filter=Q(nd__gte=6))
                        + Count("pk", filter=Q(rd__gte=6))
                        + Count("pk", filter=Q(th__gte=6)),
            match_count=Count("match", distinct=True),
            rounds_total=Count("pk"),
            throws_total=Count("pk") * 4 - Sum("non_throws"),
            scaled_points=Sum('_scaled_points'),
            weighted_throw_total=Sum("weighted_throw_count"),
            season=F("season__year"),
            position_one_throws=(
                4*Count("pk", filter=Q(throw_turn=1)) - Sum("non_throws", filter=Q(throw_turn=1))
            ),
            position_two_throws=(
                4*Count("pk", filter=Q(throw_turn=2)) - Sum("non_throws", filter=Q(throw_turn=2))
            ),
            position_three_throws=(
                4*Count("pk", filter=Q(throw_turn=3)) - Sum("non_throws", filter=Q(throw_turn=3))
            ),
            position_four_throws=(
                4*Count("pk", filter=Q(throw_turn=4)) - Sum("non_throws", filter=Q(throw_turn=4))
            ),
            avg_score=Case(
                When(throws_total__gt=0, then=Round(
                    F("score_total") / F("throws_total"), 
                    precision=2
                )),
                output_field=FloatField(),
            ),
            avg_scaled_points=Case(
                When(throws_total__gt=0, then=Round(
                        F("scaled_points") / F("throws_total"),
                        precision=2
                )),
                output_field=FloatField(),
            ),
            avg_position=Case(
                When(throws_total__gt=0, then=Round(
                        F("weighted_throw_total") / F("throws_total"), 
                        precision=2,
                )),
                output_field=FloatField(),
            ),
            pike_percentage=Case(
                When(throws_total__gt=0, then=Round(
                    F("pikes_total") / F("throws_total") * 100,
                    precision=2
                )),
                output_field=FloatField(),
            ),
            avg_score_position_one=Case(
                When(position_one_throws__gt=0, then=Round(
                    Sum("_score_total", filter=Q(throw_turn=1)) / F("position_one_throws"),
                    precision=2,
                )),
                output_field=FloatField(),
            ),
            avg_score_position_two=Case(
                When(position_two_throws__gt=0, then=Round(
                    Sum("_score_total", filter=Q(throw_turn=2)) / F("position_two_throws"),
                    precision=2,
                )),
                output_field=FloatField(),
            ),
            avg_score_position_three=Case(
                When(position_three_throws__gt=0, then=Round(
                    Sum("_score_total", filter=Q(throw_turn=3)) / F("position_three_throws"),
                    precision=2,
                )),
                output_field=FloatField(),
            ),
            avg_score_position_four=Case(
                When(position_four_throws__gt=0, then=Round(
                    Sum("_score_total", filter=Q(throw_turn=4)) / F("position_four_throws"),
                    precision=2,
                )),
                output_field=FloatField(),
            ),
        ).order_by("season")

        all_time_stats = season_data.aggregate(
            season_count=Count("season"),
            matches=Sum("match_count"),
            rounds=Sum("rounds_total"),
            throws=Sum("throws_total"),
            pikes=Sum("pikes_total"),
            zeros=Sum("zeros_total"),
            scores=Sum("score_total"),
            gte_six=Sum("gte_six_total"),
            scaled_points_total=Sum('scaled_points'),
            avg_score=Case(
                When(throws__gt=0, then=Round(F("scores") / F("throws"), precision=2)),
                output_field=FloatField(),
            ),
            avg_scaled_points=Case(
                When(throws__gt=0, then=Round(F("scaled_points_total") / F("throws"), precision=2)),
                output_field=FloatField(),
            ),
            avg_position=Case(
                When(throws__gt=0, then=Round(Sum("weighted_throw_total") / F("throws"), precision=2)),
                output_field=FloatField(),
            ),
            pike_percentage=Case(
                When(throws__gt=0, then=Round(F("pikes") / F("throws") * 100, precision=2)),
                output_field=FloatField(),
            ),
        )
        user = User.objects.get(pk=pk)

        matches_per_period = players_data.annotate(
            own_team_score=Case(
                When(
                    match__home_team=F("team"),
                    then=Case(When(
                        throw_round=1, 
                        then=F("match__home_first_round_score")),
                        default=F("match__home_second_round_score")
                    )
                ),
                When(
                    match__away_team=F("team"),
                    then=Case(When(
                        throw_round=1,
                        then=F("match__away_first_round_score")),
                        default=F("match__away_second_round_score")
                    )
                ),
                output_field=SmallIntegerField(),
            ),
            opponent_score=Case(
                When(
                    match__home_team=F("team"),
                    then=Case(When(
                        throw_round=1,
                        then=F("match__away_first_round_score")),
                        default=F("match__away_second_round_score")
                    )
                ),
                When(
                    match__away_team=F("team"),
                    then=Case(When(
                        throw_round=1,
                        then=F("match__home_first_round_score")),
                        default=F("match__home_second_round_score")
                    )
                ),
                output_field=SmallIntegerField(),
            ),
            score=F("_score_total"),
            oppenent_name=Case(
                When(match__home_team=F("team"), then=F("match__away_team__current_abbreviation")),
                default=F("match__home_team__current_abbreviation"),
                output_field=CharField(), 
            ),
            time=F('match__match_time'),
            avg_round_score=Round(F('_avg_round_score'), precision=2, output_field=FloatField()),
            season_name=F("season__year"),
        )


        matches_both_periods = players_data.alias(
            first=Case(
                When(throw_round=1, then=F("score_first")),
                default=Value("-"),
                output_field=CharField(),
            ),
            second=Case(
                When(throw_round=1, then=F("score_second")),
                default=Value("-"),
                output_field=CharField(),
            ),
            third=Case(
                When(throw_round=1, then=F("score_third")),
                default=Value("-"),
                output_field=CharField(),
            ),
            fourth=Case(
                When(throw_round=1, then=F("score_fourth")),
                default=Value("-"),
                output_field=CharField(),
            ),
            fifth=Case(
                When(throw_round=2, then=F("score_first")),
                default=Value("-"),
                output_field=CharField(),
            ),
            sixth=Case(
                When(throw_round=2, then=F("score_second")),
                default=Value("-"),
                output_field=CharField(),
            ),
            seventh=Case(
                When(throw_round=2, then=F("score_third")),
                default=Value("-"),
                output_field=CharField(),
            ),
            eighth=Case(
                When(throw_round=2, then=F("score_fourth")),
                default=Value("-"),
                output_field=CharField(),
            ),
            position_one=Case(
                When(throw_round=1, then=F("throw_turn")),
                default=Value("-"),
                output_field=CharField(),
            ),
            position_two=Case(
                When(throw_round=2, then=F("throw_turn")),
                default=Value("-"),
                output_field=CharField(),
            ),
        ).values('match', 'season').annotate(
            time=F('match__match_time'),
            opponent_name=Case(
                When(match__home_team=F("team"), then=F("match__away_team__current_abbreviation")),
                default=F("match__home_team__current_abbreviation"),
                output_field=CharField(), 
            ),
            position_one=Max("position_one"),
            position_two=Max("position_two"),
            score=Sum("_score_total"),
            first=Max("first"),
            second=Max("second"),
            third=Max("third"),
            fourth=Max("fourth"),
            fifth=Max("fifth"),
            sixth=Max("sixth"),
            seventh=Max("seventh"),
            eighth=Max("eighth"),
            score_per_throw=Round(
                F("score") / (4*Count("pk") - Sum("non_throws")),
                precision=2,
                output_field=FloatField()
            ),
            own_team_score=Case(
                When(
                    match__home_team=F("team"),
                    then=F("match__home_first_round_score") + F("match__home_second_round_score"),
                ),
                default=F("match__away_first_round_score") + F("match__away_second_round_score"),
                output_field=SmallIntegerField(),
            ),
            opponent_score=Case(
                When(
                    match__home_team=F("team"),
                    then=F("match__away_first_round_score") + F("match__away_second_round_score"),
                ),
                default=F("match__home_first_round_score") + F("match__home_second_round_score"),
                output_field=SmallIntegerField(),
            ),
        )

        return Response({
            "id" : user.pk,
            "player_name" : f"{user.first_name} {user.last_name}",
            "stats_per_seasons": season_data,
            "all_time_stats": all_time_stats,
            # .values() needed, as the query doesn't have one yet.
            "matches_per_period": matches_per_period.values(),
            "matches_both_periods": matches_both_periods,
        })


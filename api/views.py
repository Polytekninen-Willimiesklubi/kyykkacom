import datetime
import json

from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from kyykka.models import (CurrentSeason, Match, Player, PlayersInTeam, Season, Team, 
                           TeamsInSeason, Throw, User)
from kyykka.serializers import *
from rest_framework import generics, permissions, status, viewsets
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_swagger.views import get_swagger_view
from utils.caching import (cache_reset_key, getFromCache, reset_match_cache,
                           setToCache, reset_player_cache)

schema_view = get_swagger_view(title='NKL API')


def getSeason(request):
    try:
        season_id = request.query_params.get('season')
        if season_id:
            season = Season.objects.get(id=season_id)
        else:
            raise Season.DoesNotExist
    except (Season.DoesNotExist, ValueError):
        season = CurrentSeason.objects.first().season
    return season

def getPostseason(request):
    try:
        post_season = bool(int(request.query_params.get('post_season')))
    except (ValueError, TypeError):
        post_season = None
    return post_season

def getRole(user):
    try:
        if user.playersinteam_set.get(team_season__season=CurrentSeason.objects.first().season).is_captain:
            role = '1'
        else:
            role = '0'
    except PlayersInTeam.DoesNotExist as e:
        role = '0'
    return role

def getSuper(request):
    try:
        super_weekend = bool(int(request.query_params.get('super_weekend')))
    except (ValueError, TypeError):
        super_weekend = None
    return super_weekend


@ensure_csrf_cookie
def csrf(request):
    return HttpResponse(status=status.HTTP_200_OK)


def ping(request):
    return JsonResponse({'result:': 'pong'})


class IsCaptain(permissions.BasePermission):
    """
    Permission check to verify that user is captain in the right team.
    """
    def has_permission(self, request, view):
        try:
            if request.user.is_superuser:
                return True
            return request.user.playersinteam_set.get(team_season__season=CurrentSeason.objects.first().season).is_captain
        except PlayersInTeam.DoesNotExist as e:
            return False


class IsCaptainForThrow(permissions.BasePermission):
    """
    Permission check to verify if user is captain in the right team for updaing throws
    """
    def has_object_permission(self, request, view, obj):
        try:
            if request.user.is_superuser:
                return True
            return request.user == obj.match.home_team.playersinteam_set.filter(
                team_season__season=CurrentSeason.objects.first().season,
                is_captain=True
            ).first().player
        except AttributeError as e:
            print('has_object_permission', request.user.id, obj)
            return False


class MatchDetailPermission(permissions.BasePermission):
    """
    If patching is_validated, user needs to be captain of the away_team
    Else user needs to be captain of the away_team (patchin round scores)
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if 'is_validated' in request.data and len(request.data) == 1:
            return request.user == obj.away_team.playersinteam_set.filter(team_season__season=CurrentSeason.objects.first().season,
                                                                          is_captain=True).first().player
        if 'is_validated' not in request.data:
            return request.user == obj.home_team.playersinteam_set.filter(team_season__season=CurrentSeason.objects.first().season,
                                                                          is_captain=True).first().player

class IsSuperUserOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user.is_staff

# @method_decorator(ensure_csrf_cookie, name='dispatch')
# @method_decorator(csrf_protect, name='dispatch')
class LoginAPI(generics.GenericAPIView):
    # TODO: Verify what happens if eg. two browsers are used, and session ends in other one. 
    """
    Creates session for user upon successful login
    Set sessionid and CSRF to cookies
    Return User, role and team_id
    """
    serializer_class = LoginUserSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        # role = getRole(user)
        try:
            current = CurrentSeason.objects.first().season
            player_in_team = PlayersInTeam.objects.get(player=user, team_season__season=current)
            team_id = player_in_team.team_season.id
            if player_in_team.is_captain:
                role = '1'
            else:
                role = '0'
        except (PlayersInTeam.DoesNotExist, AttributeError) as e:
            team_id = None
            role = '0'
        response = Response({
            'success': True,
            'user': UserSerializer(user).data,
            'role': role,
            'team_id': team_id
            })
        return response


class LogoutAPI(APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        response = HttpResponse(json.dumps({'success': True}))
        # response.delete_cookie('role')
        response.delete_cookie('csrftoken')
        return response


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        success, message, user = serializer.save()
        login(request, user)
        return Response({
            'success': success,
            'message': message,
            'user': UserSerializer(user).data,
            'role': '0'
        })


class ReservePlayerAPI(generics.GenericAPIView):
    serializer_class = ReserveCreateSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsCaptain]

    def get(self, request):
        season = getSeason(request)
        queryset = User.objects.filter(is_superuser=False).order_by("first_name")
        serializer = ReserveListSerializer(queryset, many=True, context={'season': season})
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        success, message = serializer.save()
        if success is False:
            return Response({
            'success': success,
            'message': message,
            }, status=400)
        else: # Success 200
            return Response({
                'success': success,
                'message': message,
            })


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all players that are in a team for the season beingh queried. 
    """
    queryset = User.objects.all()

    def list(self, request, format=None):
        season = getSeason(request)
        key = 'all_players_' + str(season.year)
        all_players = getFromCache(key)
        if all_players is None:
            self.queryset = self.queryset.filter(playersinteam__team_season__season=season)
            serializer = PlayerListSerializer(self.queryset, many=True, context={'season': season})
            all_players = serializer.data
            setToCache(key, all_players)
        return Response(all_players)

    def retrieve(self, request, pk=None):
        season = getSeason(request)
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = PlayerAllDetailSerializer(user)
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
        if post_season == None:
            if super_weekend == None:
                key = 'all_teams_' + str(season.year)
                all_teams = getFromCache(key)
                if all_teams is None:
                    self.queryset = self.queryset.filter(season=season).distinct()
                    serializer = TeamListSerializer(self.queryset, many=True, context={'season': season})
                    all_teams = serializer.data
                    setToCache(key, all_teams)
            else:
                key = 'all_teams_super_weekend' + str(season.year)
                all_teams = getFromCache(key)
                if all_teams is None:
                    self.queryset = self.queryset.filter(season=season, super_weekend_bracket__gte=1).distinct()
                    serializer = TeamListSuperWeekendSerializer(self.queryset, many=True, context={'season': season})
                    all_teams = serializer.data
                    setToCache(key, all_teams)
    
        elif post_season == False:
            key = f'all_teams_{season.year}_regular_season'
            all_teams = getFromCache(key)
            if all_teams is None:
                self.queryset = self.queryset.filter(season=season).distinct()
                serializer = TeamListSerializer(self.queryset, many=True, context={'season': season, 'post_season': False})
                all_teams = serializer.data
                setToCache(key, all_teams)
        elif post_season == True:
            raise NotImplementedError
        return Response(all_teams)

    def retrieve(self, request, pk=None):
        season = getSeason(request)
        try:
            team = get_object_or_404(self.queryset, pk=pk)
        except ValueError:
            # pk probably not integer?
            raise Http404
        # Do these querys only once here, instead of doing them 2 times at serializer.
        throws = Throw.objects.filter(match__is_validated=True, season=season, team=team)
        context = {
            'season': season,
            'throws':  throws
        }
        serializer = TeamDetailSerializer(team, context=context)
        return Response(serializer.data)


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
            key = 'all_matches_' + str(season.year)
            if post_season is not None:
                key += '_post_season' if post_season else '_regular_season'
            all_matches = getFromCache(key)
            if all_matches is None:
                if post_season is None:
                    self.queryset = self.queryset.filter(season=season)
                else:
                    self.queryset = self.queryset.filter(season=season, post_season=post_season, match_type__lte=29)
                serializer = MatchListSerializer(self.queryset, many=True, context={'season': season})
                all_matches = serializer.data
                setToCache(key, all_matches)
        else:
            key = "all_matches_super_weekend" + str(season.year)
            all_matches = getFromCache(key)
            if all_matches is None:
                self.queryset = self.queryset.filter(season=season, match_type__gte=30).filter(match_type__lte=39)
                serializer = MatchListSerializer(self.queryset, many=True, context={'season': season})
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
        serializer = MatchDetailSerializer(match, context={'season': season})
        return Response(serializer.data)

    def patch(self, request, pk ,format=None):
        season = getSeason(request)
        match = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(request, match)
        # Update user session (so that it wont expire..)
        request.session.modified = True
        serializer = MatchScoreSerializer(match, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            player_ids = match.throw_set.all().values_list("player__id", flat=True).distinct()
            for id in player_ids:
                reset_player_cache(id, str(season.year))
            reset_match_cache(match, season_year=str(season.year))
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ThrowAPI(generics.GenericAPIView, UpdateModelMixin):
    serializer_class = ThrowSerializer
    queryset = Throw.objects.all()
    permission_classes = [IsAuthenticated, IsCaptain, IsCaptainForThrow]

    def patch(self, request, *args, **kwargs):
        cache_reset_key('all_teams')  # Updating throw score affects total score of team.
        return self.partial_update(request, *args, **kwargs)
    
class SeasonsAPI(generics.GenericAPIView):
    queryset = Season.objects.all()

    def get(self, request):
        key = 'all_seasons'
        all_seasons = getFromCache(key)
        if all_seasons is None:
            all_seasons = SeasonSerializer(self.queryset.all(), many=True).data
            setToCache(key, all_seasons)
       
        key = 'current_season'
        current_season = getFromCache(key)
        if current_season is None:
            current = CurrentSeason.objects.first().season
            current_season = SeasonSerializer(current).data
            setToCache(key, current_season)

        return Response((all_seasons, current_season))
    
class SuperWeekendAPI(generics.GenericAPIView):
    queryset = SuperWeekend.objects.all()

    def get(self, request):
        try:
            season_id = request.query_params.get('season')
            if season_id:
                season = Season.objects.get(id=season_id)
            else:
                raise Season.DoesNotExist
        except (Season.DoesNotExist, ValueError):
            season = None
        if season is None:
            key = 'all_superweekends'
            super_weekends = getFromCache(key)

            if super_weekends is None:
                super_weekends = SuperWeekendSerializer(self.queryset.all(), many=True).data
                setToCache(key, super_weekends)
        else:
            key = f'superweekend_{str(season.year)}'
            super_weekends = getFromCache(key)

            if super_weekends is None:
                self.queryset = self.queryset.get(season=season)
                super_weekends = SuperWeekendSerializer(self.queryset).data
                setToCache(key, super_weekends)
        return Response(super_weekends)

class KyykkaAdminViewSet(generics.GenericAPIView, UpdateModelMixin):
    serializer_class = TeamsInSeasonSerializer
    queryset = TeamsInSeason.objects.all()
    permission_classes = [IsSuperUserOrAdmin]

    def patch(self, request, *args, **kwargs):
        cache_reset_key('all_teams')
        return self.partial_update(request, *args, **kwargs)
    
class KyykkaAdminMatchViewSet(generics.GenericAPIView):
    serializer_class = AdminMatchSerializer
    permission_classes = [IsSuperUserOrAdmin]

    def post(self, request, *args, **kwargs):
        try:

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'success': True,
                'message': ''
            })
        except Exception as e:
            return Response({
            'success': False,
            'message': f'Something failed: {e}',
            }, status=400)
        
class KyykkaAdminSuperViewSet(generics.GenericAPIView, UpdateModelMixin):
    serializer_class = SuperWeekendSerializer
    queryset = SuperWeekend.objects.all()
    permission_classes = [IsSuperUserOrAdmin]

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
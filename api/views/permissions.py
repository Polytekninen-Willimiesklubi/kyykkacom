"""Permission classes for API views."""

from __future__ import annotations

import typing as t

from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import permissions, status

from kyykka.models import CurrentSeason, PlayersInTeam, Throw

from .utils.getters import get_current_season

if t.TYPE_CHECKING:
    from rest_framework.request import Request

    from kyykka.models import Throw


@ensure_csrf_cookie
def csrf(request):
    return HttpResponse(status=status.HTTP_200_OK)


class IsCaptain(permissions.BasePermission):
    """
    Permission check to verify that user is captain in the right team.
    """

    def has_permission(self, request: Request, view) -> bool:
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

            home_team_captain = obj.match.home_team.players.filter(
                is_captain=True
            ).first()
            if home_team_captain is None:
                print(f"Team {obj.match.home_team} has no captain!")
                return False

            return request.user == home_team_captain.player
        except AttributeError:
            print("has_object_permission", request.user.id, obj)
            return False


class IsCaptainForTeam(permissions.BasePermission):
    """Permission check to verify if user is captain in the right team for reserving players"""

    def has_permission(self, request: Request, view):
        # if request.user.is_superuser:
        #     return True
        try:
            current = CurrentSeason.objects.first()
            assert current is not None
            player = PlayersInTeam.objects.filter(
                team_season__season=current.season, player=request.user
            ).first()
            team_id = request.query_params.get("team", None)
            if player is None or team_id is None:
                return None
            return player.is_captain and player.team_season.team.pk == int(team_id)
        except (ValueError, TypeError):
            return None
        except AttributeError:
            print("has_permission", request.user.id)
            return False


class MatchDetailPermission(permissions.BasePermission):
    """
    If patching is_validated, user needs to be captain of the away_team
    Else user needs to be captain of the away_team (patchin round scores)
    """

    def has_object_permission(self, request: Request, view, obj: Throw) -> bool:
        if request.user.is_superuser:
            return True
        if "is_validated" in request.data:  # type: ignore
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
    def has_object_permission(self, request, view, obj) -> bool:
        return request.user.is_superuser or request.user.is_staff

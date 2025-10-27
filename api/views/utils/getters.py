from __future__ import annotations

import typing as t

from django.core.cache import cache
from django.http import Http404

from kyykka.models import CurrentSeason, PlayersInTeam, Season, User

if t.TYPE_CHECKING:
    from rest_framework.request import Request


def get_current_season() -> Season:
    cache_value = cache.get("current_season", None)
    if cache_value is not None:
        return cache_value
    current = CurrentSeason.objects.first()
    if current is None:
        raise CurrentSeason.DoesNotExist
    cache.set("current_season", current.season, 60 * 60 * 12)
    return current.season


def get_season(request: Request, required: bool = False) -> Season | None:
    """Get the current season from the request query parameters or cache.

    Raises:
        `Http404` if the season ID does not exist or not provided and required.
    """
    try:
        season_id = request.query_params.get("season", None)
        if season_id is None:
            if required:
                raise Http404(
                    "Season ID was not provided in the request, but was required."
                )
            return None
        season = cache.get(f"season_{season_id}", None)
        if season is not None:
            return season
        season = Season.objects.get(id=season_id)
        cache.set(f"season_{season_id}", season, 60 * 60 * 12)
        return season
    except Season.DoesNotExist:
        raise Http404("Season with the provided ID does not exist.")


def get_post_season(request: Request) -> bool | None:
    try:
        req_post_season = request.query_params.get("post_season", None)
        if req_post_season is None:
            return None
        return bool(int(req_post_season))
    except (ValueError, TypeError):
        return None


def get_role(user: User) -> t.Literal[0, 1, 2]:
    """Returns the role of the user:
    `0`: **Not a captain**
    `1`: **Captain**
    `2`: **Super user**
    """
    if user.is_superuser:
        return 2
    try:
        player_in_team = user.playersinteam_set.get(  # pyright: ignore
            team_season__season=get_current_season()
        )
    except PlayersInTeam.DoesNotExist:
        return 0
    assert isinstance(player_in_team, PlayersInTeam)
    return 1 if player_in_team.is_captain else 0


def get_super(request: Request) -> bool | None:
    try:
        request_param = request.query_params.get("super_weekend", None)
        if request_param is None:
            return None
        return bool(int(request_param))
    except (ValueError, TypeError):
        return None

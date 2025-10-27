import typing as t
from functools import wraps

from django.core.cache import cache


def cached_method(key: str, inserts: list[str], timeout: int = 3600 * 12):
    def decorator(func):
        @wraps(func)
        def wrapper(self, obj, *args, **kwargs):
            nonlocal key
            if inserts:
                for insert_key in inserts:
                    insert_val = None
                    for attr in insert_key.split("."):
                        insert_val = getattr(obj, attr, None)
                        if insert_val is None:
                            raise AttributeError(
                                f"Attribute {attr} not found when trying to build cache key."
                            )
                    assert insert_val is not None, "Insert value cannot be None"
                    key = key.format(insert_val)

            cached_val = cache.get(key)
            if cached_val is not None:
                return cached_val

            val = func(self, obj, *args, **kwargs)
            cache.set(key, val, timeout)
            return val

        return wrapper

    return decorator


def getFromCache(key, season_year=None) -> t.Any | None:
    if season_year:
        key = key + "_" + str(season_year)
    # print("Get cache", key, cache.get(key))
    return cache.get(key, None)


def setToCache(key, value, timeout=60 * 60 * 12, season_year=""):
    if value is None:
        value = 0
    if season_year:
        key = key + "_" + str(season_year)
    # print("Set cache", key, value)
    cache.set(key, value, timeout)


def reset_player_cache(player_id, season_year):
    """
    Resets all player_ caches for specified season
    """
    caches = [
        "player_" + str(player_id) + "_score_total_" + season_year,
        "player_" + str(player_id) + "_match_count_" + season_year,
        "player_" + str(player_id) + "_rounds_total_" + season_year,
        "player_" + str(player_id) + "_pikes_total_" + season_year,
        "player_" + str(player_id) + "_zeros_total_" + season_year,
        "player_" + str(player_id) + "_gteSix_total_" + season_year,
        "player_" + str(player_id) + "_throws_total_" + season_year,
        "player_" + str(player_id) + "_pike_percentage_" + season_year,
        "player_" + str(player_id) + "_score_per_throw_" + season_year,
        "player_" + str(player_id) + "_avg_throw_turn_" + season_year,
    ]
    # print("Removing player caches", caches)
    cache.delete_many(caches)


def reset_match_cache(match, season_year=""):
    """
    If the match is validated, stats of teams and players are affected as well.
    """
    caches = [
        "match_" + str(match.id) + "_home_score_total",
        "match_" + str(match.id) + "_away_score_total",
        "all_matches_" + season_year,
        "all_teams_" + season_year,
        "all_players_" + season_year,
    ]
    # print(caches)
    cache.delete_many(caches)


def cache_reset_key(key):
    cache.delete(key)

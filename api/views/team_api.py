import typing as t

from django.db.models import (
    Case,
    CharField,
    Count,
    F,
    FloatField,
    Min,
    Q,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Concat, Round
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.response import Response

import kyykka.serializers as serializers
from kyykka.models import (
    MATCH_TYPES,
    Match,
    PlayersInTeam,
    TeamsInSeason,
    Throw,
)

from .utils.getters import get_season
from .utils.query_helpers import (
    casted_score_fields,
    count_field_total,
    count_non_throws,
    get_correct_match_score,
    get_correct_round_score,
    rounded_divison,
    scaled_points,
    score_fields,
    scores_casted_to_int,
)


@extend_schema_view(
    list=extend_schema(
        tags=["teams"],
        description="List all teams with their stats. Returns team performance metrics including matches won/lost, scores, etc.",
        parameters=[
            OpenApiParameter(
                name="season",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Season ID to filter teams by",
            ),
            OpenApiParameter(
                name="post_season",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter teams by post-season status",
            ),
            OpenApiParameter(
                name="super_weekend",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter teams by super weekend status",
            ),
        ],
        responses={200: serializers.TeamsInSeasonSerializer},
    ),
    retrieve=extend_schema(
        tags=["teams"],
        description="Get detailed stats for a specific team including all-time stats, player stats, and match history.",
        responses={200: serializers.TeamsInSeasonSerializer},
    ),
)
class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """

    queryset = TeamsInSeason.objects.select_related("team").all()

    # TODO invalidate cache when match scores are updated
    @method_decorator(cache_page(3600 * 12))
    def list(self, request):
        # other_queryset = Match.objects.filter(is_validated=True)
        season = get_season(request)
        # post_season = get_post_season(request)
        # super_weekend = get_super(request)

        if season is not None:
            self.queryset = self.queryset.filter(season=season)

        # if post_season:
        #     other_queryset = other_queryset.filter(post_season=post_season, match_type=1)
        # elif post_season is False:
        #     other_queryset = other_queryset.filter(post_season=post_season)

        # if super_weekend:
        #     other_queryset = other_queryset.filter(match_type__gte=30)
        # elif super_weekend is False:
        #     other_queryset = other_queryset.filter(match_type__lt=30)

        home_results = (
            self.queryset.alias(
                home_score=F("home_matches__home_first_round_score")
                + F("home_matches__home_second_round_score"),
                home_opp_score=F("home_matches__away_first_round_score")
                + F("home_matches__away_second_round_score"),
                home_id=F("home_matches__pk"),
                best_round_match=Case(
                    When(
                        home_matches__home_first_round_score__lt=F(
                            "home_matches__home_second_round_score"
                        ),
                        then=F("home_matches__home_first_round_score"),
                    ),
                    default=F("home_matches__home_second_round_score"),
                ),
            )
            .values("id", "current_name", "current_abbreviation", "team_id", "bracket")
            .annotate(
                matches_lost=Count(
                    "home_id", filter=Q(home_score__gt=F("home_opp_score"))
                ),
                matches_won=Count(
                    "home_id", filter=Q(home_score__lt=F("home_opp_score"))
                ),
                matches_tie=Count(
                    "home_id", filter=Q(home_score__exact=F("home_opp_score"))
                ),
                matches_played=F("matches_lost") + F("matches_won") + F("matches_tie"),
                weighted_sum=Sum("home_score"),
                best_round=Min("best_round_match"),
                best_match=Min("home_score"),
                clearences=(
                    Count(
                        "home_id", filter=Q(home_matches__home_first_round_score__lte=0)
                    )
                    + Count(
                        "home_id",
                        filter=Q(home_matches__home_second_round_score__lte=0),
                    )
                ),
                points_total=F("matches_won") * 2 + F("matches_tie"),
            )
        )

        away_results = (
            self.queryset.alias(
                away_score=F("away_matches__away_first_round_score")
                + F("away_matches__away_second_round_score"),
                away_opp_score=F("away_matches__home_first_round_score")
                + F("away_matches__home_second_round_score"),
                away_id=F("away_matches__pk"),
                best_round_match=Case(
                    When(
                        away_matches__away_first_round_score__lt=F(
                            "away_matches__away_second_round_score"
                        ),
                        then=F("away_matches__away_first_round_score"),
                    ),
                    default=F("away_matches__away_second_round_score"),
                ),
            )
            .values("id", "current_name", "current_abbreviation", "team_id", "bracket")
            .annotate(
                matches_lost=Count(
                    "away_id", filter=Q(away_score__gt=F("away_opp_score"))
                ),
                matches_won=Count(
                    "away_id", filter=Q(away_score__lt=F("away_opp_score"))
                ),
                matches_tie=Count(
                    "away_id", filter=Q(away_score__exact=F("away_opp_score"))
                ),
                matches_played=F("matches_lost") + F("matches_won") + F("matches_tie"),
                weighted_sum=Sum("away_score"),
                best_round=Min("best_round_match"),
                best_match=Min("away_score"),
                clearences=(
                    Count(
                        "away_id", filter=Q(away_matches__away_first_round_score__lte=0)
                    )
                    + Count(
                        "away_id",
                        filter=Q(away_matches__away_second_round_score__lte=0),
                    )
                ),
                points_total=F("matches_won") * 2 + F("matches_tie"),
            )
        )

        # Add results together
        results = {}
        for result in home_results:
            index = result["team_id"]
            results[index] = result

        for result in away_results:
            index = result["team_id"]
            if index not in results:
                results[index] = result
                continue
            team_stats = results[index]
            team_stats["matches_lost"] += result["matches_lost"]
            team_stats["matches_won"] += result["matches_won"]
            team_stats["matches_tie"] += result["matches_tie"]
            team_stats["matches_played"] += result["matches_played"]
            team_stats["clearences"] += result["clearences"]
            team_stats["points_total"] += result["points_total"]
            if (
                team_stats["weighted_sum"] is not None
                and result["weighted_sum"] is not None
            ):
                team_stats["weighted_sum"] += result["weighted_sum"]
                team_stats["best_round"] = min(
                    result["best_round"], team_stats["best_round"]
                )
                team_stats["best_match"] = min(
                    result["best_match"], team_stats["best_match"]
                )
            elif (
                team_stats["weighted_sum"] is None
                and result["weighted_sum"] is not None
            ):
                team_stats["weighted_sum"] = result["weighted_sum"]
                team_stats["best_round"] = result["best_round"]
                team_stats["best_match"] = result["best_match"]

        for result in results.values():
            result["match_average"] = (
                round(result["weighted_sum"] / result["matches_played"], 2)
                if result["matches_played"]
                else "NaN"
            )
            del result["weighted_sum"]
            result["points_average"] = (
                round(result["points_total"] / result["matches_played"], 2)
                if result["matches_played"]
                else "NaN"
            )

        return Response(list(results.values()))

    def retrieve(self, request, pk=None):
        all_time_stats: dict[str, int | float | t.Any] = {
            "score_total": 0,
            "match_count": 0,
            "pikes_total": 0,
            "zeros_total": 0,
            "throws_total": 0,
            "gteSix_total": 0,
            "zero_or_pike_first_throw_total": 0,
            "clearances": 0,
            "best_round": "NaN",
            "best_match": "NaN",
            "weighted_total": 0,
            "match_average": "NaN",
            "pike_percentage": "NaN",
        }

        throws = (
            Throw.objects.select_related("team", "match", "season")
            .filter(match__is_validated=True, team__team=pk, match__match_type__lt=31)
            .alias(
                # Cast the scores to integers for >= 6 counting
                **scores_casted_to_int(),
                non_throws=count_non_throws(),
                weighted_throw_count=F("throw_turn") * (4 - F("non_throws")),
                _scaled_points=scaled_points(),
                round_score=get_correct_round_score(),
                match_score=get_correct_match_score(),
            )
            .values("season__year")
            .annotate(
                score_total=Sum("st") + Sum("nd") + Sum("rd") + Sum("th"),
                match_count=Count("match", distinct=True),
                pikes_total=count_field_total("h", *score_fields),
                zeros_total=count_field_total("0", *score_fields),
                throws_total=4 * Count("pk") - Sum("non_throws"),
                gteSix_total=count_field_total(6, *casted_score_fields, gte=True),
                zero_or_pike_first_throw_total=Count(
                    "pk",
                    filter=Q(throw_turn=1) & (Q(score_first="0") | Q(score_first="h")),
                ),
                zero_percentage=rounded_divison("zeros_total", "throws_total", True),
                pike_percentage=rounded_divison("pikes_total", "throws_total", True),
                match_average=Round(
                    Sum("round_score") / (F("match_count") * 4),
                    precision=2,
                    output_field=FloatField(),
                ),
                weighted_total=F("match_count") * F("match_average"),
                clearances=Count("pk", filter=Q(round_score__lte=0)) / 4,
                best_round=Min("round_score"),
                best_match=Min("match_score"),
            )
        )

        data = {}
        # If no matches have not been played in the season yet find it through TeamInSeason.
        seasons = TeamsInSeason.objects.filter(team=pk).values(
            "season__year", "current_name", "current_abbreviation", "logo_url"
        )

        for season in seasons:
            data[season["season__year"]] = season
            for key, value in all_time_stats.items():
                data[season["season__year"]][key] = value
            del season["season__year"]

        for season in throws:
            for key in season:
                if key != "season__year":
                    data[season["season__year"]][key] = season[key]
            for key in all_time_stats.keys():
                if key in ("match_average", "pike_percentage"):
                    continue
                elif key not in ("best_round", "best_match"):
                    all_time_stats[key] += season[key]
                else:
                    if all_time_stats[key] == "NaN":
                        all_time_stats[key] = season[key]
                    else:
                        all_time_stats[key] = min(all_time_stats[key], season[key])

        all_time_stats["zero_percentage"] = (
            round(
                all_time_stats["zeros_total"] / all_time_stats["throws_total"] * 100, 2
            )
            if all_time_stats["throws_total"]
            else "NaN"
        )

        all_time_stats["pike_percentage"] = (
            round(
                all_time_stats["pikes_total"] / all_time_stats["throws_total"] * 100, 2
            )
            if all_time_stats["throws_total"]
            else "NaN"
        )

        all_time_stats["match_average"] = (
            round(all_time_stats["weighted_total"] / all_time_stats["match_count"], 2)
            if all_time_stats["match_count"]
            else "NaN"
        )

        del all_time_stats["weighted_total"]
        data["all_time"] = all_time_stats

        # This below is for adding in players that have not played any rounds
        not_played_players = (
            PlayersInTeam.objects.filter(team_season__team=pk)
            .annotate(
                _id=F("player__id"),
                player_name=Concat(
                    "player__first_name",
                    Value(" "),
                    "player__last_name",
                    output_field=CharField(),
                ),
            )
            .values(
                "team_season__season__year",
                "_id",
                "player_name",
            )
        )
        per_season_non_played = {}
        for player in not_played_players:
            if player["team_season__season__year"] not in per_season_non_played:
                per_season_non_played[player["team_season__season__year"]] = []
            per_season_non_played[player["team_season__season__year"]].append(player)
            del player["team_season__season__year"]

        players = (
            Throw.objects.select_related("team", "match", "season")
            .filter(match__is_validated=True, team__team=pk, match__match_type__lt=31)
            .alias(
                # Cast the scores to integers for >= 6 counting
                **scores_casted_to_int(),
                non_throws=count_non_throws(),
                weighted_throw_count=F("throw_turn") * (4 - F("non_throws")),
                _scaled_points=scaled_points(),
                round_score=get_correct_round_score(),
            )
            .values("season__year", "player")
            .annotate(
                throws_total=4 * Count("pk") - Sum("non_throws"),
                player_name=Concat(
                    "player__first_name",
                    Value(" "),
                    "player__last_name",
                    output_field=CharField(),
                ),
                rounds_total=Count("match"),
                score_total=Sum("st") + Sum("nd") + Sum("rd") + Sum("th"),
                score_per_throw=rounded_divison("score_total", "throws_total"),
                scaled_points=Sum("_scaled_points"),
                scaled_points_per_throw=rounded_divison(
                    "scaled_points", "throws_total"
                ),
                weighted_throw_count=Sum("weighted_throw_count"),
                pikes_total=count_field_total("h", *score_fields),
                zeros_total=count_field_total("0", *score_fields),
                gteSix_total=count_field_total(6, *casted_score_fields, gte=True),
                pike_percentage=rounded_divison("pikes_total", "throws_total", True),
                avg_throw_turn=rounded_divison("weighted_throw_count", "throws_total"),
            )
        )
        all_time_player_stats = {}
        for player in players:
            if player["player"] not in all_time_player_stats:
                all_time_player_stats[player["player"]] = {
                    "player_name": player["player_name"],
                    "player": player["player"],
                    "score_total": 0,
                    "rounds_total": 0,
                    "pikes_total": 0,
                    "zeros_total": 0,
                    "throws_total": 0,
                    "scaled_points": 0,
                    "gteSix_total": 0,
                    "weighted_throw_count": 0,
                }
            for key in all_time_player_stats[player["player"]]:
                if key in ("player_name", "player", "weighted_throw_count"):
                    continue

                all_time_player_stats[player["player"]][key] += (
                    player[key] if player[key] is not None else 0
                )
            all_time_player_stats[player["player"]]["weighted_throw_count"] += (
                player["avg_throw_turn"] * player["throws_total"]
            )

            if "players" not in data[player["season__year"]]:
                data[player["season__year"]]["players"] = []
            data[player["season__year"]]["players"].append(player)
            del player["season__year"]

        for season in per_season_non_played:
            if season not in data:
                data[season] = {}
            if "players" not in data[season]:
                data[season]["players"] = []

            season_player_ids = [p["player"] for p in data[season]["players"]]
            for player in per_season_non_played[season]:
                if player["_id"] not in season_player_ids:
                    player["player"] = player["_id"]
                    del player["_id"]
                    player["score_total"] = 0
                    player["rounds_total"] = 0
                    player["pikes_total"] = 0
                    player["zeros_total"] = 0
                    player["throws_total"] = 0
                    player["scaled_points"] = 0
                    player["gteSix_total"] = 0
                    player["weighted_throw_count"] = 0
                    player["pike_percentage"] = "NaN"
                    player["avg_throw_turn"] = "NaN"
                    player["score_per_throw"] = "NaN"
                    player["scaled_points_per_throw"] = "NaN"
                    data[season]["players"].append(player)

                    if player["player"] not in all_time_player_stats:
                        all_time_player_stats[player["player"]] = player

        for player in all_time_player_stats.values():
            player["score_per_throw"] = (
                round(player["score_total"] / player["throws_total"], 2)
                if player["throws_total"]
                else "NaN"
            )
            player["scaled_points_per_throw"] = (
                round(player["scaled_points"] / player["throws_total"], 2)
                if player["throws_total"]
                else "NaN"
            )
            player["pike_percentage"] = (
                round(player["pikes_total"] / player["throws_total"] * 100, 2)
                if player["throws_total"]
                else "NaN"
            )
            player["avg_throw_turn"] = (
                round(player["weighted_throw_count"] / player["throws_total"], 2)
                if player["throws_total"]
                else "NaN"
            )
            del player["weighted_throw_count"]

        data["all_time"]["players"] = list(all_time_player_stats.values())

        matches = Match.objects.select_related(
            "home_team__team", "away_team__team", "season"
        ).filter(
            Q(home_team__team=pk) | Q(away_team__team=pk),
            is_validated=True,
            match_type__lt=31,
        )
        data["all_time"]["matches"] = []
        for match in matches:
            if "matches" not in data[match.season.year]:
                data[match.season.year]["matches"] = []
            if isinstance(pk, str):
                pk = int(pk)
            if match.home_team.team.pk == pk:
                opposite_team = match.away_team.current_abbreviation
                own_first = match.home_first_round_score
                own_second = match.home_second_round_score
                opp_first = match.away_first_round_score
                opp_second = match.away_second_round_score
            else:
                opposite_team = match.home_team.current_abbreviation
                own_first = match.away_first_round_score
                own_second = match.away_second_round_score
                opp_first = match.home_first_round_score
                opp_second = match.home_second_round_score
            if own_first is not None and own_second is not None:
                own_team_total = own_first + own_second
            else:
                own_team_total = None
            if opp_first is not None and opp_second is not None:
                opp_team_total = opp_first + opp_second
            else:
                opp_team_total = None
            if match.match_type is None:
                match.match_type = 0  # Default to 0 if None
            m = {
                "id": match.pk,
                "match_time": match.match_time.strftime("%Y-%m-%d %H:%M"),
                "match_type": MATCH_TYPES[match.match_type],
                "opposite_team": opposite_team,
                "own_first": own_first,
                "own_second": own_second,
                "opp_first": opp_first,
                "opp_second": opp_second,
                "own_team_total": own_team_total,
                "opposite_team_total": opp_team_total,
            }
            data[match.season.year]["matches"].append(m)
            data["all_time"]["matches"].append(m)

        return Response(data)

    def list_all(self, request):
        # All-Time stats
        # TeamInSeasons is order by in the model

        home_results = (
            self.queryset.alias(
                home_score=F("home_matches__home_first_round_score")
                + F("home_matches__home_second_round_score"),
                home_opp_score=F("home_matches__away_first_round_score")
                + F("home_matches__away_second_round_score"),
                home_id=F("home_matches__pk"),
                best_round_match=Case(
                    When(
                        home_matches__home_first_round_score__lt=F(
                            "home_matches__home_second_round_score"
                        ),
                        then=F("home_matches__home_first_round_score"),
                    ),
                    default=F("home_matches__home_second_round_score"),
                ),
            )
            .values(
                "id",
                "team_id",
                "season__year",
                "home_matches__post_season",
                "current_name",
                "current_abbreviation",
            )
            .annotate(
                season=F("season__year"),
                playoff=F("home_matches__post_season"),
                matches_lost=Count(
                    "home_id", filter=Q(home_score__gt=F("home_opp_score"))
                ),
                matches_won=Count(
                    "home_id", filter=Q(home_score__lt=F("home_opp_score"))
                ),
                matches_tie=Count(
                    "home_id", filter=Q(home_score__exact=F("home_opp_score"))
                ),
                matches_played=F("matches_lost") + F("matches_won") + F("matches_tie"),
                weighted_sum=Sum("home_score"),
                best_round=Min("best_round_match"),
                best_match=Min("home_score"),
                clearences=(
                    Count(
                        "home_id", filter=Q(home_matches__home_first_round_score__lte=0)
                    )
                    + Count(
                        "home_id",
                        filter=Q(home_matches__home_second_round_score__lte=0),
                    )
                ),
            )
        )

        away_results = (
            self.queryset.alias(
                away_score=F("away_matches__away_first_round_score")
                + F("away_matches__away_second_round_score"),
                away_opp_score=F("away_matches__home_first_round_score")
                + F("away_matches__home_second_round_score"),
                away_id=F("away_matches__pk"),
                playoff=F("away_matches__post_season"),
                best_round_match=Case(
                    When(
                        away_matches__away_first_round_score__lt=F(
                            "away_matches__away_second_round_score"
                        ),
                        then=F("away_matches__away_first_round_score"),
                    ),
                    default=F("away_matches__away_second_round_score"),
                ),
            )
            .values(
                "id",
                "team_id",
                "season__year",
                "away_matches__post_season",
                "current_name",
                "current_abbreviation",
            )
            .annotate(
                season=F("season__year"),
                playoff=F("away_matches__post_season"),
                matches_lost=Count(
                    "away_id", filter=Q(away_score__gt=F("away_opp_score"))
                ),
                matches_won=Count(
                    "away_id", filter=Q(away_score__lt=F("away_opp_score"))
                ),
                matches_tie=Count(
                    "away_id", filter=Q(away_score__exact=F("away_opp_score"))
                ),
                matches_played=F("matches_lost") + F("matches_won") + F("matches_tie"),
                weighted_sum=Sum("away_score"),
                best_round=Min("best_round_match"),
                best_match=Min("away_score"),
                clearences=(
                    Count(
                        "away_id", filter=Q(away_matches__away_first_round_score__lte=0)
                    )
                    + Count(
                        "away_id",
                        filter=Q(away_matches__away_second_round_score__lte=0),
                    )
                ),
            )
        )

        # for result in home_results:

        # Add results together
        single_results = {
            "all": {},
            "bracket": {},
            "playoff": {},
        }
        for result in home_results:
            if result["playoff"]:
                single_results["playoff"][result["id"]] = result.copy()
            else:
                single_results["bracket"][result["id"]] = result.copy()

        for result in away_results:
            index = result["id"]
            stage_key = "playoff" if result["playoff"] else "bracket"
            if index not in single_results[stage_key]:
                single_results[stage_key][index] = result.copy()
                continue

            team_stats = single_results[stage_key][index]
            team_stats["matches_lost"] += result["matches_lost"]
            team_stats["matches_won"] += result["matches_won"]
            team_stats["matches_tie"] += result["matches_tie"]
            team_stats["matches_played"] += result["matches_played"]
            team_stats["clearences"] += result["clearences"]

            if (
                team_stats["weighted_sum"] is not None
                and result["weighted_sum"] is not None
            ):
                team_stats["weighted_sum"] += result["weighted_sum"]
                team_stats["best_round"] = min(
                    result["best_round"], team_stats["best_round"]
                )
                team_stats["best_match"] = min(
                    result["best_match"], team_stats["best_match"]
                )
            elif (
                team_stats["weighted_sum"] is None
                and result["weighted_sum"] is not None
            ):
                team_stats["weighted_sum"] = result["weighted_sum"]
                team_stats["best_round"] = result["best_round"]
                team_stats["best_match"] = result["best_match"]

        single_results_all = single_results["all"]
        for key in ("bracket", "playoff"):
            for result in single_results[key].values():
                if result["id"] not in single_results_all:
                    single_results_all[result["id"]] = result.copy()
                    continue
                team_season_all_results = single_results_all[result["id"]]
                team_season_all_results["matches_lost"] += result["matches_lost"]
                team_season_all_results["matches_won"] += result["matches_won"]
                team_season_all_results["matches_tie"] += result["matches_tie"]
                team_season_all_results["matches_played"] += result["matches_played"]
                team_season_all_results["clearences"] += result["clearences"]

                if (
                    team_season_all_results["weighted_sum"] is not None
                    and result["weighted_sum"] is not None
                ):
                    team_season_all_results["weighted_sum"] += result["weighted_sum"]
                    team_season_all_results["best_round"] = min(
                        result["best_round"], team_season_all_results["best_round"]
                    )
                    team_season_all_results["best_match"] = min(
                        result["best_match"], team_season_all_results["best_match"]
                    )
                elif (
                    team_season_all_results["weighted_sum"] is None
                    and result["weighted_sum"] is not None
                ):
                    team_season_all_results["weighted_sum"] = result["weighted_sum"]
                    team_season_all_results["best_round"] = result["best_round"]
                    team_season_all_results["best_match"] = result["best_match"]

        for result in single_results["all"].values():
            result["match_average"] = (
                round(result["weighted_sum"] / result["matches_played"], 2)
                if result["matches_played"]
                else "NaN"
            )

        all_time_results = {
            "all": {},
            "bracket": {},
            "playoff": {},
        }
        for key in ("bracket", "playoff"):
            for result in single_results[key].values():
                result["match_average"] = (
                    round(result["weighted_sum"] / result["matches_played"], 2)
                    if result["matches_played"]
                    else "NaN"
                )

                team_id = result["team_id"]
                if team_id not in all_time_results[key]:
                    all_time_results[key][team_id] = result.copy()
                    all_time_results[key][team_id]["season_count"] = 1
                    continue
                team_all_time = all_time_results[key][team_id]
                team_all_time["season_count"] += 1
                if team_all_time["season"] < result["season"]:
                    team_all_time["season"] = result["season"]
                    team_all_time["current_name"] = result["current_name"]
                    team_all_time["current_abbreviation"] = result[
                        "current_abbreviation"
                    ]

                team_all_time["matches_lost"] += result["matches_lost"]
                team_all_time["matches_won"] += result["matches_won"]
                team_all_time["matches_tie"] += result["matches_tie"]
                team_all_time["matches_played"] += result["matches_played"]
                team_all_time["clearences"] += result["clearences"]
                if (
                    team_all_time["weighted_sum"] is not None
                    and result["weighted_sum"] is not None
                ):
                    team_all_time["weighted_sum"] += result["weighted_sum"]
                    team_all_time["best_round"] = min(
                        result["best_round"], team_all_time["best_round"]
                    )
                    team_all_time["best_match"] = min(
                        result["best_match"], team_all_time["best_match"]
                    )
                elif (
                    team_all_time["weighted_sum"] is None
                    and result["weighted_sum"] is not None
                ):
                    team_all_time["weighted_sum"] = result["weighted_sum"]
                    team_all_time["best_round"] = result["best_round"]
                    team_all_time["best_match"] = result["best_match"]

        for key in ("bracket", "playoff"):
            for result in all_time_results[key].values():
                result["match_average"] = (
                    round(result["weighted_sum"] / result["matches_played"], 2)
                    if result["matches_played"]
                    else "NaN"
                )

                a_t_results_combined = all_time_results["all"]
                if result["team_id"] not in a_t_results_combined:
                    a_t_results_combined[result["team_id"]] = result.copy()
                    continue
                team_season_a_t_results = a_t_results_combined[result["team_id"]]
                team_season_a_t_results["matches_lost"] += result["matches_lost"]
                team_season_a_t_results["matches_won"] += result["matches_won"]
                team_season_a_t_results["matches_tie"] += result["matches_tie"]
                team_season_a_t_results["matches_played"] += result["matches_played"]
                team_season_a_t_results["clearences"] += result["clearences"]

                if (
                    team_season_a_t_results["weighted_sum"] is not None
                    and result["weighted_sum"] is not None
                ):
                    team_season_a_t_results["weighted_sum"] += result["weighted_sum"]
                    team_season_a_t_results["best_round"] = min(
                        result["best_round"], team_season_a_t_results["best_round"]
                    )
                    team_season_a_t_results["best_match"] = min(
                        result["best_match"], team_season_a_t_results["best_match"]
                    )
                elif (
                    team_season_a_t_results["weighted_sum"] is None
                    and result["weighted_sum"] is not None
                ):
                    team_season_a_t_results["weighted_sum"] = result["weighted_sum"]
                    team_season_a_t_results["best_round"] = result["best_round"]
                    team_season_a_t_results["best_match"] = result["best_match"]

        for result in all_time_results["all"].values():
            result["match_average"] = (
                round(result["weighted_sum"] / result["matches_played"], 2)
                if result["matches_played"]
                else "NaN"
            )

        single_results = {
            "all": list(single_results["all"].values()),
            "bracket": list(single_results["bracket"].values()),
            "playoff": list(single_results["playoff"].values()),
        }

        all_time_results = {
            "all": list(all_time_results["all"].values()),
            "bracket": list(all_time_results["bracket"].values()),
            "playoff": list(all_time_results["playoff"].values()),
        }
        return Response((single_results, all_time_results))

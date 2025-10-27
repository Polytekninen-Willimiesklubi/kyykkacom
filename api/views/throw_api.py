from __future__ import annotations

import typing as t

from django.db.models import (
    Case,
    CharField,
    Count,
    F,
    FloatField,
    Max,
    Q,
    SmallIntegerField,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Concat, Round
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, mixins, permissions, viewsets
from rest_framework.response import Response

import kyykka.serializers as serializers
from kyykka.models import PlayersInTeam, Season, Throw, User

from .permissions import IsCaptain, IsCaptainForThrow
from .utils.getters import get_season
from .utils.query_helpers import (
    casted_score_fields,
    count_field_total,
    count_non_throws,
    rounded_divison,
    scaled_points,
    score_fields,
    scores_casted_to_int,
)

if t.TYPE_CHECKING:
    from rest_framework.request import Request


@extend_schema_view(
    list=extend_schema(
        tags=["throws"],
        description="List all throws with player stats, optionally filtered by season",
        parameters=[
            OpenApiParameter(
                name="season",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Season ID to filter throws by",
            ),
        ],
        responses={200: serializers.PlayerListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["throws"],
        description="Get detailed throw statistics for a specific player",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "player_name": {"type": "string"},
                    "stats_per_seasons": {"type": "array", "items": {"type": "object"}},
                    "all_time_stats": {"type": "object"},
                    "matches_per_period": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                    "matches_both_periods": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                },
            }
        },
    ),
)
class ThrowsAPI(viewsets.ReadOnlyModelViewSet):
    queryset = Throw.objects.select_related("season", "team", "match").exclude(
        player__isnull=True
    )
    serializer_class = serializers.PlayerListSerializer

    # TODO invalidate cache when current season changes
    @method_decorator(cache_page(3600 * 12))
    def list(self, request: Request, format=None) -> Response:
        season_id = request.query_params.get("season", None)
        season: Season | None = None

        # Prefilter by season if provided
        if season_id is not None:
            season = get_season(request)
            self.queryset = self.queryset.filter(season=season)
        # TODO cache this bitch if already calculated once
        # TODO superweekend should be ignored
        throws = (
            self.queryset.filter(match__match_type__lt=31, match__is_validated=True)
            .alias(
                # Cast the scores to integers for >= 6 counting
                **scores_casted_to_int(),
                non_throws=count_non_throws(),
                weighted_throw_count=F("throw_turn") * (4 - F("non_throws")),
                _scaled_points=scaled_points(),
            )
            .values("player")
            .annotate(
                player_name=Concat(
                    "player__first_name", Value(" "), "player__last_name"
                ),
                team_name=F("team__current_abbreviation"),
                throw_turn=F("throw_turn"),
                playoff=F("match__post_season"),
                score_total=Sum("st") + Sum("nd") + Sum("rd") + Sum("th"),
                pikes_total=count_field_total("h", *score_fields),
                zeros_total=count_field_total("0", *score_fields),
                gte_six_total=count_field_total(6, *casted_score_fields, gte=True),
                match_count=Count("match", distinct=True),
                rounds_total=Count("pk"),
                throws_total=Count("pk") * 4 - Sum("non_throws"),
                scaled_points=Sum("_scaled_points"),
                weighted_throw_total=Sum("weighted_throw_count"),
                season=F("season__year"),
            )
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
            throws.append(
                {
                    "player": player.player.id,  # type: ignore
                    "player_name": f"{player.player.first_name} {player.player.last_name}",
                    "team_name": player.team_season.current_abbreviation,
                    "season": player.team_season.season.year,
                    "playoff": False,
                }
            )

        return Response(throws)

    def retrieve(self, request: Request, pk=None) -> Response | None:
        assert pk is not None
        players_data = self.queryset.filter(
            player=pk, match__match_type__lt=31, match__is_validated=True
        ).alias(
            # Cast the scores to integers for >= 6 counting
            **scores_casted_to_int(),
            non_throws=count_non_throws(),
            weighted_throw_count=F("throw_turn") * (4 - F("non_throws")),
            _scaled_points=scaled_points(),
            _score_total=F("st") + F("nd") + F("rd") + F("th"),
            _avg_round_score=F("_score_total") / (4 - F("non_throws")),
        )

        season_data = (
            players_data.values("player")
            .annotate(
                team_name=F("team__current_abbreviation"),
                score_total=Sum("_score_total"),
                pikes_total=count_field_total("h", *score_fields),
                zeros_total=count_field_total("0", *score_fields),
                ones_total=count_field_total("1", *score_fields),
                twos_total=count_field_total("2", *score_fields),
                threes_total=count_field_total("3", *score_fields),
                fours_total=count_field_total("4", *score_fields),
                fives_total=count_field_total("5", *score_fields),
                gte_six_total=count_field_total(6, *casted_score_fields, gte=True),
                match_count=Count("match", distinct=True),
                rounds_total=Count("pk"),
                throws_total=Count("pk") * 4 - Sum("non_throws"),
                scaled_points=Sum("_scaled_points"),
                weighted_throw_total=Sum("weighted_throw_count"),
                season=F("season__year"),
                position_one_throws=(
                    4 * Count("pk", filter=Q(throw_turn=1))
                    - Sum("non_throws", filter=Q(throw_turn=1))
                ),
                position_two_throws=(
                    4 * Count("pk", filter=Q(throw_turn=2))
                    - Sum("non_throws", filter=Q(throw_turn=2))
                ),
                position_three_throws=(
                    4 * Count("pk", filter=Q(throw_turn=3))
                    - Sum("non_throws", filter=Q(throw_turn=3))
                ),
                position_four_throws=(
                    4 * Count("pk", filter=Q(throw_turn=4))
                    - Sum("non_throws", filter=Q(throw_turn=4))
                ),
                avg_score=rounded_divison("score_total", "throws_total"),
                avg_scaled_points=rounded_divison("scaled_points", "throws_total"),
                avg_position=rounded_divison("weighted_throw_total", "throws_total"),
                pike_percentage=rounded_divison("pikes_total", "throws_total", True),
                avg_score_position_one=Round(
                    Sum("_score_total", filter=Q(throw_turn=1))
                    / F("position_one_throws"),
                    precision=2,
                    output_field=FloatField(),
                )
                if F("position_one_throws")
                else Value("NaN"),
                avg_score_position_two=Round(
                    Sum("_score_total", filter=Q(throw_turn=2))
                    / F("position_two_throws"),
                    precision=2,
                    output_field=FloatField(),
                )
                if F("position_two_throws")
                else Value("NaN"),
                avg_score_position_three=Round(
                    Sum("_score_total", filter=Q(throw_turn=3))
                    / F("position_three_throws"),
                    precision=2,
                    output_field=FloatField(),
                )
                if F("position_three_throws")
                else Value("NaN"),
                avg_score_position_four=Round(
                    Sum("_score_total", filter=Q(throw_turn=4))
                    / F("position_four_throws"),
                    precision=2,
                    output_field=FloatField(),
                )
                if F("position_four_throws")
                else Value("NaN"),
            )
            .order_by("season")
        )

        all_time_stats = season_data.aggregate(
            season_count=Count("season"),
            matches=Sum("match_count"),
            rounds=Sum("rounds_total"),
            throws=Sum("throws_total"),
            pikes=Sum("pikes_total"),
            zeros=Sum("zeros_total"),
            scores=Sum("score_total"),
            gte_six=Sum("gte_six_total"),
            scaled_points_total=Sum("scaled_points"),
            avg_score=rounded_divison("scores", "throws"),
            avg_scaled_points=rounded_divison("scaled_points_total", "throws"),
            avg_position=Round(
                Sum("weighted_throw_total") / F("throws"),
                precision=2,
                output_field=FloatField(),
            )
            if F("throws")
            else Value("NaN"),
            pike_percentage=rounded_divison("pikes", "throws", True),
        )
        user = User.objects.get(pk=pk)

        matches_per_period = players_data.annotate(
            own_team_score=Case(
                When(
                    match__home_team=F("team"),
                    then=Case(
                        When(throw_round=1, then=F("match__home_first_round_score")),
                        default=F("match__home_second_round_score"),
                    ),
                ),
                When(
                    match__away_team=F("team"),
                    then=Case(
                        When(throw_round=1, then=F("match__away_first_round_score")),
                        default=F("match__away_second_round_score"),
                    ),
                ),
                output_field=SmallIntegerField(),
            ),
            opponent_score=Case(
                When(
                    match__home_team=F("team"),
                    then=Case(
                        When(throw_round=1, then=F("match__away_first_round_score")),
                        default=F("match__away_second_round_score"),
                    ),
                ),
                When(
                    match__away_team=F("team"),
                    then=Case(
                        When(throw_round=1, then=F("match__home_first_round_score")),
                        default=F("match__home_second_round_score"),
                    ),
                ),
                output_field=SmallIntegerField(),
            ),
            score=F("_score_total"),
            oppenent_name=Case(
                When(
                    match__home_team=F("team"),
                    then=F("match__away_team__current_abbreviation"),
                ),
                default=F("match__home_team__current_abbreviation"),
                output_field=CharField(),
            ),
            time=F("match__match_time"),
            avg_round_score=Round(
                F("_avg_round_score"), precision=2, output_field=FloatField()
            ),
            season_name=F("season__year"),
        )

        matches_both_periods = (
            players_data.alias(
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
            )
            .values("match", "season")
            .annotate(
                time=F("match__match_time"),
                opponent_name=Case(
                    When(
                        match__home_team=F("team"),
                        then=F("match__away_team__current_abbreviation"),
                    ),
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
                    F("score") / (4 * Count("pk") - Sum("non_throws")),
                    precision=2,
                    output_field=FloatField(),
                ),
                own_team_score=Case(
                    When(
                        match__home_team=F("team"),
                        then=F("match__home_first_round_score")
                        + F("match__home_second_round_score"),
                    ),
                    default=F("match__away_first_round_score")
                    + F("match__away_second_round_score"),
                    output_field=SmallIntegerField(),
                ),
                opponent_score=Case(
                    When(
                        match__home_team=F("team"),
                        then=F("match__away_first_round_score")
                        + F("match__away_second_round_score"),
                    ),
                    default=F("match__home_first_round_score")
                    + F("match__home_second_round_score"),
                    output_field=SmallIntegerField(),
                ),
            )
        )

        return Response(
            {
                "id": user.pk,
                "player_name": f"{user.first_name} {user.last_name}",
                "stats_per_seasons": season_data,
                "all_time_stats": all_time_stats,
                # .values() needed, as the query doesn't have one yet.
                "matches_per_period": matches_per_period.values(),
                "matches_both_periods": matches_both_periods,
            }
        )


# Old API for modifying throws. Meld this to the `ThrowsAPI`.
@extend_schema_view(
    patch=extend_schema(
        tags=["throws"],
        description="Update throw scores. Only home team captain can modify throws.",
        request=serializers.ThrowSerializer,
        responses={
            200: serializers.ThrowSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
    ),
)
class ThrowAPI(generics.GenericAPIView, mixins.UpdateModelMixin):
    serializer_class = serializers.ThrowSerializer
    queryset = Throw.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsCaptain, IsCaptainForThrow]

    def patch(self, request, *args, **kwargs):
        # TODO invalidate caches here
        return self.partial_update(request, *args, **kwargs)

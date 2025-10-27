from __future__ import annotations

import typing as t

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, views
from rest_framework.response import Response

import kyykka.serializers as serializers
from kyykka.models import Match

from .permissions import MatchDetailPermission
from .utils.getters import (
    get_post_season,
    get_season,
    get_super,
)

if t.TYPE_CHECKING:
    from rest_framework.request import Request


@extend_schema(
    tags=["matches"],
    description="List all matches filtered by season and optional parameters (post_season and super_weekend)",
    parameters=[
        OpenApiParameter(
            name="season",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Season ID to filter matches by",
        ),
        OpenApiParameter(
            name="super_weekend",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter matches by super weekend status",
        ),
        OpenApiParameter(
            name="post_season",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter matches by post-season status. Only used if super_weekend is false",
        ),
    ],
    responses={200: serializers.MatchListSerializer(many=True)},
)
class MatchList(views.APIView):
    """
    List all matches
    """

    # throttle_classes = [AnonRateThrottle]
    # queryset = Match.objects.filter(match_time__lt=datetime.datetime.now() + datetime.timedelta(weeks=2))
    queryset = (
        Match.objects.select_related(
            "home_team__team",
            "away_team__team",
            "season",
        )
        .prefetch_related("home_team__players", "away_team__players")
        .all()
    )

    @method_decorator(cache_page(3600 * 12))
    def get(self, request):
        season = get_season(request)
        super_weekend = get_super(request)
        if not super_weekend:
            post_season = get_post_season(request)
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
        else:
            self.queryset = self.queryset.filter(
                season=season, match_type__gte=32
            ).filter(match_type__lte=39)
            serializer = serializers.MatchListSerializer(
                self.queryset, many=True, context={"season": season}
            )
            all_matches = serializer.data

        return Response(all_matches)


@extend_schema_view(
    get=extend_schema(
        tags=["matches"],
        description="Get detailed information for a specific match",
        responses={200: serializers.MatchDetailSerializer},
    ),
    patch=extend_schema(
        tags=["matches"],
        description="Update match scores or validation status. Home team captain can update scores, away team captain can validate.",
        request=serializers.MatchScoreSerializer,
        responses={
            200: serializers.MatchScoreSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
    ),
)
class MatchDetail(views.APIView):
    """
    Retrieve or update a Match instance
    """

    # throttle_classes = [AnonRateThrottle]
    queryset = Match.objects.all()
    permission_classes = [MatchDetailPermission]

    def get(self, request: Request, pk):
        match = get_object_or_404(self.queryset, pk=pk)
        serializer = serializers.MatchDetailSerializer(match)
        return Response(serializer.data)

    def patch(self, request: Request, pk, format=None):
        # season = get_season(request)
        match = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(request, match)
        # Update user session (so that it wont expire..)
        request.session.modified = True
        serializer = serializers.MatchScoreSerializer(
            match, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            # player_ids = (
            #     match.throw_set.all().values_list("player__id", flat=True).distinct()  # type: ignore
            # )
            # TODO reset caches here
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from __future__ import annotations

import typing as t

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

import kyykka.serializers as serializers
from kyykka.models import CurrentSeason, PlayersInTeam, User

from .permissions import IsCaptainForTeam
from .utils.getters import get_season

if t.TYPE_CHECKING:
    from rest_framework.request import Request


@extend_schema_view(
    get=extend_schema(
        tags=["players"],
        description="List all players that are not currently assigned to any team in the current season.",
        responses={
            200: {"type": "array", "items": {"$ref": "#/components/schemas/User"}}
        },
    ),
    post=extend_schema(
        tags=["players"],
        description="Reserve a player for a team. Only team captains can reserve players.",
        request=serializers.ReserveCreateSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
        },
    ),
)
class ReservePlayerAPI(generics.GenericAPIView):
    serializer_class = serializers.ReserveCreateSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsCaptainForTeam]

    def get(self, request: Request):
        current_season = CurrentSeason.objects.first()
        assert current_season is not None
        unreserved_players = self.queryset.exclude(
            # Filtter out people that have team
            Q(playersinteam__team_season__season=current_season.season)
            | Q(is_superuser=True)
            | Q(is_staff=True)
        ).order_by("first_name")

        serializer = serializers.UserSerializer(unreserved_players, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        success, message = serializer.save()
        return Response(
            {
                "success": success,
                "message": message,
            },
            status=200 if success else 400,
        )


@extend_schema_view(
    list=extend_schema(
        tags=["players"],
        description="List all players that are in a team for the season being queried. "
        "Returns three lists: total, bracket, and playoff stats.",
        parameters=[
            OpenApiParameter(
                name="season",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Season ID to filter players by",
            )
        ],
        responses={200: serializers.PlayerListAllPositionSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["players"],
        description="Get detailed player stats for a specific player",
        responses={200: serializers.PlayerAllDetailSerializer},
    ),
)
class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all players that are in a team for the season being queried.
    """

    queryset = PlayersInTeam.objects.all()

    @method_decorator(cache_page(3600 * 12))
    def list(self, request: Request):
        season = get_season(request)
        self.queryset = self.queryset.filter(team_season__season=season)
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
        return Response(all_data)

    def retrieve(self, request, pk=None):
        # season = getSeason(request)
        user = get_object_or_404(self.queryset, pk=pk)
        serializer = serializers.PlayerAllDetailSerializer(user)
        return Response(serializer.data)

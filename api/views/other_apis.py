from __future__ import annotations

import typing as t

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, mixins
from rest_framework.response import Response

import kyykka.serializers as serializers
from kyykka.models import News, Season, SuperWeekend

from .utils.getters import get_current_season

if t.TYPE_CHECKING:
    from rest_framework.request import Request


@extend_schema_view(
    get=extend_schema(
        tags=["news"],
        description="Get list of news articles",
        responses={200: serializers.NewsSerializer(many=True)},
    ),
    post=extend_schema(
        tags=["news"],
        description="Create a new news article",
        request=serializers.NewsSerializer,
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
    patch=extend_schema(
        tags=["news"],
        description="Update an existing news article",
        request=serializers.NewsSerializer,
        responses={200: serializers.NewsSerializer},
    ),
)
class NewsAPI(generics.GenericAPIView, mixins.UpdateModelMixin):
    serializer_class = serializers.NewsSerializer
    queryset = News.objects.all()

    def get(self, request: Request) -> Response:
        serializer = serializers.NewsSerializer(self.queryset.all(), many=True)
        return Response(serializer.data)

    def patch(self, request: Request, *args, **kwargs) -> Response:
        return self.partial_update(request, *args, **kwargs)

    def post(self, request: Request) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"success": True, "message": "Uusi uutinen onnistuneesti tehty!"},
                status=200,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": f"Something failed: {e}"},
                status=400,
            )


@extend_schema_view(
    get=extend_schema(
        tags=["seasons"],
        description="Get list of all seasons and the current season",
        responses={
            200: {
                "type": "array",
                "items": {"type": "array", "items": serializers.SeasonSerializer},
            }
        },
    ),
)
class SeasonsAPI(generics.GenericAPIView):
    queryset = Season.objects.all()

    # TODO invalidate cache when current season changes
    @method_decorator(cache_page(3600 * 12))
    def get(self, request: Request) -> Response:
        all_seasons = serializers.SeasonSerializer(self.queryset.all(), many=True).data
        current_season = get_current_season()
        current = serializers.SeasonSerializer(current_season).data
        return Response((all_seasons, current))


@extend_schema_view(
    get=extend_schema(
        tags=["super-weekends"],
        description="Get list of super weekends, optionally filtered by season",
        parameters=[
            OpenApiParameter(
                name="season",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Season ID to filter super weekends by",
            ),
        ],
        responses={200: serializers.SuperWeekendSerializer(many=True)},
    ),
)
class SuperWeekendAPI(generics.GenericAPIView):
    queryset = SuperWeekend.objects.all()

    def get(self, request: Request) -> Response:
        season_id = request.query_params.get("season")
        season = None
        if season_id is not None:
            try:
                season = Season.objects.get(id=season_id)
            except Season.DoesNotExist:
                season = None

        if season is None:
            super_weekends = serializers.SuperWeekendSerializer(
                self.queryset, many=True
            ).data
        else:
            self.queryset = self.queryset.filter(season=season)
            super_weekends = serializers.SuperWeekendSerializer(self.queryset).data
        return Response(super_weekends)

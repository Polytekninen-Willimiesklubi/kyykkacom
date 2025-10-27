"""Admin API views for Kyykkacom. Will be removed and replaced by proper admin in the native django."""

from __future__ import annotations

import typing as t

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, mixins
from rest_framework.response import Response

import kyykka.serializers as serializers
from kyykka.models import SuperWeekend, TeamsInSeason

from .permissions import IsSuperUserOrAdmin

if t.TYPE_CHECKING:
    from rest_framework.request import Request


@extend_schema_view(
    patch=extend_schema(
        tags=["admin"],
        description="Admin endpoint to update team information for a season",
        request=serializers.TeamsInSeasonSerializer,
        responses={
            200: serializers.TeamsInSeasonSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        auth=["IsAdminUser"],
    ),
)
class KyykkaAdminViewSet(generics.GenericAPIView, mixins.UpdateModelMixin):
    serializer_class = serializers.TeamsInSeasonSerializer
    queryset = TeamsInSeason.objects.all()
    permission_classes = [IsSuperUserOrAdmin]

    def patch(self, request: Request, *args, **kwargs) -> Response:
        # TODO cache invalidation if needed
        return self.partial_update(request, *args, **kwargs)


@extend_schema_view(
    post=extend_schema(
        tags=["admin"],
        description="Admin endpoint to create new matches",
        request=serializers.AdminMatchSerializer,
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
        auth=["IsAdminUser"],
    ),
)
class KyykkaAdminMatchViewSet(generics.GenericAPIView):
    serializer_class = serializers.AdminMatchSerializer
    permission_classes = [IsSuperUserOrAdmin]

    def post(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"success": True, "message": ""}, status=200)
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Something failed: {e}",
                },
                status=400,
            )


@extend_schema_view(
    patch=extend_schema(
        tags=["admin"],
        description="Admin endpoint to update super weekend information",
        request=serializers.SuperWeekendSerializer,
        responses={
            200: serializers.SuperWeekendSerializer,
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
        auth=["IsAdminUser"],
    ),
)
class KyykkaAdminSuperViewSet(generics.GenericAPIView, mixins.UpdateModelMixin):
    serializer_class = serializers.SuperWeekendSerializer
    queryset = SuperWeekend.objects.all()
    permission_classes = [IsSuperUserOrAdmin]

    def patch(self, request, *args, **kwargs):
        # TODO cache invalidation if needed
        return self.partial_update(request, *args, **kwargs)

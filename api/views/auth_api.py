"""Authentication APIs for login, logout and registration."""

import json

from django.contrib.auth import login, logout
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, views
from rest_framework.response import Response

import kyykka.serializers as serializers
from kyykka.models import CurrentSeason, PlayersInTeam

from .utils.getters import get_role


@extend_schema_view(
    post=extend_schema(
        tags=["auth"],
        description="Creates a session for user upon successful login. This is per instance based. "
        "Logout in other browser does not end login session in other one.",
        responses={200: serializers.LoginUserSerializer},
    )
)
class LoginAPI(generics.GenericAPIView):
    serializer_class = serializers.LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        try:
            current = CurrentSeason.objects.first().season
            player_in_team = PlayersInTeam.objects.filter(
                player=user, team_season__season=current
            ).first()
            team_id = player_in_team.team_season.team.id
            role = get_role(user)
            # role = '1' if player_in_team.is_captain else '0'
        except (PlayersInTeam.DoesNotExist, AttributeError):
            team_id = None
            role = 0
        response = Response(
            {
                "success": True,
                "user": serializers.UserSerializer(user).data,
                "role": role,
                "team_id": team_id,
            }
        )
        return response


@extend_schema_view(
    post=extend_schema(
        tags=["auth"],
        description="Logs out the current user. Removes the session and CSRF token.",
        responses={
            200: {"type": "object", "properties": {"success": {"type": "boolean"}}}
        },
    )
)
class LogoutAPI(views.APIView):
    def post(self, request, *args, **kwargs):
        logout(request)
        response = HttpResponse(json.dumps({"success": True}))
        response.delete_cookie("csrftoken")
        return response


@extend_schema_view(
    post=extend_schema(
        tags=["auth"],
        description="Register a new user account and automatically log them in.",
        request=serializers.CreateUserSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "user": {"$ref": "#/components/schemas/User"},
                    "role": {"type": "string", "enum": ["0", "1", "2"]},
                },
            }
        },
    )
)
class RegistrationAPI(generics.GenericAPIView):
    serializer_class = serializers.CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        success, message, user = serializer.save()
        login(request, user)
        return Response(
            {
                "success": success,
                "message": message,
                "user": serializers.UserSerializer(user).data,
                "role": "0",
            }
        )

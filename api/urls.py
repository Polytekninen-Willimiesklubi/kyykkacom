from django.conf import settings
from django.conf.urls import include
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import SimpleRouter

from . import views

urlpatterns = [
    # API Schema URLs
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # path('docs/', views.schema_view),
    path("csrf/", views.csrf),
    path("login/", views.LoginAPI.as_view(), name="login"),
    path("logout/", views.LogoutAPI.as_view()),
    path("register/", views.RegistrationAPI.as_view(), name="register"),
    path("reserve/", views.ReservePlayerAPI.as_view(), name="reserve"),
    path("matches/", views.MatchList.as_view(), name="matches-list"),
    path("matches/<int:pk>", views.MatchDetail.as_view(), name="matches-detail"),
    path("throws/update/<int:pk>/", views.ThrowAPI.as_view()),
    path("seasons", views.SeasonsAPI.as_view()),
    path("superweekend/", views.SuperWeekendAPI.as_view(), name="superweekend"),
    path("news/", views.NewsAPI.as_view()),
    path(
        "kyykka_admin/team/update/<int:pk>",
        views.KyykkaAdminViewSet.as_view(),
        name="teams-in-season",
    ),
    path(
        "kyykka_admin/match",
        views.KyykkaAdminMatchViewSet.as_view(),
        name="match-admin",
    ),
    path(
        "kyykka_admin/superweekend/<int:pk>",
        views.KyykkaAdminSuperViewSet.as_view(),
        name="admin-super",
    ),
    path("players/", views.ThrowsAPI.as_view({"get": "list"})),
    path("players/<int:pk>/", views.ThrowsAPI.as_view({"get": "retrieve"})),
    path("teams/", views.TeamViewSet.as_view({"get": "list"})),
    path("teams/<int:pk>/", views.TeamViewSet.as_view({"get": "retrieve"})),
    path("teams/all/", views.TeamViewSet.as_view({"get": "list_all"})),
    path("upload/", views.LogoUploadView.as_view(), name="logo-upload"),
]

router = SimpleRouter()
# router.register(r"players", views.PlayerViewSet, "player")
# router.register(r"teams", views.TeamViewSet)

# router.register(r'matches', views.MatchViewSet)
# router.register(r'reserve', views.ReservePlayerViewSet)
urlpatterns = router.urls + urlpatterns
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("^__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

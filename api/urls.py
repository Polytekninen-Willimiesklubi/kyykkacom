from django.conf import settings
from django.conf.urls import include
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import SimpleRouter

from api import views

schema_view = get_schema_view(
    openapi.Info(
        title="NKL API",
        default_version="v1",
        # description="Test description",
        # terms_of_service="https://www.google.com/policies/terms/",
        # contact=openapi.Contact(email="contact@snippets.local"),
        # license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # path('docs/', views.schema_view),
    path("csrf/", views.csrf),
    path("ping/", views.ping),
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
]

router = SimpleRouter()
router.register(r"players", views.PlayerViewSet, "player")
router.register(r"teams", views.TeamViewSet)

# router.register(r'matches', views.MatchViewSet)
# router.register(r'reserve', views.ReservePlayerViewSet)
urlpatterns = router.urls + urlpatterns
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("^__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

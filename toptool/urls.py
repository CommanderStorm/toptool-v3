from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from protokolle.views import show_public_protokoll
from toptool.views import login_failed

urlpatterns = [
    # admin
    path("admin/", admin.site.urls),
    # localization
    path("i18n/", include("django.conf.urls.i18n")),
    # apps
    path("profile/", include("userprofile.urls")),
    path("", include("meetingtypes.urls")),
    path("<str:mt_pk>/", include("meetings.urls")),
    path("<str:mt_pk>/", include("tops.urls")),
    path("<str:mt_pk>/", include("protokolle.urls")),
    path("<str:mt_pk>/", include("persons.urls")),
    # public protokoll url (for shibboleth)
    path(
        "protokolle/<str:mt_pk>/<uuid:meeting_pk>/<str:filetype>/",
        show_public_protokoll,
        name="protokollpublic",
    ),
    # redirect root
    path("", lambda x: redirect("ownmts", permanent=True)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # type: ignore
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # type: ignore

if settings.USE_KEYCLOAK:
    urlpatterns = [
        # Auth
        path("logout/", LogoutView.as_view(), name="logout"),
        path("oidc/", include("mozilla_django_oidc.urls")),
        path("login/failed/", login_failed),
    ] + urlpatterns
else:
    urlpatterns = [
        # Auth
        path("login/", LoginView.as_view(template_name="login.html"), name="login"),
        path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    ] + urlpatterns

from typing import List, Union

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, URLPattern, URLResolver
from django.views.generic import RedirectView, TemplateView

from toptool.views import login_failed

urlpatterns: List[Union[URLResolver, URLPattern]] = [
    # general browser stuff
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    # admin
    path("admin/", admin.site.urls),
    # localization
    path("i18n/", include("django.conf.urls.i18n")),
    # apps
    path("profile/", include("userprofile.urls")),
    path("meeting/", include("meetings.urls")),
    path("meeting/", include("tops.urls")),
    path("protokoll/", include("protokolle.urls")),
    path("person/", include("persons.urls")),
    path("", include("meetingtypes.urls")),
    # redirect root
    path("", RedirectView.as_view(pattern_name="ownmts", permanent=True), name="main-view"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # type: ignore
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # type: ignore

if settings.USE_KEYCLOAK:
    new_patterns: List[Union[URLResolver, URLPattern]] = [
        # Auth
        path("login/", RedirectView.as_view(pattern_name="oidc_authentication_init", permanent=True)),
        path("logout/", LogoutView.as_view(), name="logout"),
        path("oidc/", include("mozilla_django_oidc.urls")),
        path("login/failed/", login_failed),
    ]
else:
    new_patterns = [
        # Auth
        path("login/", LoginView.as_view(template_name="login.html"), name="login"),
        path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    ]
urlpatterns = new_patterns + urlpatterns

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

urlpatterns = [
    # admin
    url(r'^admin/', admin.site.urls),

    # login, logout
    url(r'^login/$',
        auth_views.login,
        {'template_name': 'toptool_common/login.html'},
        name='login'),

    url(r'^logout/$',
        auth_views.logout,
        {'next_page': '/'},
        name='logout'),

    # localozation
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # apps
    url(r'^tops/', include('tops.urls')),
    url(r'^meetings/', include('meetings.urls')),
    url(r'^meetingtypes/', include('meetingtypes.urls')),
    url(r'^protokolle/', include('protokolle.urls')),
    url(r'^persons/', include('persons.urls')),

    # redirect root
    url(r'^$', lambda x: redirect('ownmts', permanent=True)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

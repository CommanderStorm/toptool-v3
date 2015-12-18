from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^tops/', include('tops.urls')),
    url(r'^meetings/', include('meetings.urls')),
]

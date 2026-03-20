from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

_static = settings.STATIC_URL
if not _static.startswith('/'):
    _static = '/' + _static
_favicon_url = _static.rstrip('/') + '/user/img/logo/New.png'

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=_favicon_url, permanent=False)),
    path('django-admin/', admin.site.urls),
    path('', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

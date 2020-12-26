from django.urls import path, include, re_path
from django.contrib import admin
from django.views.static import serve
from django.conf import settings
from config import DJANGO_ADMIN_URL

urlpatterns = [
    path('', include('shop.urls')),
    path('payments/', include('payments.urls')),
    path('api/', include('shop.api.urls')),
    path(f'{DJANGO_ADMIN_URL}/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

handler404 = 'shop.views.handler404'

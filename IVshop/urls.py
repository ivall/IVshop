from django.urls import path, include, re_path
from django.contrib import admin
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('', include('shop.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

handler404 = 'shop.views.handler404'

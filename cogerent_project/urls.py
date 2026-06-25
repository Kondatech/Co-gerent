"""
URL configuration for cogerent_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('crm/', include('crm.urls')),
    path('ventes/', include('ventes.urls')),
    path('notifications/', include('notifications.urls')),
    path('agents/', include('agents.urls')),
    path('communication/', include('communication.urls')),  # ← AJOUTER CETTE LIGNE
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
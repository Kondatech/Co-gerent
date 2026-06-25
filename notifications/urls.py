from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.centre_notifications, name='centre'),
    path('api/marquer-lue/', views.marquer_lue, name='marquer_lue'),
    path('api/marquer-toutes-lues/', views.marquer_toutes_lues, name='marquer_toutes_lues'),
    path('api/count/', views.get_notifications_count, name='count'),
    path('api/recentes/', views.get_notifications_recentes, name='recentes'),
]
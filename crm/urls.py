from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    # Clients
    path('clients/', views.liste_clients, name='liste_clients'),
    path('clients/<int:client_id>/', views.detail_client, name='detail_client'),
    path('clients/nouveau/', views.nouveau_client, name='nouveau_client'),
    path('clients/<int:client_id>/modifier/', views.modifier_client, name='modifier_client'),
    path('clients/<int:client_id>/supprimer/', views.supprimer_client, name='supprimer_client'),
    path('clients/importer/', views.importer_clients, name='importer_clients'),
    
    # Interactions
    path('clients/<int:client_id>/interactions/nouvelle/', views.nouvelle_interaction, name='nouvelle_interaction'),
]
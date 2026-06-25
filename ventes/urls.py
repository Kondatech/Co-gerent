from django.urls import path
from . import views

app_name = 'ventes'

urlpatterns = [
    path('', views.liste_ventes, name='liste_ventes'),
    path('<int:vente_id>/', views.detail_vente, name='detail_vente'),
    path('nouvelle/', views.nouvelle_vente, name='nouvelle_vente'),
    path('<int:vente_id>/modifier/', views.modifier_vente, name='modifier_vente'),
    path('<int:vente_id>/supprimer/', views.supprimer_vente, name='supprimer_vente'),
    path('<int:vente_id>/statut/', views.changer_statut, name='changer_statut'),
]
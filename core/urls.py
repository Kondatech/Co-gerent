from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Page d'accueil
    path('', views.accueil, name='accueil'),
    
    # Authentification
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
    # Dashboard et onboarding
    path('dashboard/', views.dashboard, name='dashboard'),
    path('onboarding/', views.onboarding, name='onboarding'),
]
from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    # Page principale des integrations
    path('integrations/', views.integrations, name='integrations'),
    
    # Connexion manuelle (formulaire)
    path('connecter/', views.connecter_facebook, name='connecter_facebook'),
    
    # Deconnexion
    path('deconnecter/', views.deconnecter_facebook, name='deconnecter_facebook'),
    
    # Verification token (API)
    path('verifier-token/', views.verifier_token, name='verifier_token'),
    
    # Callback OAuth (deprecie mais garde pour compatibilite)
    path('facebook/callback/', views.facebook_callback, name='facebook_callback'),
    path('facebook/confirmer/', views.confirmer_page_facebook, name='confirmer_page_facebook'),
]
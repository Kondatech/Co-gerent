from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
import requests
from .models import ConnexionFacebook
from .forms import ConnexionFacebookForm


@login_required
def integrations(request):
    """Page des integrations"""
    entreprise = request.user.entreprise
    
    if not entreprise:
        messages.warning(request, 'Vous devez avoir une entreprise pour gerer les integrations.')
        return redirect('core:onboarding')
    
    # Récupérer la connexion existante
    connexion = None
    try:
        connexion = ConnexionFacebook.objects.get(entreprise=entreprise)
    except ConnexionFacebook.DoesNotExist:
        pass
    
    # Traiter le formulaire
    if request.method == 'POST':
        form = ConnexionFacebookForm(request.POST)
        if form.is_valid():
            # Vérifier le token avec un appel API test
            token = form.cleaned_data['access_token']
            page_id = form.cleaned_data['page_id']
            
            # Tester le token
            test_url = f"https://graph.facebook.com/v19.0/{page_id}?access_token={token}"
            
            try:
                response = requests.get(test_url)
                data = response.json()
                
                if 'error' in data:
                    messages.error(request, f"Erreur Facebook: {data['error'].get('message', 'Token invalide')}")
                    return render(request, 'communication/integrations.html', {
                        'form': form,
                        'connexion': connexion,
                        'facebook_connecte': False,
                    })
                
                # Si tout est ok, sauvegarder
                with transaction.atomic():
                    # Supprimer l'ancienne connexion si elle existe
                    ConnexionFacebook.objects.filter(entreprise=entreprise).delete()
                    
                    # Créer la nouvelle
                    connexion = ConnexionFacebook.objects.create(
                        entreprise=entreprise,
                        page_id=page_id,
                        page_nom=form.cleaned_data.get('page_nom', data.get('name', page_id)),
                        access_token=token,
                        est_active=True
                    )
                
                messages.success(request, f'Page Facebook "{connexion.page_nom}" connectee avec succes !')
                return redirect('communication:integrations')
                
            except requests.RequestException as e:
                messages.error(request, f'Erreur de connexion a Facebook: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        # Pré-remplir le formulaire avec les données existantes
        initial = {}
        if connexion:
            initial = {
                'page_id': connexion.page_id,
                'page_nom': connexion.page_nom,
                'access_token': connexion.access_token,
            }
        form = ConnexionFacebookForm(initial=initial)
    
    context = {
        'form': form,
        'connexion': connexion,
        'facebook_connecte': connexion is not None and connexion.est_active,
    }
    
    return render(request, 'communication/integrations.html', context)


@login_required
def connecter_facebook(request):
    """Redirige vers l'autorisation Facebook (OAuth) - DEPRECIE"""
    # Cette vue est gardée pour compatibilité mais redirige vers integrations
    messages.info(request, 'Utilisez le formulaire ci-dessous pour connecter votre page.')
    return redirect('communication:integrations')


@login_required
def deconnecter_facebook(request):
    """Deconnecte la page Facebook"""
    if request.method == 'POST':
        try:
            connexion = ConnexionFacebook.objects.get(entreprise=request.user.entreprise)
            connexion.delete()
            messages.success(request, 'Page Facebook deconnectee avec succes.')
        except ConnexionFacebook.DoesNotExist:
            messages.warning(request, 'Aucune page Facebook connectee.')
    else:
        messages.error(request, 'Methode non autorisee.')
    
    return redirect('communication:integrations')


@login_required
def facebook_callback(request):
    """Callback OAuth Facebook - DEPRECIE"""
    messages.info(request, 'Utilisez le formulaire de connexion manuelle.')
    return redirect('communication:integrations')


@login_required
def confirmer_page_facebook(request):
    """Confirme la selection de la page Facebook - DEPRECIE"""
    messages.info(request, 'Utilisez le formulaire de connexion manuelle.')
    return redirect('communication:integrations')


@login_required
@transaction.atomic
def verifier_token(request):
    """API pour verifier un token Facebook"""
    if request.method == 'POST':
        token = request.POST.get('token')
        page_id = request.POST.get('page_id')
        
        if not token or not page_id:
            return JsonResponse({'error': 'Token et Page ID requis'}, status=400)
        
        test_url = f"https://graph.facebook.com/v19.0/{page_id}?access_token={token}"
        
        try:
            response = requests.get(test_url)
            data = response.json()
            
            if 'error' in data:
                return JsonResponse({
                    'valid': False,
                    'error': data['error'].get('message', 'Token invalide')
                })
            
            return JsonResponse({
                'valid': True,
                'page_name': data.get('name', 'Page inconnue'),
                'page_id': data.get('id')
            })
            
        except requests.RequestException as e:
            return JsonResponse({'valid': False, 'error': str(e)})
    
    return JsonResponse({'error': 'Methode non autorisee'}, status=405)
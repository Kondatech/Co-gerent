from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db import models
from django.utils import timezone
from .models import Entreprise, Utilisateur, ProfilEntreprise
from .forms import InscriptionForm, ConnexionForm, OnboardingForm


def accueil(request):
    """Page d'accueil du Co-Gérant"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/accueil.html')


def inscription(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} ! Commencons par configurer votre entreprise.')
            return redirect('core:onboarding')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = InscriptionForm()
    
    return render(request, 'core/inscription.html', {'form': form})


def connexion(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Mettre à jour la date de dernière connexion
            user.date_derniere_connexion = timezone.now()
            user.save()
            
            messages.success(request, f'Bon retour {user.first_name} !')
            
            # Rediriger vers l'onboarding si nécessaire
            if not user.onboarding_complete:
                return redirect('core:onboarding')
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
    else:
        form = ConnexionForm()
    
    return render(request, 'core/connexion.html', {'form': form})


def deconnexion(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, 'Vous avez ete deconnecte.')
    return redirect('core:accueil')


@login_required
def dashboard(request):
    """Dashboard principal après authentification"""
    # Vérifier si l'utilisateur a une entreprise
    if not request.user.entreprise:
        messages.warning(request, 'Vous n\'etes pas encore rattache a une entreprise.')
        return render(request, 'core/dashboard.html', {
            'entreprise': None,
            'profil_complet': False,
            'total_clients': 0,
            'ca_mois': 0,
            'notifications_non_lues': 0,
            'recommandations_count': 0
        })
    
    # Vérifier si le profil est complet
    try:
        profil = request.user.entreprise.profil
        profil_complet = profil.complet
        if not profil_complet:
            messages.warning(request, 'Veuillez completer le profil de votre entreprise.')
    except ProfilEntreprise.DoesNotExist:
        profil_complet = False
        messages.warning(request, 'Veuillez completer le profil de votre entreprise.')
    
    # Rediriger vers l'onboarding si nécessaire
    if not request.user.onboarding_complete or not profil_complet:
        return redirect('core:onboarding')
    
    # Importer les modèles pour les statistiques
    from crm.models import Client
    from ventes.models import Vente
    from notifications.models import Notification
    
    # Calculer les statistiques
    entreprise_id = request.user.entreprise.id
    
    # Total clients
    total_clients = Client.objects.filter(entreprise_id=entreprise_id).count()
    
    # CA du mois
    maintenant = timezone.now()
    mois_courant = maintenant.replace(day=1, hour=0, minute=0, second=0)
    ca_mois = Vente.objects.filter(
        entreprise_id=entreprise_id,
        date_vente__gte=mois_courant
    ).aggregate(total=models.Sum('montant_total'))['total'] or 0
    
    # Notifications non lues
    notifications_non_lues = Notification.objects.filter(
        utilisateur=request.user,
        est_lue=False
    ).count()
    
    # Recommandations non lues
    recommandations_count = Notification.objects.filter(
        utilisateur=request.user,
        type='RECOMMANDATION',
        est_lue=False
    ).count()
    
    context = {
        'entreprise': request.user.entreprise,
        'profil_complet': profil_complet,
        'utilisateur': request.user,
        'total_clients': total_clients,
        'ca_mois': ca_mois,
        'notifications_non_lues': notifications_non_lues,
        'recommandations_count': recommandations_count,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def onboarding(request):
    """Page d'onboarding (questionnaire conversationnel)"""
    # Si l'onboarding est déjà complet, rediriger vers le dashboard
    if request.user.onboarding_complete:
        try:
            if request.user.entreprise.profil.complet:
                return redirect('core:dashboard')
        except ProfilEntreprise.DoesNotExist:
            pass
    
    # Récupérer l'entreprise existante si elle existe
    entreprise = request.user.entreprise
    profil = None
    if entreprise:
        try:
            profil = entreprise.profil
        except ProfilEntreprise.DoesNotExist:
            profil = None
    
    if request.method == 'POST':
        form = OnboardingForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Créer ou mettre à jour l'entreprise
                if not request.user.entreprise:
                    entreprise = Entreprise.objects.create(
                        nom=form.cleaned_data['nom_entreprise'],
                        secteur=form.cleaned_data['secteur'],
                        ville=form.cleaned_data['ville'],
                        pays=form.cleaned_data['pays']
                    )
                    request.user.entreprise = entreprise
                    request.user.save()
                else:
                    entreprise = request.user.entreprise
                    entreprise.nom = form.cleaned_data['nom_entreprise']
                    entreprise.secteur = form.cleaned_data['secteur']
                    entreprise.ville = form.cleaned_data['ville']
                    entreprise.pays = form.cleaned_data['pays']
                    entreprise.save()
                
                # Créer ou mettre à jour le profil
                profil, created = ProfilEntreprise.objects.get_or_create(
                    entreprise=entreprise,
                    defaults={
                        'objectif_court_terme': form.cleaned_data['objectif_court_terme'],
                        'objectif_long_terme': form.cleaned_data['objectif_long_terme'],
                        'services_prioritaires': form.cleaned_data['services_prioritaires'],
                        'description_activite': form.cleaned_data['description_activite'],
                        'nombre_employes': form.cleaned_data['nombre_employes'],
                        'complet': True
                    }
                )
                
                if not created:
                    profil.objectif_court_terme = form.cleaned_data['objectif_court_terme']
                    profil.objectif_long_terme = form.cleaned_data['objectif_long_terme']
                    profil.services_prioritaires = form.cleaned_data['services_prioritaires']
                    profil.description_activite = form.cleaned_data['description_activite']
                    profil.nombre_employes = form.cleaned_data['nombre_employes']
                    profil.complet = True
                    profil.save()
                
                # Marquer l'onboarding comme terminé
                request.user.onboarding_complete = True
                request.user.save()
                
                messages.success(request, 'Profil de votre entreprise enregistre avec succes !')
                return redirect('core:dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erreur dans le champ {field}: {error}')
    else:
        # Pré-remplir le formulaire si des données existent
        initial_data = {}
        if entreprise:
            initial_data['nom_entreprise'] = entreprise.nom
            initial_data['secteur'] = entreprise.secteur
            initial_data['ville'] = entreprise.ville
            initial_data['pays'] = entreprise.pays
        
        if profil:
            initial_data['objectif_court_terme'] = profil.objectif_court_terme
            initial_data['objectif_long_terme'] = profil.objectif_long_terme
            initial_data['services_prioritaires'] = profil.services_prioritaires
            initial_data['description_activite'] = profil.description_activite
            initial_data['nombre_employes'] = profil.nombre_employes
        
        form = OnboardingForm(initial=initial_data)
    
    context = {
        'form': form,
        'titre': 'Onboarding - Definissez votre profil',
    }
    return render(request, 'core/onboarding.html', context)
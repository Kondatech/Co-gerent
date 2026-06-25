from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import csv
import io
from .models import Client, Interaction
from ventes.models import Vente
from .forms import ClientForm, InteractionForm, ImportClientsForm


@login_required
def liste_clients(request):
    """Liste des clients avec recherche, filtres et pagination"""
    entreprise = request.user.entreprise
    
    if not entreprise:
        messages.warning(request, 'Vous devez etre rattache a une entreprise')
        return redirect('core:onboarding')
    
    clients = Client.objects.filter(entreprise=entreprise)
    
    # Recherche
    search = request.GET.get('search', '')
    if search:
        clients = clients.filter(
            Q(nom__icontains=search) |
            Q(email__icontains=search) |
            Q(telephone__icontains=search)
        )
    
    # Filtres
    segment = request.GET.get('segment', '')
    if segment:
        clients = clients.filter(segment=segment)
    
    statut = request.GET.get('statut', '')
    if statut == 'actif':
        clients = clients.filter(est_actif=True)
    elif statut == 'inactif':
        clients = clients.filter(est_actif=False)
    
    # Tri
    tri = request.GET.get('tri', '-date_creation')
    clients = clients.order_by(tri)
    
    # Pagination
    paginator = Paginator(clients, 10)
    page = request.GET.get('page', 1)
    clients_page = paginator.get_page(page)
    
    # Statistiques pour l'affichage
    total_clients = Client.objects.filter(entreprise=entreprise).count()
    clients_actifs = Client.objects.filter(entreprise=entreprise, est_actif=True).count()
    
    context = {
        'clients': clients_page,
        'search': search,
        'segment': segment,
        'statut': statut,
        'tri': tri,
        'total_clients': total_clients,
        'clients_actifs': clients_actifs,
        'segments': Client.SEGMENTS,
        'paginator': paginator,
    }
    return render(request, 'crm/liste_clients.html', context)


@login_required
def detail_client(request, client_id):
    """Fiche detaillee d'un client"""
    entreprise = request.user.entreprise
    client = get_object_or_404(Client, id=client_id, entreprise=entreprise)
    
    # Ventes du client
    ventes = Vente.objects.filter(client=client).order_by('-date_vente')
    
    # Interactions du client
    interactions = client.interactions.all().order_by('-date')
    
    context = {
        'client': client,
        'ventes': ventes,
        'interactions': interactions,
    }
    return render(request, 'crm/detail_client.html', context)


@login_required
def nouveau_client(request):
    """Creer un nouveau client"""
    entreprise = request.user.entreprise
    
    if not entreprise:
        messages.warning(request, 'Vous devez etre rattache a une entreprise')
        return redirect('core:onboarding')
    
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.entreprise = entreprise
            client.save()
            messages.success(request, f'Client {client.nom} cree avec succes')
            return redirect('crm:detail_client', client_id=client.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = ClientForm()
    
    return render(request, 'crm/nouveau_client.html', {'form': form})


@login_required
def modifier_client(request, client_id):
    """Modifier un client existant"""
    entreprise = request.user.entreprise
    client = get_object_or_404(Client, id=client_id, entreprise=entreprise)
    
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client {client.nom} modifie avec succes')
            return redirect('crm:detail_client', client_id=client.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = ClientForm(instance=client)
    
    return render(request, 'crm/modifier_client.html', {'form': form, 'client': client})


@login_required
@require_http_methods(['POST'])
def supprimer_client(request, client_id):
    """Supprimer un client"""
    entreprise = request.user.entreprise
    client = get_object_or_404(Client, id=client_id, entreprise=entreprise)
    
    # Verifier si le client a des ventes
    if client.ventes.exists():
        messages.error(request, 'Impossible de supprimer ce client car il a des ventes associees')
        return redirect('crm:detail_client', client_id=client.id)
    
    nom = client.nom
    client.delete()
    messages.success(request, f'Client {nom} supprime avec succes')
    return redirect('crm:liste_clients')


@login_required
def importer_clients(request):
    """Importer des clients depuis un fichier CSV"""
    entreprise = request.user.entreprise
    
    if not entreprise:
        messages.warning(request, 'Vous devez etre rattache a une entreprise')
        return redirect('core:onboarding')
    
    if request.method == 'POST':
        form = ImportClientsForm(request.POST, request.FILES)
        if form.is_valid():
            fichier = request.FILES['fichier_csv']
            dedupliquer_par = form.cleaned_data['dedupliquer_par']
            ecraser = form.cleaned_data['ecraser_existants']
            
            try:
                # Lire le CSV
                data = fichier.read().decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(data))
                
                created_count = 0
                updated_count = 0
                errors = []
                
                for row in csv_reader:
                    try:
                        nom = row.get('nom', '').strip()
                        email = row.get('email', '').strip()
                        telephone = row.get('telephone', '').strip()
                        segment = row.get('segment', 'STANDARD').strip()
                        score_rfm = int(row.get('score_rfm', 0))
                        
                        if not nom:
                            errors.append("Ligne ignoree: nom manquant")
                            continue
                        
                        # Verifier si le client existe deja
                        existing_client = None
                        
                        if dedupliquer_par == 'email' and email:
                            existing_client = Client.objects.filter(
                                entreprise=entreprise,
                                email=email
                            ).first()
                        elif dedupliquer_par == 'telephone' and telephone:
                            existing_client = Client.objects.filter(
                                entreprise=entreprise,
                                telephone=telephone
                            ).first()
                        elif dedupliquer_par == 'email_telephone':
                            if email and telephone:
                                existing_client = Client.objects.filter(
                                    entreprise=entreprise
                                ).filter(
                                    Q(email=email) | Q(telephone=telephone)
                                ).first()
                            elif email:
                                existing_client = Client.objects.filter(
                                    entreprise=entreprise,
                                    email=email
                                ).first()
                            elif telephone:
                                existing_client = Client.objects.filter(
                                    entreprise=entreprise,
                                    telephone=telephone
                                ).first()
                        
                        if existing_client:
                            if ecraser:
                                existing_client.nom = nom
                                existing_client.segment = segment
                                existing_client.score_rfm = score_rfm
                                existing_client.save()
                                updated_count += 1
                            # Sinon on ignore
                        else:
                            # Creer un nouveau client
                            Client.objects.create(
                                entreprise=entreprise,
                                nom=nom,
                                email=email,
                                telephone=telephone,
                                segment=segment if segment in dict(Client.SEGMENTS) else 'STANDARD',
                                score_rfm=score_rfm,
                                est_actif=True
                            )
                            created_count += 1
                            
                    except Exception as e:
                        errors.append(f"Erreur ligne {csv_reader.line_num}: {str(e)}")
                
                # Message de synthese
                message = f"Import termine: {created_count} clients crees"
                if updated_count > 0:
                    message += f", {updated_count} clients mis a jour"
                if errors:
                    message += f", {len(errors)} erreurs"
                messages.success(request, message)
                
                if errors:
                    for error in errors[:5]:
                        messages.warning(request, error)
                
                return redirect('crm:liste_clients')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la lecture du fichier: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = ImportClientsForm()
    
    return render(request, 'crm/importer_clients.html', {'form': form})


@login_required
def nouvelle_interaction(request, client_id):
    """Ajouter une interaction a un client"""
    entreprise = request.user.entreprise
    client = get_object_or_404(Client, id=client_id, entreprise=entreprise)
    
    if request.method == 'POST':
        form = InteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.client = client
            interaction.save()
            messages.success(request, 'Interaction ajoutee avec succes')
            return redirect('crm:detail_client', client_id=client.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = InteractionForm()
    
    return render(request, 'crm/nouvelle_interaction.html', {'form': form, 'client': client})
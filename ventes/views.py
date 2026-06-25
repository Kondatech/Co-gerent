from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Vente, LigneVente
from crm.models import Client
from .forms import VenteForm, LigneVenteFormSet, VenteStatutForm


@login_required
def liste_ventes(request):
    """Liste des ventes avec filtres et pagination"""
    entreprise = request.user.entreprise
    
    if not entreprise:
        messages.warning(request, 'Vous devez etre rattache a une entreprise')
        return redirect('core:onboarding')
    
    ventes = Vente.objects.filter(entreprise=entreprise)
    
    # Filtres
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    if date_debut and date_fin:
        try:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d') + timedelta(days=1)
            ventes = ventes.filter(date_vente__gte=date_debut_obj, date_vente__lt=date_fin_obj)
        except ValueError:
            pass
    
    statut = request.GET.get('statut', '')
    if statut:
        ventes = ventes.filter(statut=statut)
    
    client_id = request.GET.get('client', '')
    if client_id:
        ventes = ventes.filter(client_id=client_id)
    
    # Recherche par numero de facture
    search = request.GET.get('search', '')
    if search:
        ventes = ventes.filter(numero_facture__icontains=search)
    
    # Tri
    tri = request.GET.get('tri', '-date_vente')
    ventes = ventes.order_by(tri)
    
    # Pagination
    paginator = Paginator(ventes, 10)
    page = request.GET.get('page', 1)
    ventes_page = paginator.get_page(page)
    
    # Statistiques
    total_ca = ventes.aggregate(total=Sum('montant_total'))['total'] or 0
    total_ventes = ventes.count()
    
    context = {
        'ventes': ventes_page,
        'search': search,
        'statut': statut,
        'client_id': client_id,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'tri': tri,
        'total_ca': total_ca,
        'total_ventes': total_ventes,
        'clients': Client.objects.filter(entreprise=entreprise, est_actif=True).order_by('nom'),
        'statuts': Vente.STATUS,
        'paginator': paginator,
    }
    return render(request, 'ventes/liste_ventes.html', context)


@login_required
def detail_vente(request, vente_id):
    """Detail d'une vente avec ses lignes"""
    entreprise = request.user.entreprise
    vente = get_object_or_404(Vente, id=vente_id, entreprise=entreprise)
    lignes = vente.lignes.all()
    
    context = {
        'vente': vente,
        'lignes': lignes,
    }
    return render(request, 'ventes/detail_vente.html', context)


@login_required
def nouvelle_vente(request):
    """Creer une nouvelle vente"""
    entreprise = request.user.entreprise
    
    if not entreprise:
        messages.warning(request, 'Vous devez etre rattache a une entreprise')
        return redirect('core:onboarding')
    
    if request.method == 'POST':
        form = VenteForm(request.POST, entreprise=entreprise)
        formset = LigneVenteFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                vente = form.save(commit=False)
                vente.entreprise = entreprise
                vente.montant_total = 0
                vente.save()
                
                # Sauvegarder les lignes
                lignes = formset.save(commit=False)
                total = 0
                for ligne in lignes:
                    ligne.vente = vente
                    ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                    total += ligne.total_ligne
                    ligne.save()
                
                # Mettre a jour le montant total
                vente.montant_total = total
                vente.save()
                
                # Mettre a jour le client
                if vente.client:
                    client = vente.client
                    client.nombre_achats += 1
                    client.montant_total_achats += total
                    client.date_dernier_achat = timezone.now()
                    client.save()
                
                messages.success(request, f'Vente {vente.numero_facture} creee avec succes')
                return redirect('ventes:detail_vente', vente_id=vente.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
            
            for form_error in formset.errors:
                for field, errors in form_error.items():
                    for error in errors:
                        messages.error(request, f'Erreur ligne: {error}')
    else:
        form = VenteForm(entreprise=entreprise)
        formset = LigneVenteFormSet()
    
    return render(request, 'ventes/nouvelle_vente.html', {
        'form': form,
        'formset': formset,
    })


@login_required
def modifier_vente(request, vente_id):
    """Modifier une vente existante"""
    entreprise = request.user.entreprise
    vente = get_object_or_404(Vente, id=vente_id, entreprise=entreprise)
    
    if request.method == 'POST':
        form = VenteForm(request.POST, instance=vente, entreprise=entreprise)
        formset = LigneVenteFormSet(request.POST, instance=vente)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                vente = form.save(commit=False)
                vente.save()
                
                # Sauvegarder les lignes
                lignes = formset.save(commit=False)
                total = 0
                for ligne in lignes:
                    ligne.vente = vente
                    ligne.total_ligne = ligne.quantite * ligne.prix_unitaire
                    total += ligne.total_ligne
                    ligne.save()
                
                # Supprimer les lignes marquees pour suppression
                for deleted_ligne in formset.deleted_objects:
                    deleted_ligne.delete()
                
                # Mettre a jour le montant total
                vente.montant_total = total
                vente.save()
                
                messages.success(request, f'Vente {vente.numero_facture} modifiee avec succes')
                return redirect('ventes:detail_vente', vente_id=vente.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = VenteForm(instance=vente, entreprise=entreprise)
        formset = LigneVenteFormSet(instance=vente)
    
    return render(request, 'ventes/modifier_vente.html', {
        'form': form,
        'formset': formset,
        'vente': vente,
    })


@login_required
@require_http_methods(['POST'])
def supprimer_vente(request, vente_id):
    """Supprimer une vente"""
    entreprise = request.user.entreprise
    vente = get_object_or_404(Vente, id=vente_id, entreprise=entreprise)
    
    numero = vente.numero_facture
    vente.delete()
    messages.success(request, f'Vente {numero} supprimee avec succes')
    return redirect('ventes:liste_ventes')


@login_required
@require_http_methods(['POST'])
def changer_statut(request, vente_id):
    """Changer le statut d'une vente"""
    entreprise = request.user.entreprise
    vente = get_object_or_404(Vente, id=vente_id, entreprise=entreprise)
    
    form = VenteStatutForm(request.POST, instance=vente)
    if form.is_valid():
        form.save()
        messages.success(request, f'Statut de la vente {vente.numero_facture} mis a jour')
    else:
        messages.error(request, 'Erreur lors du changement de statut')
    
    return redirect('ventes:detail_vente', vente_id=vente.id)
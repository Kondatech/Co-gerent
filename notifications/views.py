from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Notification
import json

@login_required
def centre_notifications(request):
    """
    Centre de notifications de l'utilisateur.
    """
    # Récupérer toutes les notifications de l'utilisateur
    notifications = Notification.objects.filter(utilisateur=request.user)
    
    # Filtrer par statut
    statut = request.GET.get('statut', 'toutes')
    if statut == 'non_lues':
        notifications = notifications.filter(est_lue=False)
    elif statut == 'lues':
        notifications = notifications.filter(est_lue=True)
    
    # Compter les non lues
    non_lues = Notification.objects.filter(utilisateur=request.user, est_lue=False).count()
    
    # Pagination simple
    page = request.GET.get('page', 1)
    limit = 20
    offset = (int(page) - 1) * limit
    total = notifications.count()
    notifications_page = notifications[offset:offset + limit]
    
    context = {
        'notifications': notifications_page,
        'non_lues': non_lues,
        'statut': statut,
        'page': int(page),
        'total': total,
        'has_previous': int(page) > 1,
        'has_next': offset + limit < total,
        'previous_page': int(page) - 1,
        'next_page': int(page) + 1,
        'total_pages': (total + limit - 1) // limit,
    }
    return render(request, 'notifications/centre.html', context)


@login_required
@require_POST
@csrf_exempt
def marquer_lue(request):
    """
    API pour marquer une notification comme lue.
    """
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            utilisateur=request.user
        )
        notification.marquer_lue()
        
        # Si toutes les notifications sont lues, message de succès
        non_lues = Notification.objects.filter(utilisateur=request.user, est_lue=False).count()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marquée comme lue',
            'non_lues': non_lues
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notification non trouvée'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
@csrf_exempt
def marquer_toutes_lues(request):
    """
    API pour marquer toutes les notifications comme lues.
    """
    try:
        notifications = Notification.objects.filter(
            utilisateur=request.user, 
            est_lue=False
        )
        count = notifications.count()
        notifications.update(est_lue=True)
        
        return JsonResponse({
            'success': True,
            'message': f'{count} notification(s) marquée(s) comme lue(s)',
            'non_lues': 0
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def get_notifications_count(request):
    """
    API pour récupérer le nombre de notifications non lues.
    """
    non_lues = Notification.objects.filter(
        utilisateur=request.user, 
        est_lue=False
    ).count()
    
    return JsonResponse({
        'non_lues': non_lues
    })


@login_required
def get_notifications_recentes(request):
    """
    API pour récupérer les notifications récentes (pour le widget).
    """
    limit = request.GET.get('limit', 5)
    
    notifications = Notification.objects.filter(
        utilisateur=request.user
    ).order_by('-date_creation')[:int(limit)]
    
    data = []
    for notif in notifications:
        data.append({
            'id': notif.id,
            'type': notif.type,
            'type_display': notif.get_type_display(),
            'priorite': notif.priorite,
            'message': notif.message,
            'est_lue': notif.est_lue,
            'date_creation': notif.date_creation.strftime('%d/%m/%Y %H:%M'),
            'icone': notif.get_icone(),
            'couleur': notif.get_couleur(),
            'lien': notif.lien
        })
    
    return JsonResponse({
        'notifications': data,
        'non_lues': Notification.objects.filter(utilisateur=request.user, est_lue=False).count()
    })
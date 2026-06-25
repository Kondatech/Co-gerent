from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from .graph import executer_agent


@login_required
def chat(request):
    """
    Page de chat pour interagir avec les agents.
    """
    # Vérifier que l'utilisateur a une entreprise
    if not request.user.entreprise:
        messages.warning(request, 'Vous devez configurer votre entreprise avant d\'utiliser le chat.')
        return redirect('core:onboarding')
    
    # Vérifier que le profil est complet
    try:
        profil = request.user.entreprise.profil
        if not profil.complet:
            messages.warning(request, 'Veuillez compléter votre profil avant d\'utiliser le chat.')
            return redirect('core:onboarding')
    except:
        messages.warning(request, 'Veuillez compléter votre profil avant d\'utiliser le chat.')
        return redirect('core:onboarding')
    
    context = {
        'entreprise': request.user.entreprise,
        'utilisateur': request.user,
    }
    return render(request, 'agents/chat.html', context)


@login_required
@csrf_exempt
def api_chat(request):
    """
    API pour envoyer des messages au chatbot.
    """
    if request.method != 'POST':
        return JsonResponse({'erreur': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        requete = data.get('requete', '').strip()
        historique = data.get('historique', [])
        
        if not requete:
            return JsonResponse({'erreur': 'Veuillez poser une question'}, status=400)
        
        # Exécuter l'agent
        resultat = executer_agent(
            requete=requete,
            utilisateur_id=request.user.id,
            historique=historique
        )
        
        return JsonResponse({
            'reponse': resultat.get('reponse', ''),
            'agent': resultat.get('agent_utilise', 'inconnu'),
            'notification_necessaire': resultat.get('notification_necessaire', False),
            'notification_message': resultat.get('notification_message', '')
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'erreur': 'Format de données invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'erreur': f'Erreur: {str(e)}'}, status=500)
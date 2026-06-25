"""
Tâches Celery pour le système de notifications
"""
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Notification
import logging

logger = logging.getLogger(__name__)

@shared_task
def envoyer_notification(utilisateur_id, type_notif, message, priorite='MOYENNE', lien='', donnees=None):
    """
    Tâche pour envoyer une notification à un utilisateur.
    
    Args:
        utilisateur_id: ID de l'utilisateur
        type_notif: Type de notification (INFO, SUCCES, ALERTE, etc.)
        message: Message de la notification
        priorite: Priorité (BASSE, MOYENNE, HAUTE, CRITIQUE)
        lien: Lien associé
        donnees: Données supplémentaires (JSON)
    """
    from core.models import Utilisateur
    
    try:
        utilisateur = Utilisateur.objects.get(id=utilisateur_id)
        
        notification = Notification.objects.create(
            utilisateur=utilisateur,
            type=type_notif,
            priorite=priorite,
            message=message,
            lien=lien,
            donnees=donnees or {}
        )
        
        logger.info(f"Notification créée pour {utilisateur.email}: {message[:50]}")
        
        # Si priorité CRITIQUE, envoyer un email (à implémenter avec SMTP)
        if priorite == 'CRITIQUE':
            envoyer_email_notification.delay(
                utilisateur.email,
                f"[Co-Gérant] Alerte: {type_notif}",
                message
            )
        
        return notification.id
        
    except Utilisateur.DoesNotExist:
        logger.error(f"Utilisateur {utilisateur_id} non trouvé pour la notification")
        return None


@shared_task
def envoyer_email_notification(destinataire, sujet, message):
    """
    Tâche pour envoyer une notification par email (simulé pour le moment).
    """
    # Simulation d'envoi d'email
    logger.info(f"[EMAIL] À: {destinataire} | Sujet: {sujet} | Message: {message[:100]}...")
    
    # En production, utiliser django.core.mail
    # from django.core.mail import send_mail
    # send_mail(sujet, message, 'noreply@cogerent.com', [destinataire], fail_silently=False)
    
    return True


@shared_task
def notifier_recommandation_prioritaire(utilisateur_id, recommandation, donnees=None):
    """
    Tâche spécifique pour les recommandations prioritaires de l'agent Décision.
    """
    message = f"🎯 Recommandation stratégique : {recommandation[:100]}..."
    
    envoyer_notification.delay(
        utilisateur_id=utilisateur_id,
        type_notif='RECOMMANDATION',
        priorite='HAUTE',
        message=message,
        lien='/agents/chat/',
        donnees=donnees or {'recommandation': recommandation}
    )


@shared_task
def notifier_alerte_ca(utilisateur_id, ca_mois, objectif):
    """
    Tâche pour notifier une alerte sur le chiffre d'affaires.
    """
    message = f"💰 Alerte: Votre CA du mois ({ca_mois:,.0f} FCFA) est inférieur à l'objectif ({objectif:,.0f} FCFA)"
    
    envoyer_notification.delay(
        utilisateur_id=utilisateur_id,
        type_notif='ALERTE',
        priorite='HAUTE',
        message=message,
        lien='/ventes/'
    )


@shared_task
def notifier_relance_client(utilisateur_id, client_nom):
    """
    Tâche pour notifier qu'un client doit être relancé.
    """
    message = f"📞 Client à relancer: {client_nom}. Dernier achat datant de plus de 90 jours."
    
    envoyer_notification.delay(
        utilisateur_id=utilisateur_id,
        type_notif='INFO',
        priorite='MOYENNE',
        message=message,
        lien='/crm/'
    )

@shared_task
def publier_publications_programmees():
    """
    Tâche périodique pour publier les publications programmées.
    Appeler toutes les 5 minutes par Celery Beat.
    """
    from communication.models import PublicationProgrammee
    from agents.tools import AgentTools
    from django.utils import timezone
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Publications en attente dont la date est passee
    publications = PublicationProgrammee.objects.filter(
        statut='EN_ATTENTE',
        date_publication__lte=timezone.now()
    )
    
    for publication in publications:
        try:
            tools = AgentTools(publication.entreprise_id)
            resultat = tools.publier_maintenant(publication.id)
            
            if resultat.get('succes'):
                logger.info(f"Publication {publication.id} publiee avec succes")
            else:
                logger.error(f"Publication {publication.id} echec: {resultat.get('erreur')}")
                
        except Exception as e:
            logger.error(f"Erreur publication {publication.id}: {str(e)}")
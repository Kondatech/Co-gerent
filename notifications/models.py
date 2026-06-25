from django.db import models
from django.utils import timezone
from core.models import Utilisateur

class Notification(models.Model):
    """Modèle pour les notifications"""
    
    TYPES = [
        ('INFO', 'Information'),
        ('SUCCES', 'Succès'),
        ('ALERTE', 'Alerte'),
        ('EMAIL', 'Email'),
        ('RECOMMANDATION', 'Recommandation'),
        ('URGENT', 'Urgent'),
    ]
    
    PRIORITES = [
        ('BASSE', 'Basse'),
        ('MOYENNE', 'Moyenne'),
        ('HAUTE', 'Haute'),
        ('CRITIQUE', 'Critique'),
    ]
    
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Utilisateur'
    )
    type = models.CharField('Type', max_length=20, choices=TYPES, default='INFO')
    priorite = models.CharField('Priorité', max_length=20, choices=PRIORITES, default='MOYENNE')
    message = models.TextField('Message')
    est_lue = models.BooleanField('Lue', default=False)
    date_creation = models.DateTimeField('Date de création', auto_now_add=True)
    date_lecture = models.DateTimeField('Date de lecture', null=True, blank=True)
    lien = models.CharField('Lien associé', max_length=200, blank=True)
    
    # Métadonnées supplémentaires
    donnees = models.JSONField('Données supplémentaires', default=dict, blank=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['utilisateur', 'est_lue']),
            models.Index(fields=['date_creation']),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.message[:50]}..."
    
    def marquer_lue(self):
        """Marque la notification comme lue"""
        self.est_lue = True
        self.date_lecture = timezone.now()
        self.save()
    
    def marquer_non_lue(self):
        """Marque la notification comme non lue"""
        self.est_lue = False
        self.date_lecture = None
        self.save()
    
    @classmethod
    def get_non_lues(cls, utilisateur):
        """Récupère les notifications non lues d'un utilisateur"""
        return cls.objects.filter(utilisateur=utilisateur, est_lue=False)
    
    @classmethod
    def get_recentes(cls, utilisateur, limit=10):
        """Récupère les notifications récentes d'un utilisateur"""
        return cls.objects.filter(utilisateur=utilisateur).order_by('-date_creation')[:limit]
    
    def get_icone(self):
        """Retourne l'icône Font Awesome pour le type de notification"""
        icones = {
            'INFO': 'fa-info-circle',
            'SUCCES': 'fa-check-circle',
            'ALERTE': 'fa-exclamation-triangle',
            'EMAIL': 'fa-envelope',
            'RECOMMANDATION': 'fa-lightbulb',
            'URGENT': 'fa-bell',
        }
        return icones.get(self.type, 'fa-bell')
    
    def get_couleur(self):
        """Retourne la couleur Bootstrap pour le type de notification"""
        couleurs = {
            'INFO': 'info',
            'SUCCES': 'success',
            'ALERTE': 'warning',
            'EMAIL': 'primary',
            'RECOMMANDATION': 'purple',
            'URGENT': 'danger',
        }
        return couleurs.get(self.type, 'secondary')
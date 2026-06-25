from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Entreprise

class Client(models.Model):
    """Modèle représentant un client de l'entreprise"""
    
    SEGMENTS = [
        ('PREMIUM', 'Premium'),
        ('STANDARD', 'Standard'),
        ('BASIQUE', 'Basique'),
    ]
    
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name='Entreprise'
    )
    nom = models.CharField('Nom du client', max_length=200)
    email = models.EmailField('Email', blank=True, null=True)
    telephone = models.CharField('Téléphone', max_length=20, blank=True)
    adresse = models.TextField('Adresse', blank=True)
    segment = models.CharField('Segment', max_length=20, choices=SEGMENTS, default='STANDARD')
    
    # RFM (Récence, Fréquence, Montant)
    score_rfm = models.IntegerField(
        'Score RFM', 
        default=0, 
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    
    date_premier_achat = models.DateField('Date du premier achat', null=True, blank=True)
    date_dernier_achat = models.DateField('Date du dernier achat', null=True, blank=True)
    nombre_achats = models.PositiveIntegerField('Nombre d\'achats', default=0)
    montant_total_achats = models.DecimalField(
        'Montant total des achats (FCFA)',
        max_digits=15,
        decimal_places=0,
        default=0
    )
    
    date_creation = models.DateTimeField('Date de création', auto_now_add=True)
    date_modification = models.DateTimeField('Dernière modification', auto_now=True)
    est_actif = models.BooleanField('Client actif', default=True)
    
    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['-montant_total_achats']
        unique_together = ['entreprise', 'email']  # Un email unique par entreprise
    
    def __str__(self):
        return f"{self.nom} - {self.segment} - {self.score_rfm}"
    
    def get_niveau_rfm(self):
        """Retourne le niveau RFM"""
        if self.score_rfm >= 800:
            return 'Excellent'
        elif self.score_rfm >= 600:
            return 'Bon'
        elif self.score_rfm >= 400:
            return 'Moyen'
        else:
            return 'À améliorer'


class Interaction(models.Model):
    """Modèle représentant une interaction avec un client"""
    
    TYPES = [
        ('APPEL', 'Appel téléphonique'),
        ('EMAIL', 'Email'),
        ('RENCONTRE', 'Rencontre physique'),
        ('WHATSAPP', 'WhatsApp'),
        ('AUTRE', 'Autre'),
    ]
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='interactions',
        verbose_name='Client'
    )
    type = models.CharField('Type d\'interaction', max_length=20, choices=TYPES)
    date = models.DateTimeField('Date de l\'interaction', auto_now_add=True)
    description = models.TextField('Description', max_length=500)
    suivi = models.BooleanField('Suivi nécessaire', default=False)
    date_suivi = models.DateTimeField('Date de suivi', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Interaction'
        verbose_name_plural = 'Interactions'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.client.nom} - {self.type} - {self.date.strftime('%d/%m/%Y')}"
from django.db import models
from core.models import Entreprise, Utilisateur


class ConnexionFacebook(models.Model):
    """Connexion Facebook d'une entreprise - Version manuelle"""
    
    entreprise = models.OneToOneField(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='connexion_facebook',
        verbose_name='Entreprise'
    )
    page_id = models.CharField('ID de la page Facebook', max_length=100)
    page_nom = models.CharField('Nom de la page', max_length=200, blank=True, null=True)
    access_token = models.TextField('Token d\'acces Facebook')
    date_connexion = models.DateTimeField('Date de connexion', auto_now_add=True)
    date_modification = models.DateTimeField('Derniere modification', auto_now=True)
    est_active = models.BooleanField('Connexion active', default=True)
    
    class Meta:
        verbose_name = 'Connexion Facebook'
        verbose_name_plural = 'Connexions Facebook'
        unique_together = ['entreprise', 'page_id']
    
    def __str__(self):
        return f"{self.entreprise.nom} - {self.page_nom or self.page_id}"
    
    def est_token_valide(self):
        """Verifie si le token est encore valide (approximatif)"""
        # On ne peut pas vraiment vérifier sans appel API
        return self.est_active


class PublicationProgrammee(models.Model):
    """Publication Facebook programmee"""
    
    STATUS = [
        ('EN_ATTENTE', 'En attente de publication'),
        ('PUBLIEE', 'Publiee'),
        ('ECHEC', 'Echec'),
        ('ANNULEE', 'Annulee'),
    ]
    
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='publications',
        verbose_name='Entreprise'
    )
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='publications',
        verbose_name='Utilisateur'
    )
    page_id = models.CharField('ID de la page Facebook', max_length=100)
    page_nom = models.CharField('Nom de la page', max_length=200)
    
    contenu_texte = models.TextField('Contenu du post')
    
    date_publication = models.DateTimeField('Date de publication prevue', null=True, blank=True)
    date_publication_reelle = models.DateTimeField('Date de publication reelle', null=True, blank=True)
    
    statut = models.CharField('Statut', max_length=20, choices=STATUS, default='EN_ATTENTE')
    message_erreur = models.TextField('Message d\'erreur', blank=True, null=True)
    
    date_creation = models.DateTimeField('Date de creation', auto_now_add=True)
    date_modification = models.DateTimeField('Derniere modification', auto_now=True)
    
    publication_id_facebook = models.CharField('ID Facebook', max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Publication programmee'
        verbose_name_plural = 'Publications programmees'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.entreprise.nom} - {self.contenu_texte[:50]}..."
    
    def est_en_attente(self):
        return self.statut == 'EN_ATTENTE'
    
    def est_publiee(self):
        return self.statut == 'PUBLIEE'
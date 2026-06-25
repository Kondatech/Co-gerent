from django.db import models
from crm.models import Client
from core.models import Entreprise

class Vente(models.Model):
    """Modèle représentant une vente"""
    
    STATUS = [
        ('EN_COURS', 'En cours'),
        ('VALIDE', 'Validée'),
        ('LIVREE', 'Livrée'),
        ('ANNULEE', 'Annulée'),
    ]
    
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='ventes',
        verbose_name='Entreprise'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='ventes',
        verbose_name='Client',
        null=True,
        blank=True
    )
    
    numero_facture = models.CharField('Numéro de facture', max_length=50, unique=True)
    date_vente = models.DateTimeField('Date de vente', auto_now_add=True)
    montant_total = models.DecimalField(
        'Montant total (FCFA)',
        max_digits=15,
        decimal_places=0
    )
    statut = models.CharField('Statut', max_length=20, choices=STATUS, default='EN_COURS')
    description = models.TextField('Description', blank=True)
    
    date_modification = models.DateTimeField('Dernière modification', auto_now=True)
    
    class Meta:
        verbose_name = 'Vente'
        verbose_name_plural = 'Ventes'
        ordering = ['-date_vente']
    
    def __str__(self):
        return f"{self.numero_facture} - {self.montant_total} FCFA - {self.statut}"


class LigneVente(models.Model):
    """Modèle représentant une ligne de vente (détail)"""
    
    vente = models.ForeignKey(
        Vente,
        on_delete=models.CASCADE,
        related_name='lignes',
        verbose_name='Vente'
    )
    produit = models.CharField('Produit', max_length=200)
    quantite = models.PositiveIntegerField('Quantité', default=1)
    prix_unitaire = models.DecimalField('Prix unitaire (FCFA)', max_digits=10, decimal_places=0)
    total_ligne = models.DecimalField('Total ligne (FCFA)', max_digits=10, decimal_places=0)
    
    class Meta:
        verbose_name = 'Ligne de vente'
        verbose_name_plural = 'Lignes de vente'
    
    def __str__(self):
        return f"{self.produit} - {self.quantite} x {self.prix_unitaire} FCFA"
    
    def save(self, *args, **kwargs):
        self.total_ligne = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)
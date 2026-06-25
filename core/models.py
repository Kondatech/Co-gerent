"""
Modèles core pour Co-Gérant
- Utilisateur (extension du User Django)
- Entreprise
- ProfilEntreprise
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator

class Entreprise(models.Model):
    """Modèle représentant une entreprise (PME)"""
    
    SECTEURS = [
        ('COMMERCE', 'Commerce / Distribution'),
        ('SERVICES', 'Services'),
        ('AGRICULTURE', 'Agriculture / Agroalimentaire'),
        ('ARTISANAT', 'Artisanat'),
        ('TECHNOLOGIE', 'Technologie / Digital'),
        ('TRANSPORT', 'Transport / Logistique'),
        ('IMMOBILIER', 'Immobilier / Construction'),
        ('SANTE', 'Santé'),
        ('EDUCATION', 'Éducation / Formation'),
        ('AUTRE', 'Autre'),
    ]
    
    nom = models.CharField('Nom de l\'entreprise', max_length=200)
    secteur = models.CharField('Secteur d\'activité', max_length=50, choices=SECTEURS)
    ville = models.CharField('Ville', max_length=100)
    pays = models.CharField('Pays', max_length=100, default='Burkina Faso')
    date_creation = models.DateTimeField('Date de création', auto_now_add=True)
    date_modification = models.DateTimeField('Dernière modification', auto_now=True)
    est_active = models.BooleanField('Entreprise active', default=True)
    
    class Meta:
        verbose_name = 'Entreprise'
        verbose_name_plural = 'Entreprises'
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} - {self.secteur}"
    
    def get_utilisateurs_actifs(self):
        """Retourne les utilisateurs actifs de l'entreprise"""
        return self.utilisateurs.filter(est_actif=True)


class Utilisateur(AbstractUser):
    """Modèle utilisateur personnalisé pour Co-Gérant"""
    
    ROLES = [
        ('GERANT', 'Gérant'),
        ('COMMERCIAL', 'Commercial'),
        ('COMPTABLE', 'Comptable'),
        ('RESPONSABLE', 'Responsable'),
        ('AUTRE', 'Autre'),
    ]
    
    entreprise = models.ForeignKey(
        Entreprise, 
        on_delete=models.CASCADE, 
        related_name='utilisateurs',
        null=True, 
        blank=True,
        verbose_name='Entreprise'
    )
    role = models.CharField('Rôle', max_length=20, choices=ROLES, default='GERANT')
    telephone = models.CharField('Téléphone', max_length=20, blank=True)
    est_actif = models.BooleanField('Compte actif', default=True)
    date_derniere_connexion = models.DateTimeField('Dernière connexion', null=True, blank=True)
    
    # Champs pour l'onboarding
    onboarding_complete = models.BooleanField('Onboarding terminé', default=False)
    onboarding_date = models.DateTimeField('Date de l\'onboarding', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-date_joined']
    
    def __str__(self):
        if self.entreprise:
            return f"{self.get_full_name() or self.username} - {self.entreprise.nom}"
        return f"{self.get_full_name() or self.username} (sans entreprise)"
    
    def get_entreprise_active(self):
        """Retourne l'entreprise active de l'utilisateur"""
        return self.entreprise


class ProfilEntreprise(models.Model):
    """Profil détaillé de l'entreprise (onboarding)"""
    
    entreprise = models.OneToOneField(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='profil',
        verbose_name='Entreprise'
    )
    
    # Objectifs
    objectif_court_terme = models.TextField('Objectif court terme', max_length=500, blank=True)
    objectif_long_terme = models.TextField('Objectif long terme', max_length=500, blank=True)
    
    # Services prioritaires (stocké en JSON pour flexibilité)
    services_prioritaires = models.JSONField(
        'Services prioritaires', 
        default=list,
        help_text='Liste des services dont l\'entreprise a besoin en priorité'
    )
    
    # Informations complémentaires
    description_activite = models.TextField('Description de l\'activité', max_length=1000, blank=True)
    nombre_employes = models.PositiveIntegerField('Nombre d\'employés', null=True, blank=True)
    chiffre_affaires_annuel = models.DecimalField(
        'Chiffre d\'affaires annuel (FCFA)', 
        max_digits=15, 
        decimal_places=0,
        null=True, 
        blank=True
    )
    
    # Métadonnées
    date_creation = models.DateTimeField('Date de création du profil', auto_now_add=True)
    date_modification = models.DateTimeField('Dernière modification', auto_now=True)
    complet = models.BooleanField('Profil complet', default=False)
    
    class Meta:
        verbose_name = 'Profil entreprise'
        verbose_name_plural = 'Profils entreprise'
    
    def __str__(self):
        return f"Profil de {self.entreprise.nom}"
    
    def get_services_prioritaires_affichage(self):
        """Retourne les services prioritaires formatés pour l'affichage"""
        if not self.services_prioritaires:
            return "Aucun service prioritaire défini"
        return ", ".join(self.services_prioritaires)
    
    def est_complet(self):
        """Vérifie si le profil est complet"""
        return all([
            self.objectif_court_terme,
            self.objectif_long_terme,
            self.services_prioritaires,
        ])
    
class ResumeMemoire(models.Model):
    """Résumé des conversations et décisions prises"""
    
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='memoires',
        verbose_name='Entreprise'
    )
    contenu_resume = models.TextField('Contenu du résumé')
    date_maj = models.DateTimeField('Date de mise à jour', auto_now_add=True)
    
    # Métadonnées
    dernier_sujet = models.CharField('Dernier sujet abordé', max_length=200, blank=True)
    decisions_prises = models.JSONField('Décisions prises', default=list)
    recommandations = models.JSONField('Recommandations', default=list)
    
    class Meta:
        verbose_name = 'Résumé de mémoire'
        verbose_name_plural = 'Résumés de mémoire'
        ordering = ['-date_maj']
    
    def __str__(self):
        return f"Mémoire de {self.entreprise.nom} - {self.date_maj.strftime('%d/%m/%Y')}"
    
    def ajouter_decision(self, decision: str):
        """Ajoute une décision à la mémoire"""
        if not self.decisions_prises:
            self.decisions_prises = []
        self.decisions_prises.append({
            'decision': decision,
            'date': datetime.now().isoformat()
        })
        self.save()
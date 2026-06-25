from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Entreprise, Utilisateur, ProfilEntreprise

@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'secteur', 'ville', 'date_creation', 'est_active')
    list_filter = ('secteur', 'est_active', 'pays')
    search_fields = ('nom', 'ville')
    ordering = ('nom',)

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'entreprise', 'role', 'onboarding_complete', 'est_actif')
    list_filter = ('role', 'est_actif', 'onboarding_complete')
    search_fields = ('username', 'email', 'telephone')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations entreprise', {
            'fields': ('entreprise', 'role', 'telephone', 'est_actif', 'onboarding_complete')
        }),
    )

@admin.register(ProfilEntreprise)
class ProfilEntrepriseAdmin(admin.ModelAdmin):
    list_display = ('entreprise', 'complet', 'nombre_employes', 'date_creation')
    list_filter = ('complet',)
    search_fields = ('entreprise__nom', 'objectif_court_terme')
    readonly_fields = ('date_creation', 'date_modification')
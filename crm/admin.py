from django.contrib import admin
from .models import Client, Interaction

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'entreprise', 'segment', 'score_rfm', 'montant_total_achats', 'est_actif')
    list_filter = ('entreprise', 'segment', 'est_actif')
    search_fields = ('nom', 'email', 'telephone')
    readonly_fields = ('date_creation', 'date_modification')
    fieldsets = (
        ('Informations générales', {
            'fields': ('entreprise', 'nom', 'email', 'telephone', 'adresse')
        }),
        ('Segmentation', {
            'fields': ('segment', 'score_rfm')
        }),
        ('Historique achats', {
            'fields': ('date_premier_achat', 'date_dernier_achat', 'nombre_achats', 'montant_total_achats')
        }),
        ('Statut', {
            'fields': ('est_actif',)
        }),
    )

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('client', 'type', 'date', 'suivi')
    list_filter = ('type', 'suivi')
    search_fields = ('client__nom', 'description')
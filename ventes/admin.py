from django.contrib import admin
from .models import Vente, LigneVente

class LigneVenteInline(admin.TabularInline):
    model = LigneVente
    extra = 1

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('numero_facture', 'entreprise', 'client', 'montant_total', 'statut', 'date_vente')
    list_filter = ('entreprise', 'statut', 'date_vente')
    search_fields = ('numero_facture', 'client__nom')
    readonly_fields = ('date_vente', 'date_modification')
    inlines = [LigneVenteInline]
    fieldsets = (
        ('Informations générales', {
            'fields': ('entreprise', 'client', 'numero_facture')
        }),
        ('Montant et statut', {
            'fields': ('montant_total', 'statut')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )

@admin.register(LigneVente)
class LigneVenteAdmin(admin.ModelAdmin):
    list_display = ('vente', 'produit', 'quantite', 'prix_unitaire', 'total_ligne')
    search_fields = ('produit', 'vente__numero_facture')
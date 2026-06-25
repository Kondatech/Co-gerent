from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'type', 'priorite', 'message', 'est_lue', 'date_creation')
    list_filter = ('type', 'priorite', 'est_lue', 'date_creation')
    search_fields = ('message', 'utilisateur__email', 'utilisateur__username')
    readonly_fields = ('date_creation', 'date_lecture')
    fieldsets = (
        ('Informations générales', {
            'fields': ('utilisateur', 'type', 'priorite', 'message')
        }),
        ('Statut', {
            'fields': ('est_lue', 'date_lecture')
        }),
        ('Métadonnées', {
            'fields': ('lien', 'donnees')
        }),
    )
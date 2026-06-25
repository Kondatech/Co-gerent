from django import forms
from django.forms import inlineformset_factory
from .models import Vente, LigneVente
from crm.models import Client


class VenteForm(forms.ModelForm):
    """Formulaire pour creer/modifier une vente"""
    
    client = forms.ModelChoiceField(
        queryset=Client.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Client',
        required=False
    )
    
    class Meta:
        model = Vente
        fields = ['client', 'numero_facture', 'montant_total', 'statut', 'description']
        widgets = {
            'numero_facture': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FACT-2026-0001'}),
            'montant_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description de la vente'}),
        }
        labels = {
            'client': 'Client',
            'numero_facture': 'Numero de facture',
            'montant_total': 'Montant total (FCFA)',
            'statut': 'Statut',
            'description': 'Description',
        }
    
    def __init__(self, *args, entreprise=None, **kwargs):
        super().__init__(*args, **kwargs)
        if entreprise:
            self.fields['client'].queryset = Client.objects.filter(
                entreprise=entreprise,
                est_actif=True
            ).order_by('nom')


class LigneVenteForm(forms.ModelForm):
    """Formulaire pour une ligne de vente"""
    
    class Meta:
        model = LigneVente
        fields = ['produit', 'quantite', 'prix_unitaire']
        widgets = {
            'produit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control quantite-input', 'min': 1}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control prix-input', 'step': '0.01', 'min': 0}),
        }
        labels = {
            'produit': 'Produit',
            'quantite': 'Quantite',
            'prix_unitaire': 'Prix unitaire (FCFA)',
        }


# Formset pour gerer plusieurs lignes de vente
LigneVenteFormSet = inlineformset_factory(
    Vente,
    LigneVente,
    form=LigneVenteForm,
    extra=1,
    min_num=1,
    can_delete=True,
    can_delete_extra=True
)


class VenteStatutForm(forms.ModelForm):
    """Formulaire pour changer le statut d'une vente"""
    
    class Meta:
        model = Vente
        fields = ['statut']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
from django import forms
from django.core.validators import FileExtensionValidator
from .models import Client, Interaction


class ClientForm(forms.ModelForm):
    """Formulaire pour créer/modifier un client"""
    
    class Meta:
        model = Client
        fields = ['nom', 'email', 'telephone', 'adresse', 'segment', 'score_rfm', 'est_actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet du client'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@client.com'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+226 XX XX XX XX'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse complète'}),
            'segment': forms.Select(attrs={'class': 'form-select'}),
            'score_rfm': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 1000}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nom': 'Nom du client',
            'email': 'Adresse email',
            'telephone': 'Telephone',
            'adresse': 'Adresse',
            'segment': 'Segment',
            'score_rfm': 'Score RFM (0-1000)',
            'est_actif': 'Client actif',
        }
        help_texts = {
            'score_rfm': 'Score de recence, frequence et montant',
        }


class InteractionForm(forms.ModelForm):
    """Formulaire pour créer/modifier une interaction"""
    
    class Meta:
        model = Interaction
        fields = ['type', 'description', 'suivi', 'date_suivi']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Decrivez l\'interaction'}),
            'suivi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_suivi': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'type': 'Type d\'interaction',
            'description': 'Description',
            'suivi': 'Suivi necessaire',
            'date_suivi': 'Date de suivi',
        }


class ImportClientsForm(forms.Form):
    """Formulaire pour importer des clients depuis un CSV"""
    
    fichier_csv = forms.FileField(
        label='Fichier CSV',
        help_text='Format: nom, email, telephone, segment, score_rfm (segment: PREMIUM, STANDARD, BASIQUE)',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    
    dedupliquer_par = forms.ChoiceField(
        label='Criteres de deduplication',
        choices=[
            ('email', 'Email'),
            ('telephone', 'Telephone'),
            ('email_telephone', 'Email ou Telephone'),
        ],
        initial='email',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    ecraser_existants = forms.BooleanField(
        label='Ecraser les clients existants',
        help_text='Si coche, les clients existants seront mis a jour',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
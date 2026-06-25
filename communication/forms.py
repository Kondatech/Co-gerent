from django import forms
from .models import ConnexionFacebook


class ConnexionFacebookForm(forms.ModelForm):
    """Formulaire pour connecter une page Facebook avec token"""
    
    class Meta:
        model = ConnexionFacebook
        fields = ['page_id', 'page_nom', 'access_token']
        widgets = {
            'page_id': forms.TextInput(attrs={
                'class': 'form-glass w-full text-sm',
                'placeholder': 'Ex: 123456789012345'
            }),
            'page_nom': forms.TextInput(attrs={
                'class': 'form-glass w-full text-sm',
                'placeholder': 'Ex: Ma Page Entreprise'
            }),
            'access_token': forms.TextInput(attrs={
                'class': 'form-glass w-full text-sm',
                'placeholder': 'EAA... (token d\'acces)'
            }),
        }
        labels = {
            'page_id': 'ID de la page Facebook',
            'page_nom': 'Nom de la page (optionnel)',
            'access_token': 'Token d\'acces',
        }
        help_texts = {
            'page_id': 'Trouvez l\'ID dans l\'URL de votre page',
            'access_token': 'Generez un token depuis l\'outil Graph API Explorer',
        }
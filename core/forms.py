from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import Utilisateur, Entreprise, ProfilEntreprise

class InscriptionForm(UserCreationForm):
    """Formulaire d'inscription des utilisateurs"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'})
    )
    prenom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'})
    )
    nom = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'})
    )
    telephone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre téléphone (optionnel)'})
    )
    role = forms.ChoiceField(
        choices=Utilisateur.ROLES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )
    password2 = forms.CharField(
        label='Confirmation du mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez le mot de passe'})
    )
    
    class Meta:
        model = Utilisateur
        fields = ('prenom', 'nom', 'email', 'telephone', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les labels
        self.fields['prenom'].label = 'Prénom'
        self.fields['nom'].label = 'Nom'
        self.fields['email'].label = 'Adresse email'
        self.fields['telephone'].label = 'Téléphone'
        self.fields['role'].label = 'Votre rôle'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Utiliser l'email comme username
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['prenom']
        user.last_name = self.cleaned_data['nom']
        user.telephone = self.cleaned_data.get('telephone', '')
        user.role = self.cleaned_data['role']
        user.onboarding_complete = False
        
        if commit:
            user.save()
        return user


class ConnexionForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'})
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )
    
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            # Authentifier avec l'email
            try:
                user = Utilisateur.objects.get(email=email)
                self.user_cache = authenticate(self.request, username=user.username, password=password)
                if self.user_cache is None:
                    raise forms.ValidationError('Email ou mot de passe incorrect.')
            except Utilisateur.DoesNotExist:
                raise forms.ValidationError('Email ou mot de passe incorrect.')
        
        return self.cleaned_data


class OnboardingForm(forms.ModelForm):
    """Formulaire d'onboarding pour le profil de l'entreprise"""
    
    nom_entreprise = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Ma PME SARL'})
    )
    secteur = forms.ChoiceField(
        choices=Entreprise.SECTEURS,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    ville = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ouagadougou'})
    )
    pays = forms.CharField(
        max_length=100,
        required=False,
        initial='Burkina Faso',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    objectif_court_terme = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Augmenter notre chiffre d\'affaires de 20% dans les 6 prochains mois'})
    )
    objectif_long_terme = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Devenir le leader régional dans notre secteur d\'ici 3 ans'})
    )
    services_prioritaires = forms.MultipleChoiceField(
        required=True,
        choices=[
            ('CRM (Gestion de la relation client)', 'CRM (Gestion de la relation client)'),
            ('Suivi des ventes et performances', 'Suivi des ventes et performances'),
            ('Communication et marketing digital', 'Communication et marketing digital'),
            ('Aide à la décision stratégique', 'Aide à la décision stratégique'),
            ('Gestion des ressources humaines', 'Gestion des ressources humaines'),
            ('Suivi financier et comptabilité', 'Suivi financier et comptabilité'),
            ('Gestion des stocks', 'Gestion des stocks'),
            ('Planification et stratégie', 'Planification et stratégie'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    description_activite = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Décrivez brièvement votre activité'})
    )
    nombre_employes = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 10'})
    )
    
    class Meta:
        model = ProfilEntreprise
        fields = ('objectif_court_terme', 'objectif_long_terme', 'services_prioritaires', 
                  'description_activite', 'nombre_employes')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['services_prioritaires'].help_text = 'Sélectionnez au moins un service'
        self.fields['services_prioritaires'].required = True
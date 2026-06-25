Guide complet pour pusher votre code sur GitHub
1. CRÉER UN COMPTE GITHUB
Va sur https://github.com

Clique sur "Sign up"

Crée ton compte (gratuit)

2. CRÉER UN NOUVEAU DÉPÔT SUR GITHUB
Connecte-toi à GitHub

Clique sur le bouton "+" en haut à droite → "New repository"

Remplis les informations :

Repository name : cogerent (ou le nom que tu veux)

Description : "Copilote IA pour PME africaines"

Public/Private : Choisis Public (gratuit) ou Private

Ne coche PAS "Initialize this repository with a README"

Clique sur "Create repository"

3. INITIALISER LE DÉPÔT LOCAL
powershell
# Se positionner dans le dossier du projet
cd C:\Users\I-4M0\Documents\Documents\fasolab\copilot

# Initialiser le dépôt Git
git init
4. CRÉER UN FICHIER .gitignore
Crée un fichier .gitignore à la racine du projet :

powershell
# Créer le fichier .gitignore
New-Item -Path .gitignore -ItemType File -Force
Ajoute ce contenu au fichier .gitignore :

gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so
*.egg
*.egg-info/
dist/
build/
*.whl
*.log

# Django
*.sqlite3
db.sqlite3
*.sqlite
staticfiles/
media/

# Environment
.env
venv/
env/
ENV/
.venv/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db

# Celery
celerybeat-schedule
celerybeat.pid

# Logs
*.log
logs/

# Testing
.coverage
htmlcov/
.tox/
.pytest_cache/

# ngrok
ngrok.yml

# Tailwind
node_modules/
static/css/output.css

# Secrets
*.pem
*.key
*.crt
5. AJOUTER LES FICHIERS
powershell
# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Vérifier ce qui va être commité
git status
6. FAIRE LE PREMIER COMMIT
powershell
# Créer le premier commit
git commit -m "Initial commit: Co-Gerant - Copilote IA pour PME africaines

- Structure Django avec apps core, crm, ventes, notifications, agents, communication
- Authentification et onboarding
- Agents IA avec LangGraph (CRM, Ventes, Communication, Decision)
- Interface CRM et Ventes
- Systeme de notifications avec Celery
- Integration Facebook
- Design Glassmorphism avec Tailwind CSS
- Tests unitaires avec pytest"
7. LIER LE DÉPÔT LOCAL AU DÉPÔT DISTANT
powershell
# Ajouter l'URL du dépôt distant (remplace par ton URL)
git remote add origin https://github.com/TON_USERNAME/cogerent.git

# OU si tu préfères SSH (recommandé) :
git remote add origin git@github.com:TON_USERNAME/cogerent.git
8. PUSHER LE CODE
powershell
# Premier push (avec branche principale)
git push -u origin main

# Si ta branche principale s'appelle master :
git push -u origin master
9. SI TU AS UNE ERREUR DE BRANCHE
powershell
# Vérifier le nom de la branche
git branch

# Si c'est master, pousse vers master
git push -u origin master

# OU renommer master en main
git branch -m master main
git push -u origin main
10. COMMANDES COMPLÈTES RÉCAPITULATIVES
powershell
# Se positionner dans le projet
cd C:\Users\I-4M0\Documents\Documents\fasolab\copilot

# Initialiser Git
git init

# Créer le .gitignore
echo "__pycache__/" > .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "db.sqlite3" >> .gitignore
echo "staticfiles/" >> .gitignore
echo "media/" >> .gitignore
echo "node_modules/" >> .gitignore
echo "static/css/output.css" >> .gitignore
echo ".vscode/" >> .gitignore
echo ".idea/" >> .gitignore
echo "logs/" >> .gitignore
echo ".pytest_cache/" >> .gitignore
echo "__pycache__/" >> .gitignore

# Ajouter tous les fichiers
git add .

# Vérifier l'état
git status

# Premier commit
git commit -m "Initial commit: Co-Gerant - Copilote IA pour PME africaines"

# Lier au dépôt distant (à adapter)
git remote add origin https://github.com/TON_USERNAME/cogerent.git

# Pusher
git push -u origin main
11. COMMANDES UTILITAIRES
Voir l'état des fichiers
powershell
git status
Voir l'historique des commits
powershell
git log --oneline
Ajouter des modifications
powershell
git add .
git commit -m "Description des modifications"
git push
Créer une branche
powershell
git branch nom-de-la-branche
git checkout nom-de-la-branche
# OU en une ligne :
git checkout -b nom-de-la-branche
Pusher sur une branche
powershell
git push -u origin nom-de-la-branche
12. GÉRER LES FICHIERS SENSIBLES
⚠️ NE JAMAIS COMMITER CES FICHIERS
Fichier	Raison
.env	Contient les clés API et mots de passe
db.sqlite3	Base de données locale
media/	Fichiers uploadés
venv/	Environnement virtuel
*.pyc	Fichiers compilés Python
__pycache__/	Cache Python
*.log	Fichiers de logs
ngrok.yml	Token ngrok
Si tu as déjà commité un fichier sensible
powershell
# Supprimer le fichier du suivi
git rm --cached .env

# Ajouter au .gitignore
echo ".env" >> .gitignore

# Commit
git commit -m "Retirer .env du suivi"
git push
13. EXEMPLE DE COMMIT PAR SPRINT
powershell
# Sprint 0
git add .
git commit -m "Sprint 0: Setup Django + PostgreSQL + Bootstrap"

# Sprint 1
git add .
git commit -m "Sprint 1: Authentification et Onboarding"

# Sprint 2
git add .
git commit -m "Sprint 2: Agents LangGraph - CRM et Ventes"

# Sprint 3
git add .
git commit -m "Sprint 3: Memoire, Communication et Decision"

# Sprint 4
git add .
git commit -m "Sprint 4: Systeme de notifications"

# Sprint 5
git add .
git commit -m "Sprint 5: Tests unitaires"

# Sprint 6
git add .
git commit -m "Sprint 6: Interface CRM et Ventes"

# Sprint 7
git add .
git commit -m "Sprint 7: Design Glassmorphism - Tailwind CSS"

# Sprint 8
git add .
git commit -m "Sprint 8: Integration Facebook"
14. TAGS (VERSIONS)
powershell
# Créer un tag
git tag -a v1.0 -m "Version 1.0 - Premiere version complete"

# Pousser les tags
git push --tags
15. RÉSUMÉ VISUEL DU FLUX
text
┌─────────────────────────────────────────────────────────────────┐
│                     GITHUB                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │   https://github.com/ton_user/cogerent                   │ │
│  │   ┌─────────────────────────────────────────────────────┐ │ │
│  │   │   main (branche principale)                        │ │ │
│  │   │   ├── commit 1: Initial commit                     │ │ │
│  │   │   ├── commit 2: Sprint 1                          │ │ │
│  │   │   ├── commit 3: Sprint 2                          │ │ │
│  │   │   └── ...                                         │ │ │
│  │   └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              ▲                                 │
│                              │ git push                        │
│                              │                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │   ORDINATEUR LOCAL                                       │ │
│  │   ┌─────────────────────────────────────────────────────┐ │ │
│  │   │   C:\Users\...\copilot\                           │ │ │
│  │   │   ├── cogerent_project/                           │ │ │
│  │   │   ├── core/                                      │ │ │
│  │   │   ├── crm/                                       │ │ │
│  │   │   ├── ventes/                                    │ │ │
│  │   │   ├── agents/                                    │ │ │
│  │   │   ├── communication/                             │ │ │
│  │   │   ├── templates/                                 │ │ │
│  │   │   ├── static/                                    │ │ │
│  │   │   ├── tests/                                     │ │ │
│  │   │   ├── manage.py                                  │ │ │
│  │   │   └── .git/                                      │ │ │
│  │   └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
16. PROBLÈMES COURANTS ET SOLUTIONS
Problème : "Permission denied (publickey)"
Solution :

powershell
# Générer une clé SSH
ssh-keygen -t rsa -b 4096 -C "ton_email@example.com"

# Copier la clé
cat ~/.ssh/id_rsa.pub

# Ajouter sur GitHub : Settings → SSH and GPG keys → New SSH Key
Problème : "fatal: remote origin already exists"
Solution :

powershell
git remote set-url origin https://github.com/TON_USERNAME/cogerent.git
Problème : "Updates were rejected"
Solution :

powershell
git pull origin main --rebase
git push
Problème : "fatal: refusing to merge unrelated histories"
Solution :

powershell
git pull origin main --allow-unrelated-histories
git push
17. LIENS UTILES
GitHub : https://github.com

Documentation Git : https://git-scm.com/doc

Tutoriel Git : https://learngitbranching.js.org/

.gitignore générateur : https://www.toptal.com/developers/gitignore

Bon push sur GitHub ! 🚀

je met quoi en description
Voici les descriptions à utiliser pour ton dépôt GitHub :

1. DESCRIPTION COURTE (Short Description)
Version simple :

text
Co-Gérant - Copilote IA pour PME africaines (Django + LangGraph + OpenAI)
Version avec emojis :

text
🤖 Co-Gérant - Copilote IA pour PME africaines | Django · LangGraph · OpenAI
2. DESCRIPTION LONGUE (README.md)
Voici le contenu complet à mettre dans ton fichier README.md :

markdown
# 🤖 Co-Gérant - Copilote IA pour PME africaines

Co-Gérant est un assistant intelligent (copilote IA) destiné aux PME africaines, combinant un système de gestion (CRM, Ventes) avec une intelligence artificielle orchestrée par LangGraph.

[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-blue.svg)](https://python.langchain.com/docs/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture technique](#-architecture-technique)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Sprints réalisés](#-sprints-réalisés)
- [Technologies utilisées](#-technologies-utilisées)
- [Tests](#-tests)
- [Déploiement](#-déploiement)
- [Prochaines mises à jour](#-prochaines-mises-à-jour)
- [Contribution](#-contribution)
- [Contact](#-contact)

## 🚀 Fonctionnalités

### 🤖 Agents IA
| Agent | Rôle | Fonctionnalités |
|-------|------|-----------------|
| **Agent CRM** | Gestion des clients | Top clients, segments RFM, relances, statistiques |
| **Agent Ventes** | Analyse des ventes | Chiffre d'affaires, prévisions, performances |
| **Agent Communication** | Messages & publications | Messages de relance, publications Facebook |
| **Agent Décision** | Stratégie | Recommandations stratégiques, analyses croisées |

### 💼 Modules de gestion
- **CRM** : Liste clients, Fiche client, CRUD, Import CSV, Interactions
- **Ventes** : Liste ventes, Détail vente, CRUD, Lignes de vente, Gestion statuts

### 🔔 Système de notifications
- Notifications en temps réel
- Priorités (Basse, Moyenne, Haute, Critique)
- Centre de notifications
- Widget de compteur

### 📱 Intégrations
- **Facebook** : Connexion via token, Publication automatique
- **Email** : Envoi de messages (simulé)

### 🎨 Interface
- Design Glassmorphism
- Tailwind CSS
- Alpine.js & HTMX
- 100% responsive

## 🏗️ Architecture technique
┌─────────────────────────────────────────────────────────────────┐
│ Architecture Co-Gérant │
├─────────────────────────────────────────────────────────────────┤
│ │
│ ┌─────────────┐ ┌─────────────────────────────────────┐ │
│ │ Frontend │ │ Orchestrateur IA │ │
│ │ Tailwind │ │ LangGraph │ │
│ │ Alpine.js │────▶│ ┌─────────────────────────────┐ │ │
│ │ HTMX │ │ │ Superviseur │ │ │
│ └─────────────┘ │ └──────────┬──────────────────┘ │ │
│ │ │ │ │
│ │ ┌──────────┼──────────────────────┐ │ │
│ │ │ ▼ │ │ │
│ │ │ ┌─────────────┐ ┌───────────┐ │ │ │
│ │ │ │ Agent CRM │ │Agent Ventes│ │ │ │
│ │ │ ├─────────────┤ ├───────────┤ │ │ │
│ │ │ │Agent Comm. │ │Agent Dec. │ │ │ │
│ │ │ └─────────────┘ └───────────┘ │ │ │
│ │ └─────────────────────────────────┘ │ │
│ │ │ │ │
│ │ ┌──────────┴──────────┐ │ │
│ │ │ Mémoire │ │ │
│ │ │ (PostgreSQL/Redis) │ │ │
│ │ └─────────────────────┘ │ │
│ └─────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────┐│
│ │ Base de données PostgreSQL ││
│ │ Entreprise │ Utilisateur │ Client │ Vente │ Notification ││
│ └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

text

## 🛠️ Stack technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Django | 5.1 |
| Base de données | PostgreSQL | Latest |
| Frontend | Tailwind CSS + Alpine.js + HTMX | Latest |
| Orchestration IA | LangGraph | 0.2 |
| LLM | OpenAI GPT-4o-mini | Latest |
| Tâches asynchrones | Celery + Redis | 5.4 |
| Tests | pytest | 8.3 |
| Déploiement | Docker + ngrok | Latest |

## 📦 Installation

### Prérequis
- Python 3.10+
- PostgreSQL
- Redis (optionnel, pour Celery)
- Node.js (pour Tailwind)

### Étapes d'installation

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/cogerent.git
cd cogerent

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Installer Tailwind CSS
npm install
npm run build

# 5. Configurer les variables d'environnement
cp .env.example .env
# Modifier .env avec vos identifiants

# 6. Appliquer les migrations
python manage.py migrate

# 7. Créer un superutilisateur
python manage.py createsuperuser

# 8. Remplir avec des données de démonstration
python manage.py seed_data

# 9. Lancer le serveur
python manage.py runserver
🚀 Utilisation
Accès à l'application
Accueil : http://localhost:8000/

Dashboard : http://localhost:8000/dashboard/

Assistant IA : http://localhost:8000/agents/chat/

Admin : http://localhost:8000/admin/

Comptes de démonstration
Rôle	Email	Mot de passe
Gérant	demo@cogerent.com	demo123
Admin	admin@cogerent.com	admin123
Exemples de questions pour l'assistant IA
CRM :

"Quels sont mes meilleurs clients ?"

"Quels clients dois-je relancer ?"

Ventes :

"Quel est mon chiffre d'affaires du mois ?"

"Quelles sont mes prévisions de ventes ?"

Communication :

"Génère un message de relance pour Nadia"

"Publie une offre pour un ordinateur à 700 000 FCFA"

Décision :

"Comment augmenter mes ventes ?"

"Donne-moi des recommandations stratégiques"

📁 Structure du projet
text
cogerent/
├── cogerent_project/          # Configuration Django
├── core/                      # Gestion des entreprises et utilisateurs
├── crm/                       # Gestion de la relation client
├── ventes/                    # Gestion des ventes
├── notifications/             # Système de notifications
├── agents/                    # Orchestration IA (LangGraph)
├── communication/             # Communication et intégrations
├── templates/                 # Templates Tailwind
├── static/                    # Fichiers statiques
├── tests/                     # Tests unitaires
├── manage.py
├── requirements.txt
└── .env
✅ Sprints réalisés
Sprint	Description	Statut
Sprint 0	Setup Django + PostgreSQL + Bootstrap	✅
Sprint 1	Authentification et Onboarding	✅
Sprint 2	Agents LangGraph (CRM et Ventes)	✅
Sprint 3	Mémoire, Communication et Décision	✅
Sprint 4	Système de notifications	✅
Sprint 5	Tests unitaires	✅
Sprint 6	Interface CRM et Ventes	✅
Sprint 7	Design Glassmorphism - Tailwind CSS	✅
Sprint 8	Intégration Facebook	✅
🧪 Tests
bash
# Exécuter tous les tests
pytest

# Tests unitaires uniquement
pytest -m unit

# Avec couverture de code
pytest --cov=agents --cov=crm --cov=ventes
🚀 Déploiement
Accès distant avec ngrok
bash
# Lancer Django
python manage.py runserver

# Dans un autre terminal
ngrok http 8000
Docker (à venir)
bash
docker-compose up -d
📋 Prochaines mises à jour
Version 1.1 (3 mois)
📸 Images dans les publications Facebook

📊 Dashboard avancé avec graphiques

📱 Application mobile

📄 Export de rapports

Version 1.2 (6 mois)
💬 Intégration WhatsApp Business

📈 Analyse prédictive

🔔 Alertes personnalisées

👥 Multi-utilisateurs

Version 2.0 (12 mois)
🤖 Agents personnalisables

🔗 API publique

🌍 Multi-langues

📊 Tableaux de bord personnalisables

🤝 Contribution
Les contributions sont les bienvenues ! Voici comment contribuer :

Fork le projet

Crée ta branche (git checkout -b feature/AmazingFeature)

Commit tes changements (git commit -m 'Add AmazingFeature')

Push sur la branche (git push origin feature/AmazingFeature)

Ouvre une Pull Request

👨‍💻 Auteur
Votre Nom - Projet de fin d'études

📄 Licence
Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

🙏 Remerciements
Django pour le framework backend

LangChain pour LangGraph

OpenAI pour les modèles LLM

Tailwind CSS pour le design

⭐ N'oublie pas de mettre une étoile si ce projet t'a été utile !

text

---

## 3. BADGES POUR LE README

Tu peux ajouter ces badges en haut du README :

```markdown
[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-blue.svg)](https://python.langchain.com/docs/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com/)
[![Tailwind](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red.svg)](https://github.com/votre-username/cogerent)
4. TAGS GITHUB
Ajoute ces tags à ton dépôt pour qu'il soit plus visible :

text
cogerent, django, langgraph, openai, crm, ventes, ia, intelligence-artificielle, pme, afrique, copilote-ia, chat, assistant-ia, tailwind, glassmorphism, celery, redis, postgresql
5. TOPICS GITHUB
Dans les paramètres de ton dépôt, ajoute ces topics :

django

langgraph

openai

crm

pme

afrique

intelligence-artificielle

assistant-ia

tailwind-css

chatbot

machine-learning

python

6. COMMANDES POUR LE PREMIER PUSH
powershell
# 1. Créer le README.md
New-Item -Path README.md -ItemType File -Force

# 2. Copier le contenu du README ci-dessus dans le fichier

# 3. Ajouter les fichiers
git add .

# 4. Commit
git commit -m "Initial commit: Co-Gerant - Copilote IA pour PME africaines"

# 5. Lier au dépôt distant
git remote add origin https://github.com/TON_USERNAME/cogerent.git

# 6. Pusher
git push -u origin main

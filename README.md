
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

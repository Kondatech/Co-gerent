# 🤖 Co-Gérant - Copilote IA pour PME africaines

Co-Gérant est un assistant intelligent (copilote IA) destiné aux PME africaines, combinant un système de gestion (CRM, Ventes, Communication) avec une intelligence artificielle multi-agents orchestrée par LangGraph.

[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-blue.svg)](https://python.langchain.com/docs/langgraph)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange.svg)](https://openai.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture technique](#️-architecture-technique)
- [Stack technologique](#️-stack-technologique)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Sprints réalisés](#-sprints-réalisés)
- [Tests](#-tests)
- [Déploiement](#-déploiement)
- [Prochaines mises à jour](#-prochaines-mises-à-jour)
- [Mettre à jour le dépôt](#-mettre-à-jour-le-dépôt)
- [Auteurs](#-auteurs)
- [Licence](#-licence)

## 🚀 Fonctionnalités

### 🤖 Agents IA
| Agent | Rôle | Fonctionnalités |
|-------|------|-----------------|
| **Agent CRM** | Gestion des clients | Top clients, segments RFM, relances, statistiques |
| **Agent Ventes** | Analyse des ventes | Chiffre d'affaires, prévisions, performances |
| **Agent Communication** | Messages & publications | Messages de relance, publications Facebook programmées |
| **Agent Décision** | Stratégie | Recommandations priorisées, analyses croisées CRM/ventes/objectifs |

### 💼 Modules de gestion
- **CRM** : liste clients, fiche client, CRUD, import CSV, historique d'interactions
- **Ventes** : liste des ventes, détail de vente, CRUD, lignes de vente, gestion des statuts

### 🔔 Notifications
- Notifications déclenchées par les agents (ex. recommandation prioritaire, clients à relancer)
- Centre de notifications avec compteur en temps réel

### 📱 Intégrations
- **Facebook** : connexion via token, génération de post par IA, publication immédiate ou programmée
- **Email** : envoi de messages (simulé, journalisé en notification)

### 🎨 Interface
- Design Glassmorphism, Tailwind CSS, Alpine.js & HTMX
- 100% responsive

## 🏗️ Architecture technique

```text
┌─────────────────────────────────────────────────────────────────┐
│                        Architecture Co-Gérant                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌─────────────┐      ┌─────────────────────────────────────┐  │
│   │  Frontend   │      │         Orchestrateur IA             │  │
│   │  Tailwind   │      │            LangGraph                 │  │
│   │  Alpine.js  │─────▶│  ┌─────────────────────────────┐    │  │
│   │  HTMX       │      │  │        Superviseur           │    │  │
│   └─────────────┘      │  └──────────┬───────────────────┘    │  │
│                         │             │                        │  │
│                         │  ┌──────────┼──────────────────────┐ │  │
│                         │  │          ▼                      │ │  │
│                         │  │  ┌─────────────┐ ┌────────────┐ │ │  │
│                         │  │  │ Agent CRM   │ │Agent Ventes│ │ │  │
│                         │  │  ├─────────────┤ ├────────────┤ │ │  │
│                         │  │  │Agent Comm.  │ │Agent Déc.  │ │ │  │
│                         │  │  └─────────────┘ └────────────┘ │ │  │
│                         │  └─────────────────────────────────┘ │  │
│                         │             │                        │  │
│                         │  ┌──────────┴──────────┐             │  │
│                         │  │      Mémoire         │             │  │
│                         │  │  (PostgreSQL/Redis)   │             │  │
│                         │  └──────────────────────┘             │  │
│                         └─────────────────────────────────────┘  │
│                                                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                 Base de données PostgreSQL               │   │
│   │   Entreprise │ Utilisateur │ Client │ Vente │ Notification│  │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Stack technologique

| Composant | Technologie |
|-----------|-------------|
| Backend | Django 5.1 |
| Base de données | PostgreSQL |
| Frontend | Tailwind CSS + Alpine.js + HTMX |
| Orchestration IA | LangGraph + LangChain |
| LLM | OpenAI gpt-4o-mini |
| Tâches asynchrones | Celery + Redis + django-celery-beat |
| Tests | pytest, pytest-django, factory-boy, faker |

## 📦 Installation

### Prérequis
- Python 3.10+
- PostgreSQL
- Redis (pour Celery)
- Node.js (pour Tailwind CSS)

### Étapes

```bash
# 1. Cloner le projet
git clone https://github.com/Kondatech/Co-gerent.git
cd Co-gerent

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# 3. Installer les dépendances Python
pip install -r requirements.txt

# 4. Installer et compiler Tailwind CSS
npm install
npm run build

# 5. Configurer les variables d'environnement
cp .env.example .env
# Modifier .env avec vos identifiants (base de données, clé OpenAI, etc.)

# 6. Appliquer les migrations
python manage.py migrate

# 7. Créer un superutilisateur
python manage.py createsuperuser

# 8. Lancer le serveur
python manage.py runserver
```

## 🚀 Utilisation

### Accès à l'application
- Accueil : http://localhost:8000/
- Dashboard : http://localhost:8000/dashboard/
- Assistant IA : http://localhost:8000/agents/chat/
- Admin : http://localhost:8000/admin/

### Exemples de questions pour l'assistant IA

**CRM**
- « Quels sont mes meilleurs clients ? »
- « Quels clients dois-je relancer ? »

**Ventes**
- « Quel est mon chiffre d'affaires du mois ? »
- « Quelles sont mes prévisions de ventes ? »

**Communication**
- « Génère un message de relance pour Nadia »
- « Publie une offre pour un ordinateur à 700 000 FCFA »

**Décision**
- « Comment augmenter mes ventes ? »
- « Donne-moi des recommandations stratégiques »

## 📁 Structure du projet

```text
Co-gerent/
├── cogerent_project/     # Configuration Django (settings, urls)
├── core/                 # Entreprises, utilisateurs, profils, mémoire
├── crm/                  # Gestion de la relation client
├── ventes/                # Gestion des ventes
├── notifications/         # Système de notifications
├── agents/                # Orchestration IA (LangGraph, tools, LLM)
├── communication/         # Messages, intégration Facebook
├── templates/              # Templates Django + Tailwind
├── static/                 # Fichiers statiques (CSS, JS, images)
├── manage.py
├── requirements.txt
└── .env
```

## ✅ Sprints réalisés

| Sprint | Description | Statut |
|--------|--------------|--------|
| Sprint 0 | Setup Django + PostgreSQL | ✅ |
| Sprint 1 | Authentification et onboarding | ✅ |
| Sprint 2 | Agents LangGraph (CRM et Ventes) | ✅ |
| Sprint 3 | Mémoire, Communication et Décision | ✅ |
| Sprint 4 | Système de notifications | ✅ |
| Sprint 5 | Tests unitaires | ✅ |
| Sprint 6 | Interface CRM et Ventes | ✅ |
| Sprint 7 | Design Glassmorphism - Tailwind CSS | ✅ |
| Sprint 8 | Intégration Facebook | ✅ |

## 🧪 Tests

```bash
# Exécuter tous les tests
pytest

# Avec couverture de code
pytest --cov=agents --cov=crm --cov=ventes
```

## 🚀 Déploiement

### Accès distant avec ngrok (démonstration)
```bash
python manage.py runserver
# Dans un autre terminal
ngrok http 8000
```

> Voir la discussion sur l'hébergement pour une mise en production (Celery/Redis/PostgreSQL en services persistants — Railway ou Render sont mieux adaptés que les plateformes serverless).

## 📋 Prochaines mises à jour

**Version 1.1**
- Images dans les publications Facebook
- Dashboard avancé avec graphiques
- Export de rapports

**Version 1.2**
- Intégration WhatsApp Business
- Analyse prédictive
- Alertes personnalisées

**Version 2.0**
- Agents personnalisables
- API publique
- Multi-langues

## 🔄 Mettre à jour le dépôt

Le projet est versionné sur `master`. Pour proposer une mise à jour :

```bash
git add <fichiers modifiés>
git commit -m "description du changement"
git push origin master
```

## 👨‍💻 Auteurs

**KONDA Ibrahima** & **BANDE Abdoul**
Licence en Génie Logiciel — Université Virtuelle du Burkina Faso
Sous la supervision de **Dr KAM**

## 📄 Licence

Ce projet est sous licence MIT — voir le fichier [LICENSE](LICENSE).

## 🙏 Remerciements

Django · LangChain / LangGraph · OpenAI · Tailwind CSS

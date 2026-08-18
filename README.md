# 🚀 Smart ERP Pro — Système ERP Enterprise Hybride

**Smart ERP Pro** est une application web de gestion d'entreprise (Enterprise Resource Planning) de nouvelle génération. Elle combine la puissance analytique et la rapidité d'un backend **FastAPI**, une interface utilisateur moderne et réactive **Vue.js 3**, et la robustesse de **Dolibarr ERP** comme source de vérité opérationnelle.

---

## 🏗️ Architecture du Projet

```text
               ┌──────────────────────────────────────────────┐
               │    Frontend Vue.js 3 (Vite + Tailwind/CSS)    │
               └──────────────────────┬───────────────────────┘
                                      │ REST API / Axios
                                      ▼
               ┌──────────────────────────────────────────────┐
               │         Backend FastAPI (Python 3.12)        │
               └──────────────┬────────────────┬──────────────┘
                              │                │
             ORM SQLAlchemy   │                │ Client Async REST API
                              ▼                ▼
             ┌───────────────────┐        ┌───────────────────┐
             │   PostgreSQL 15   │        │   Dolibarr ERP    │
             │ (Cache & Audit)   │        │(Source Opération) │
             └───────────────────┘        └───────────────────┘
```

### 🛠️ Stack Technique

- **Frontend** : Vue.js 3 (Composition API), Vite, Pinia, Vue Router, Lucide Icons. Thème professionnel *Obsidian & Copper*.
- **Backend** : FastAPI, Python 3.12, Pydantic v2, SQLAlchemy, Alembic, JWT (OAuth2).
- **ERP Master** : Dolibarr ERP via REST API Client asynchrone (Httpx).
- **Base de données & Cache** : PostgreSQL 15, Redis.
- **Conteneurisation** : Docker & Docker Compose.

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé sur votre machine :

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommandé pour une installation rapide).
- Ou alternativement :
  - **Python 3.12+**
  - **Node.js 18+** & **npm**
  - **PostgreSQL 15+**

---

## 🚀 Lancement Rapide (Via Docker Compose)

C'est la méthode recommandée pour démarrer l'ensemble de l'écosystème en une seule commande.

### 1. Cloner le projet
```bash
git clone <URL_DU_DEPOT>
cd projet_soutenance
```

### 2. Démarrer les services
```bash
docker-compose up -d --build
```

Cette commande démarre automatiquement :
- 🛢️ **PostgreSQL** (`localhost:5432`)
- ⚙️ **Backend FastAPI** (`http://localhost:8000`)
- 💻 **Frontend Vue.js** (`http://localhost:5173`)
- 🏢 **Dolibarr ERP** (`http://localhost:8080`)

### 3. Accéder à l'application
- **Application Web Smart ERP** : [http://localhost:5173](http://localhost:5173)
- **Documentation API (Swagger UI)** : [http://localhost:8000/docs](http://localhost:8000/docs)
- **Interface Dolibarr ERP** : [http://localhost:8080](http://localhost:8080)

---

## 🔑 Identifiants de Connexion

Un compte administrateur est configuré par défaut à la première initialisation :

- **Email** : `admin@erp.com`
- **Mot de passe** : `Admin@123`
- **Rôle** : `ADMIN` (Accès complet à tous les modules)

---

## 💻 Lancement Manuel (Sans Docker)

Si vous préférez exécuter le backend et le frontend directement sur votre machine hôte :

### 1. Démarrer le Backend (FastAPI)

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv
# Activer l'environnement (Windows)
venv\Scripts\activate
# Activer l'environnement (Linux/macOS)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur uvicorn
uvicorn app.main:app --reload --port 8000
```

### 2. Démarrer le Frontend (Vue.js 3)

```bash
cd frontend

# Installer les dépendances npm
npm install

# Démarrer le serveur de développement Vite
npm run dev
```

Accédez ensuite à `http://localhost:5173`.

---

## 💡 Guide des Modules & Fonctionnalités

### 📊 1. Tableau de Bord Directorial & Analytics
- Visualisation synthétique du Chiffre d'Affaires, de la valeur du Stock et de la masse salariale.
- Graphiques de répartition et indicateurs clés de performance (KPI).

### 🛒 2. Achats & Approvisionnements
- **Référentiel Fournisseurs** : Gestion des tiers fournisseurs et conditions de règlement.
- **Bons de Commande Fournisseur** : Création et suivi des commandes d'achat.
- **Réception Stock** : Entrée en stock automatique des marchandises reçues.

### 📦 3. Stocks & Inventaires
- **Catalogue produits** : Gestion des articles, références (SKU), prix d'achat/vente.
- **Catégories & Familles** : Classification dynamique synchronisée avec Dolibarr.
- **Mouvements de stock** : Journal des entrées, sorties et ajustements avec traçabilité.

### 💼 4. Ventes & Clients
- **Référentiel Clients** : Gestion du fichier tiers client.
- **Devis Commercial (Pro-Forma)** : Établissement de devis multi-produits avec conversion directe en commande.
- **Pipeline Commandes Clients** : Saisie multi-articles avec calcul automatique du Total HT/TTC et déstockage synchrone.
- **Facturation & Règlements** : Émission des factures clients et enregistrement des règlements.

### 👥 5. Ressources Humaines & Paie
- **Annuaire Employés** : Fiches employés, postes et départements.
- **Congés & Absences** : Demandes et validation des congés.
- **Gestion des Paies** : Bulletins de paie, salaire brut, cotisations et net à payer.

### 🤝 6. Recrutement & Candidats
- **Offres d'Emploi** : Publication et gestion du statut des postes ouverts.
- **Suivi des Candidatures** : Pipeline de traitement des candidats (Nouveau, Entretien, Retenu, Rejeté).

### 🛡️ 7. Gouvernance, RBAC & Audit
- **Annuaire Utilisateurs & Rôles** : Gestion des habilitations fines (RBAC).
- **Journal d'Audit** : Traçabilité complète des actions effectuées dans le système.

---

## 🔄 Réinitialisation & Maintenance des Données

Pour réinitialiser les données de test (remettre la base de données dans un état propre) :

1. Connectez-vous en tant qu'administrateur dans l'application.
2. Accédez au module **Paramètres Système & Audit**.
3. Cliquez sur **Réinitialiser les données**.
*(Les comptes utilisateurs admin, rôles et permissions seront préservés).*

---

## 📄 Licence & Soutenance

Ce projet a été développé dans le cadre du projet de soutenance Smart ERP. Tous droits réservés.

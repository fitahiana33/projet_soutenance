1. Merise → Base de données

Besoins
   ↓
MCD
   ↓
MLD
   ↓
PostgreSQL / Dolibarr

2. UML → Fonctionnalités et comportement

Use Case
Class Diagram
Sequence Diagram
Activity Diagram

3. C4 Model → Architecture

Pour expliquer clairement :

Utilisateur
    ↓
Frontend Vue.js
    ↓
Backend FastAPI
    ↓
┌───────────────┬───────────────┐
│ PostgreSQL    │   Dolibarr    │
└───────────────┴───────────────┘
        ↓
   Services IA

4. Agile + Scrum → Gestion du développement

On développe progressivement :

Sprint 1 → Authentification
Sprint 2 → Utilisateurs / rôles
Sprint 3 → Intégration Dolibarr
Sprint 4 → RH
Sprint 5 → Stock
...
⭐ Pour la soutenance

Je présenterais donc notre démarche comme :

Méthodologie Agile Scrum, conception fonctionnelle et comportementale avec UML, conception des données avec Merise et modélisation de l'architecture avec le C4 Model.
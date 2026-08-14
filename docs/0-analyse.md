                    ┌──────────────────┐
                    │    Vue.js        │
                    │  Interface Web   │
                    └────────┬─────────┘
                             │
                         REST API
                             │
                    ┌────────▼─────────┐
                    │     FastAPI      │
                    └───────┬─┬────────┘
                            │ │
                ┌───────────┘ └────────────┐
                ▼                          ▼
       ┌─────────────────┐       ┌─────────────────┐
       │   PostgreSQL    │       │    Dolibarr     │
       │                 │       │                 │
       │ Auth            │       │ Clients         │
       │ Users           │       │ Fournisseurs    │
       │ Roles           │       │ Produits        │
       │ Permissions     │       │ Stocks          │
       │ IA              │       │ Achats          │
       │ Predictions     │       │ Ventes          │
       │ Recommendations │       │ RH              │
       │ Analytics       │       │ Factures        │
       └────────┬────────┘       └─────────────────┘
                │
                ▼
       ┌─────────────────┐
       │ Services IA     │
       │ Python          │
       │                 │
       │ Prévision       │
       │ Anomalies       │
       │ Scoring         │
       │ Recommandations │
       └─────────────────┘


| Donnée                       | Dolibarr | PostgreSQL |
| ---------------------------- | :------: | :--------: |
| Clients                      |     ✅    |      ❌     |
| Fournisseurs                 |     ✅    |      ❌     |
| Produits                     |     ✅    |      ❌     |
| Stock                        |     ✅    |      ❌     |
| Achats                       |     ✅    |      ❌     |
| Ventes                       |     ✅    |      ❌     |
| Factures                     |     ✅    |      ❌     |
| Employés                     |     ✅    |      ❌     |
| Utilisateurs de connexion    |     ❌    |      ✅     |
| Rôles                        |     ❌    |      ✅     |
| Permissions                  |     ❌    |      ✅     |
| Sessions / tokens            |     ❌    |      ✅     |
| Prédictions IA               |     ❌    |      ✅     |
| Recommandations IA           |     ❌    |      ✅     |
| Anomalies détectées          |     ❌    |      ✅     |
| KPI spécifiques              |     ❌    |      ✅     |
| Résultats de simulations     |     ❌    |      ✅     |
| Historique préparé pour l'IA |     ❌    |      ✅     |

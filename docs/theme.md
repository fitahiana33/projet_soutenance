1. Thème et sujet de stage
Thème

Intelligence artificielle et aide à la décision appliquées à la gestion des ressources d’entreprise

Sujet de stage

Conception et développement d’une plateforme intelligente d’aide à la décision intégrée à un ERP pour l’optimisation des ressources humaines, des achats et des stocks.

C'est cette formulation que je recommande pour ton rapport.

2. Description du projet

Le projet consiste à concevoir une plateforme web intelligente capable d’exploiter les données issues d’un ERP afin d’améliorer le pilotage et la prise de décision dans l’entreprise.

La plateforme couvrira principalement :

-Ressources humaines : employés, recrutement, contrats, congés, absences, temps de travail, paie, compétences et performances ;
-Achats et fournisseurs : demandes, commandes, réceptions, factures et suivi des fournisseurs ;
-Stocks et inventaires : mouvements, niveaux de stock, transferts, inventaires, valorisation et risques de rupture ;
-Ventes : commandes, livraisons, facturation et analyse des ventes ;
-Tableaux de bord décisionnels : KPI, statistiques, indicateurs par service et analyse des performances.

La partie innovante sera constituée d'un moteur intelligent permettant notamment :

-la prévision de la demande et des besoins en stock ;
-la détection d’anomalies dans les données RH, paie, achats ou stocks ;
-le scoring et le classement des fournisseurs ou candidats ;
-la recommandation d’actions aux responsables ;
-la simulation de scénarios afin d’évaluer l’impact d’une décision ;
-l'analyse des données pour identifier les risques et opportunités ;
-un assistant intelligent permettant d'interroger les données et les indicateurs de l'entreprise.

Architecture envisagée
                 ERP EXISTANT
                  (Dolibarr)
                      │
                      │ API
                      ▼
                ┌────────────┐
                │  FastAPI   │
                └─────┬──────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
Données / KPI(postgres)       Moteur IA
                                 │
                ┌────────────────┼───────────────┐
                ▼                ▼               ▼
            Prévision       Anomalies       Recommandation
                │                │               │
                └────────────────┼───────────────┘
                                ▼
                            Décisionnel
                                │
                                ▼
                            Vue.js
En une phrase pour l'encadreur

Il s'agit de développer une plateforme intelligente connectée à un ERP, qui transforme les données RH, achats, ventes et stocks en indicateurs, prédictions, détection d'anomalies et recommandations afin d'aider les responsables à prendre de meilleures décisions.
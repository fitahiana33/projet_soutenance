CAHIER DES CHARGES COMPLET
Projet de soutenance
Conception et développement d’une plateforme intelligente d’aide à la décision pour l’optimisation des ressources d’entreprise basée sur l’intelligence artificielle et l’analyse prédictive
1. Présentation générale
1.1 Contexte

Les entreprises utilisent de nombreuses données provenant de leurs activités quotidiennes :

ressources humaines ;
achats ;
ventes ;
stocks ;
fournisseurs ;
clients ;
produits ;
facturation ;
performances ;
coûts.

Ces données sont généralement exploitées pour enregistrer les opérations, mais elles sont moins souvent utilisées pour anticiper les problèmes et assister les responsables dans leurs décisions.

Le projet consiste donc à développer une plateforme capable de récupérer les données d'un ERP existant, notamment Dolibarr, de les analyser et de produire des informations décisionnelles.

2. Problématique

Une entreprise peut connaître :

des ruptures de stock imprévues ;
des surstocks ;
des achats coûteux ;
des fournisseurs peu fiables ;
des anomalies dans les transactions ;
des difficultés à analyser les performances ;
une mauvaise anticipation des besoins ;
une dispersion des informations ;
une difficulté à transformer les données en décisions.
Problématique principale

Comment exploiter intelligemment les données opérationnelles d'un ERP afin de prédire les risques, détecter les anomalies et fournir des recommandations permettant aux responsables de prendre des décisions plus pertinentes ?

3. Objectif général

Développer une plateforme web intelligente permettant de :

centraliser les informations utiles à l'analyse ;
exploiter les données provenant de Dolibarr ;
produire des indicateurs de performance ;
effectuer des analyses prédictives ;
détecter automatiquement certaines anomalies ;
comparer et évaluer différentes ressources ;
générer des recommandations ;
simuler différents scénarios ;
assister les responsables dans leurs décisions.
4. Objectifs spécifiques

Le système devra notamment permettre de :

gérer les utilisateurs et leurs permissions ;
gérer les rôles ;
récupérer les données de Dolibarr via API ;
synchroniser les données nécessaires ;
conserver les données propres à notre plateforme ;
analyser les données historiques ;
calculer des KPI ;
prévoir certaines évolutions ;
détecter des comportements anormaux ;
calculer des scores ;
proposer des recommandations ;
comparer différents scénarios ;
présenter les résultats dans des dashboards interactifs ;
assurer la traçabilité des actions.
5. Concept général du projet

Le projet sera organisé autour de trois niveaux.

┌──────────────────────────────────────┐
│       1. ERP OPÉRATIONNEL            │
│             DOLIBARR                 │
│                                      │
│ Achats • Ventes • Stock • RH • etc.  │
└──────────────────┬───────────────────┘
                   │
                   │ API
                   ▼
┌──────────────────────────────────────┐
│       2. PLATEFORME INTELLIGENTE     │
│              FASTAPI                 │
│                                      │
│ Data • Analytics • IA • Décision     │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│          3. INTERFACE WEB             │
│               VUE.JS                 │
│                                      │
│ Dashboards • Alertes • IA • KPI      │
└──────────────────────────────────────┘
6. Architecture des données

Nous utiliserons deux bases de données.

6.1 Base Dolibarr

Elle contient les données opérationnelles de l'ERP :

produits ;
stocks ;
fournisseurs ;
clients ;
achats ;
ventes ;
commandes ;
factures ;
utilisateurs ;
etc.

Nous ne devons pas modifier directement la structure interne de Dolibarr.

6.2 Notre base PostgreSQL

Elle contient les données propres à notre plateforme :

Users
Roles
Permissions
Audit logs
AI predictions
AI anomalies
AI recommendations
AI simulations
Analytics
Synchronisation
Configuration

Elle pourra également contenir les données RH ou décisionnelles que nous ne souhaitons pas gérer directement dans Dolibarr.

7. MODULE 1 — Authentification et sécurité
Fonctionnalités
Authentification
connexion ;
déconnexion ;
gestion du mot de passe ;
expiration de session ;
JWT ;
protection des routes.
Utilisateurs
création ;
modification ;
consultation ;
désactivation ;
réactivation ;
recherche ;
filtrage.
Rôles

Exemples :

ADMIN
DIRECTOR
HR_MANAGER
PURCHASE_MANAGER
SALES_MANAGER
STOCK_MANAGER
EMPLOYEE
ANALYST
Permissions

Exemples :

USER_READ
USER_CREATE
USER_UPDATE
STOCK_READ
STOCK_UPDATE
PURCHASE_CREATE
PURCHASE_VALIDATE
REPORT_READ
AI_READ
AI_SIMULATE
Sécurité avancée
RBAC ;
contrôle d'accès selon les attributs/contexte lorsque nécessaire ;
principe du moindre privilège ;
séparation des tâches ;
double validation pour certaines opérations sensibles ;
délégations temporaires ;
journalisation des actions.
8. MODULE 2 — Intégration avec Dolibarr

C'est un module essentiel puisque nous ne voulons pas recréer tout l'ERP.

Fonctionnalités
connexion à l'API Dolibarr ;
authentification API ;
récupération des données ;
synchronisation ;
gestion des erreurs ;
détection des données modifiées ;
synchronisation périodique ;
synchronisation manuelle.
Données synchronisées

Selon le périmètre retenu :

Produits
Stocks
Fournisseurs
Clients
Achats
Ventes
Commandes
Factures
Employés
9. MODULE 3 — Référentiel produits

Fonctionnalités :

liste des produits ;
recherche ;
filtrage ;
catégories ;
références ;
prix ;
état ;
stock disponible ;
historique des mouvements.
10. MODULE 4 — Gestion des stocks

Le système devra permettre d'analyser :

stock actuel ;
entrées ;
sorties ;
transferts ;
ajustements ;
inventaires ;
stock minimum ;
stock de sécurité ;
stock maximum ;
rotation ;
valorisation.
Méthodes de valorisation

Selon le périmètre retenu :

FIFO ;
CUMP ;
éventuellement comparaison des méthodes.
Lots et séries

Prévoir :

numéro de lot ;
numéro de série ;
date d'expiration ;
traçabilité ;
blocage des lots expirés ;
FEFO lorsque pertinent.
11. MODULE 5 — Achats

Fonctionnalités :

fournisseurs ;
demandes d'achat ;
commandes ;
réception ;
factures ;
historique des achats ;
prix d'achat ;
délais ;
performances fournisseurs.
Workflow
Demande
   ↓
Validation
   ↓
Commande
   ↓
Réception
   ↓
Contrôle
   ↓
Facturation

Les opérations sensibles pourront nécessiter une validation selon le rôle.

12. MODULE 6 — Analyse des fournisseurs

Pour chaque fournisseur :

prix moyen ;
délai moyen ;
taux de retard ;
taux de conformité ;
qualité ;
fréquence d'achat ;
évolution des prix.
Score fournisseur

Exemple :

Prix             30 %
Délai            25 %
Qualité          25 %
Fiabilité        20 %

Résultat :

Fournisseur A : 78 %
Fournisseur B : 93 %
Fournisseur C : 84 %

Le système peut ensuite proposer le fournisseur ayant le meilleur score selon les critères choisis.

13. MODULE 7 — Ventes

Fonctionnalités :

clients ;
commandes ;
livraisons ;
factures ;
produits vendus ;
chiffre d'affaires ;
historique ;
analyse par période ;
analyse par produit ;
analyse par client.
14. MODULE 8 — Ressources humaines

Le module RH sera intégré progressivement.

Employés
fiche employé ;
poste ;
service ;
contrat ;
ancienneté ;
historique professionnel.
Temps et absences
congés ;
absences ;
retards ;
heures supplémentaires ;
historique.
Paie

Selon les données disponibles :

salaire brut ;
retenues ;
salaire net ;
primes ;
heures supplémentaires ;
charges ;
historique.
Performance
objectifs ;
évaluations ;
compétences ;
formations ;
évolution.
15. MODULE 9 — Recrutement intelligent

Le système pourra gérer :

offres ;
candidatures ;
CV ;
candidats ;
compétences ;
expériences ;
diplômes.
Matching CV / poste

Exemple :

Poste :
Python Developer

Candidat A : 92 %
Candidat B : 81 %
Candidat C : 67 %

Le système doit également expliquer le résultat :

Python        ✓
FastAPI       ✓
PostgreSQL    ✓
Git           ✓
Expérience    ✓

Il s'agit d'un outil d'aide au tri et à l'analyse, et non d'une décision automatique définitive concernant un candidat.

16. MODULE 10 — Business Intelligence

C'est la partie analytique.

KPI stocks
taux de rotation ;
couverture de stock ;
valeur du stock ;
taux de rupture ;
stock dormant ;
évolution des entrées/sorties.
KPI achats
montant des achats ;
évolution des prix ;
délai moyen ;
taux de retard ;
performance fournisseur.
KPI ventes
chiffre d'affaires ;
évolution ;
produits les plus vendus ;
produits les moins vendus ;
marge lorsque les données permettent de la calculer.
KPI RH
effectif ;
absentéisme ;
ancienneté ;
turnover ;
masse salariale ;
heures supplémentaires.
17. MODULE 11 — Intelligence artificielle

C'est le cœur innovant du projet.

Nous ne construirons pas une seule IA.

Nous construirons un moteur IA composé de plusieurs fonctionnalités spécialisées.

17.1 Prévision
Stock

Le système analyse :

historique des ventes
+
consommation
+
saisonnalité
+
stock actuel
+
délais fournisseurs

Puis prédit :

Demande future
Risque de rupture
Besoin futur

Exemple :

Le produit X présente un risque élevé de rupture dans les prochaines semaines.

18. Détection d'anomalies

L'IA recherche des comportements inhabituels.

Exemples :

Prix habituel : 100 000 Ar
Nouveau prix : 180 000 Ar

→ anomalie potentielle.

Ou :

Consommation habituelle : 100 unités
Consommation actuelle : 450

→ anomalie potentielle.

Même principe pour :

achats ;
stocks ;
ventes ;
heures de travail ;
absences ;
paie.
19. IA RH prédictive

Le système pourra produire des indicateurs de risque concernant certaines situations RH.

Exemple :

Risque estimé : élevé

Facteurs :
- faible évolution
- nombreuses heures supplémentaires
- ancienneté importante
- faible mobilité

Le système ne prend pas la décision à la place du RH.

Il fournit :

un signal permettant au responsable d'analyser la situation.

20. Recommandations intelligentes

Le moteur combine plusieurs résultats.

Exemple :

Prévision
+
Stock actuel
+
Délai fournisseur
+
Historique
        ↓
Recommandation

Exemple :

Commander une quantité supplémentaire du produit X auprès du fournisseur B afin de réduire le risque de rupture.

21. Simulation décisionnelle

Le responsable pourra modifier une hypothèse.

Exemple
Situation actuelle

Stock : 250
Coût : 12 M Ar
Risque rupture : 8 %

Puis :

Que se passe-t-il si les ventes augmentent de 20 % ?

Le système calcule un scénario :

Stock nécessaire
Coût supplémentaire
Risque de rupture
Besoin d'achat
Impact estimé

Autres simulations :

augmentation des ventes ;
augmentation des prix fournisseurs ;
changement de fournisseur ;
augmentation du stock de sécurité ;
variation des effectifs ;
variation des coûts.
22. MODULE 12 — Assistant intelligent

Un assistant conversationnel pourra permettre de poser des questions telles que :

Quels produits présentent un risque de rupture ?

Quel fournisseur a le meilleur score ?

Pourquoi le coût des achats a augmenté ?

Quelles sont les anomalies détectées cette semaine ?

Quelle est l'évolution des ventes ?

L'assistant devra s'appuyer sur les données et résultats de notre système, plutôt que d'inventer des informations.

23. MODULE 13 — Tableau de bord direction

Le dashboard principal affichera :

Chiffre d'affaires
Valeur du stock
Achats
Ventes
Effectif
Masse salariale
Risques
Anomalies
Alertes

Avec :

graphiques ;
tableaux ;
indicateurs ;
tendances ;
alertes ;
scores ;
prédictions.
24. MODULE 14 — Tableau de bord intelligent

Différence importante :

Dashboard classique
Stock : 250
Ventes : 1 500
Achats : 800
Dashboard intelligent
⚠️ 3 produits risquent une rupture

📈 Demande prévue : +17 %

⚠️ Fournisseur B : hausse de prix de 14 %

💡 Commande recommandée

🔎 4 anomalies détectées

📊 Score global des fournisseurs : 87 %

C'est cette deuxième partie qui donne sa valeur au projet.

25. MODULE 15 — Notifications et alertes

Le système pourra générer :

alerte rupture ;
alerte stock excessif ;
alerte anomalie ;
alerte contrat ;
alerte expiration ;
alerte retard fournisseur ;
alerte KPI ;
alerte prédictive.
26. MODULE 16 — Audit et traçabilité

Toutes les opérations importantes doivent être journalisées.

Exemple :

Utilisateur
Action
Date
Heure
Module
Ancienne valeur
Nouvelle valeur
Adresse/IP si nécessaire

Exemple :

ADMIN
Modification fournisseur
12/08/2026 14:32
Prix : 100 000 → 150 000

Le journal d'audit doit être protégé contre les modifications ordinaires.

27. MODULE 17 — Gestion documentaire

Selon le temps disponible :

contrats ;
factures ;
documents RH ;
CV ;
justificatifs ;
rapports.

Avec :

téléchargement ;
consultation ;
classement ;
association à une entité ;
contrôle d'accès.
28. Gestion des rôles
Rôle	Accès principal
Admin	Administration complète
Direction	Tous les dashboards et décisions
RH	RH et recrutement
Responsable achats	Achats et fournisseurs
Responsable stock	Stocks et inventaires
Responsable ventes	Ventes
Analyste	Analytics / IA
Employé	Espace personnel

Les permissions seront contrôlées côté backend.

29. Architecture technique
Frontend
Vue.js
Vite
Vue Router
Pinia
Axios
Backend
Python
FastAPI
SQLAlchemy
Pydantic
JWT
IA
Python
Pandas
NumPy
Scikit-learn

Selon les modèles :

Statistiques
Machine Learning
NLP
LLM
Base
PostgreSQL
ERP
Dolibarr
API REST
Infrastructure
Docker
Docker Compose
30. Architecture logicielle

Nous utiliserons une architecture en couches :

┌──────────────────────────┐
│       Vue.js             │
│     Presentation         │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       FastAPI            │
│     API / Routes         │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│       Services           │
│    Business Logic        │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│     AI / Analytics       │
│ Prediction / Anomaly     │
│ Recommendation           │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│       Data Access        │
│      SQLAlchemy          │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│      PostgreSQL          │
└──────────────────────────┘

Et :

FastAPI
   │
   └──────────► Dolibarr API
31. Structure du backend

Nous conserverons l'architecture modulaire que nous avons déjà définie :

backend/
└── app/
    ├── main.py
    │
    ├── core/
    │   ├── config.py
    │   ├── database.py
    │   └── security.py
    │
    ├── models/
    │   ├── users/
    │   ├── roles/
    │   ├── permissions/
    │   └── authentication/
    │
    ├── schemas/
    │   ├── users/
    │   ├── roles/
    │   ├── permissions/
    │   └── authentication/
    │
    ├── api/
    │   └── routes/
    │       ├── users/
    │       ├── roles/
    │       ├── permissions/
    │       └── authentication/
    │
    ├── services/
    │   ├── users/
    │   ├── roles/
    │   ├── permissions/
    │   └── authentication/
    │
    ├── integrations/
    │   └── dolibarr/
    │
    ├── analytics/
    │   ├── stock/
    │   ├── purchases/
    │   ├── sales/
    │   └── hr/
    │
    └── ai/
        ├── forecasting/
        ├── anomaly_detection/
        ├── scoring/
        ├── recommendations/
        ├── simulations/
        └── assistant/
32. Architecture frontend
frontend/
└── src/
    ├── main.js
    ├── App.vue
    │
    ├── router/
    │
    ├── store/
    │
    ├── services/
    │   ├── api.js
    │   ├── auth.js
    │   ├── users.js
    │   ├── dolibarr.js
    │   └── ai.js
    │
    ├── views/
    │   ├── auth/
    │   ├── dashboard/
    │   ├── users/
    │   ├── hr/
    │   ├── stock/
    │   ├── purchases/
    │   ├── sales/
    │   └── ai/
    │
    └── components/
33. Base de données de notre plateforme

Les premières tables :

user_
roles
permissons
user_roles
role_permissions

Puis progressivement :

audit_logs

ai_predictions
ai_anomalies
ai_recommendations
ai_simulations

analytics_snapshots

sync_logs

Le schéma sera développé progressivement en fonction des modules.

34. Communication entre les systèmes
                    ┌───────────────┐
                    │   Dolibarr    │
                    └───────┬───────┘
                            │
                         REST API
                            │
                            ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    └───────┬───────┘
                            │
                 ┌──────────┴─────────┐
                 ▼                    ▼
          PostgreSQL             AI Engine
                 │                    │
                 └──────────┬─────────┘
                            ▼
                         Vue.js
35. Contraintes techniques

Le projet doit :

fonctionner avec Docker ;
être développé avec des technologies gratuites/open source ;
pouvoir fonctionner sur un PC personnel ;
être modulaire ;
être facilement extensible ;
utiliser des API ;
séparer les responsabilités ;
protéger les données ;
permettre l'évolution progressive des modules.
36. Contraintes liées à l'IA

L'objectif n'est pas d'entraîner un modèle gigantesque.

Les modèles seront adaptés aux données disponibles.

Données ERP
    ↓
Préparation
    ↓
Entraînement / calibration
    ↓
Évaluation
    ↓
Modèle
    ↓
Prédiction

Les performances des modèles devront être mesurées lorsque cela est pertinent.

Exemples :

MAE ;
RMSE ;
précision ;
rappel ;
F1-score ;
taux d'anomalies pertinentes.
37. Tests
Backend
tests unitaires ;
tests des services ;
tests API ;
tests d'authentification ;
tests des permissions.
Frontend
tests des composants importants ;
tests des appels API ;
tests des routes protégées.
IA
validation des données ;
évaluation des modèles ;
comparaison des performances ;
vérification des résultats.
38. Déploiement

Tout l'environnement devra être conteneurisé :

Docker Compose
│
├── frontend
├── backend
├── postgres
└── éventuellement services supplémentaires

Dolibarr pourra fonctionner séparément et être consommé via son API.

39. Livrables

À la fin du projet :

Application
frontend fonctionnel ;
backend fonctionnel ;
connexion PostgreSQL ;
connexion Dolibarr ;
modules principaux ;
dashboards ;
fonctionnalités IA.
Documentation
cahier des charges ;
analyse fonctionnelle ;
architecture ;
MCD/MLD ;
documentation API ;
documentation technique ;
documentation IA ;
manuel utilisateur ;
rapport de stage/soutenance.
Présentation
démonstration ;
scénarios de décision ;
résultats des modèles ;
KPI ;
comparaison avant/après ;
limites ;
perspectives.
40. Planning sur 3 mois

Il faut être réaliste : nous ne devons pas essayer de développer 20 modules complets en trois mois.

Mois 1 — Socle
Semaine 1
Architecture + Docker + PostgreSQL

Semaine 2
Authentification + utilisateurs + rôles + permissions

Semaine 3
Intégration API Dolibarr

Semaine 4
Synchronisation + premiers modules de données
Mois 2 — Fonctionnel + Analytics
Semaine 5
Stocks

Semaine 6
Achats + fournisseurs

Semaine 7
Ventes

Semaine 8
Dashboards + KPI
Mois 3 — IA + décisionnel
Semaine 9
Prévision

Semaine 10
Détection d'anomalies + scoring

Semaine 11
Recommandations + simulations

Semaine 12
Assistant IA + tests + documentation + soutenance

Le RH peut être développé en parallèle ou après le socle opérationnel, en fonction du niveau d'accès aux données et du temps restant.

41. Scénario principal de démonstration

C'est ce scénario que je privilégierais devant le jury.

Étape 1

Le responsable se connecte.

Étape 2

Il arrive sur le dashboard :

CA                 125 M Ar
Valeur stock        48 M Ar
Achats              32 M Ar
Produits à risque        7
Anomalies détectées      4
Étape 3

Le système détecte :

⚠️ Le produit X présente un risque élevé de rupture.

Étape 4

Le responsable ouvre l'analyse.

Le système explique :

Stock actuel : 25
Demande prévue : 76
Délai fournisseur : 12 jours
Risque : élevé
Étape 5

Le système recommande :

Commander une quantité supplémentaire auprès du fournisseur B.

Étape 6

Le responsable consulte les fournisseurs :

A → 78 %
B → 93 %
C → 84 %
Étape 7

Il lance une simulation :

« Que se passe-t-il si les ventes augmentent de 20 % ? »

Étape 8

Le système calcule l'impact sur :

stock ;
achats ;
coûts ;
risque de rupture.
Étape 9

Le responsable peut prendre sa décision.

Voilà le message que le jury doit retenir :

Le système ne se contente pas d'enregistrer ce qui s'est passé. Il analyse ce qui se passe, anticipe ce qui pourrait arriver et aide le responsable à décider quoi faire.

42. Valeur ajoutée du projet

Le projet apporte plusieurs niveaux de valeur :

ERP
 ↓
Centralisation des opérations
 ↓
Analytics
 ↓
Compréhension des données
 ↓
IA
 ↓
Prédiction
 ↓
Recommandation
 ↓
Simulation
 ↓
AIDE À LA DÉCISION

C'est précisément ce qui différencie notre projet d'un simple « logiciel de gestion d'entreprise ».

43. Résumé officiel du projet

Le projet consiste à concevoir et développer une plateforme web intelligente intégrée à un ERP existant, permettant de centraliser et d'analyser les données relatives aux ressources humaines, aux achats, aux ventes et aux stocks. La plateforme s'appuie sur des techniques d'analyse de données, d'intelligence artificielle et d'analyse prédictive afin de détecter les anomalies, prévoir certains événements, évaluer les ressources, générer des recommandations et simuler différents scénarios. L'objectif est de transformer les données opérationnelles de l'entreprise en informations exploitables afin d'améliorer le pilotage et la prise de décision.

Stack finale retenue
              ┌───────────────┐
              │   DOLIBARR    │
              │      ERP      │
              └───────┬───────┘
                      │
                     API
                      │
                      ▼
              ┌───────────────┐
              │    FASTAPI    │
              │    PYTHON     │
              └───────┬───────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   ┌─────────────┐         ┌─────────────┐
   │ PostgreSQL  │         │  AI / ML    │
   │ Notre DB    │         │   Engine    │
   └─────────────┘         └──────┬──────┘
                                  │
                                  ▼
                           ┌─────────────┐
                           │   VUE.JS    │
                           │  Dashboard  │
                           └─────────────┘
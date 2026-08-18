from datetime import datetime, date, timezone
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.permissions.permission import Permission
from app.models.roles.role import Role
from app.models.users.user import User
from app.models.hr.holiday import PublicHoliday
from app.models.system.parameter import SystemParameter
from app.models.hr.employee import Employee
from app.models.purchases.purchase import Supplier
from app.models.sales.sales import Customer
from app.models.products.product import Category, Product

ADMIN_EMAIL = "admin@erp.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_ROLE = "ADMIN"

DEFAULT_PERMISSIONS = [
    {"code": "USER_READ", "description": "Consulter les utilisateurs"},
    {"code": "USER_CREATE", "description": "Créer des utilisateurs"},
    {"code": "USER_UPDATE", "description": "Modifier des utilisateurs"},
    {"code": "USER_DELETE", "description": "Supprimer des utilisateurs"},
    {"code": "USER_ASSIGN_ROLE", "description": "Affecter des rôles aux utilisateurs"},
    {"code": "ROLE_READ", "description": "Consulter les rôles"},
    {"code": "ROLE_MANAGE", "description": "Gérer les rôles et permissions"},
    {"code": "PERMISSION_MANAGE", "description": "Gérer les permissions système"},
    {"code": "DOLIBARR_READ", "description": "Consulter les données Dolibarr"},
    {"code": "DOLIBARR_SYNC", "description": "Synchroniser les données Dolibarr"},
    {"code": "CATEGORY_READ", "description": "Consulter les catégories produits"},
    {"code": "CATEGORY_MANAGE", "description": "Gérer les catégories produits"},
    {"code": "PRODUCT_READ", "description": "Consulter les fiches produits"},
    {"code": "PRODUCT_MANAGE", "description": "Gérer les fiches produits"},
    {"code": "STOCK_READ", "description": "Consulter les stocks et inventaires"},
    {"code": "STOCK_UPDATE", "description": "Mettre à jour les stocks"},
    {"code": "STOCK_MANAGE", "description": "Gérer les mouvements et lots de stock"},
    {"code": "SUPPLIER_READ", "description": "Consulter la base fournisseurs"},
    {"code": "SUPPLIER_CREATE", "description": "Créer des fournisseurs"},
    {"code": "SUPPLIER_UPDATE", "description": "Modifier des fournisseurs"},
    {"code": "SUPPLIER_MANAGE", "description": "Gérer les fournisseurs (CRUD + notation)"},
    {"code": "PURCHASE_READ", "description": "Consulter les demandes et commandes d'achat"},
    {"code": "PURCHASE_CREATE", "description": "Créer des commandes d'achat"},
    {"code": "PURCHASE_UPDATE", "description": "Modifier des commandes d'achat"},
    {"code": "PURCHASE_VALIDATE", "description": "Valider des commandes d'achat"},
    {"code": "PURCHASE_DELETE", "description": "Supprimer des commandes d'achat"},
    {"code": "CUSTOMER_READ", "description": "Consulter la base clients"},
    {"code": "CUSTOMER_CREATE", "description": "Créer des clients"},
    {"code": "CUSTOMER_UPDATE", "description": "Modifier des clients"},
    {"code": "CUSTOMER_MANAGE", "description": "Gérer la base clients"},
    {"code": "SALES_READ", "description": "Consulter devis, commandes et factures clients"},
    {"code": "SALES_CREATE", "description": "Créer des devis et commandes clients"},
    {"code": "SALES_UPDATE", "description": "Modifier des devis et commandes clients"},
    {"code": "SALES_VALIDATE", "description": "Valider / facturer une commande client"},
    {"code": "SALES_MANAGE", "description": "Gérer le cycle de vente complet"},
    {"code": "HR_READ", "description": "Consulter les données RH"},
    {"code": "HR_CREATE", "description": "Créer des fiches employés"},
    {"code": "HR_UPDATE", "description": "Modifier des fiches employés"},
    {"code": "HR_MANAGE", "description": "Gérer le département RH"},
    {"code": "EMPLOYEE_READ", "description": "Consulter sa fiche employé"},
    {"code": "EMPLOYEE_MANAGE", "description": "Gérer les fiches employés"},
    {"code": "PAYROLL_READ", "description": "Consulter les bulletins de paie"},
    {"code": "PAYROLL_MANAGE", "description": "Générer les bulletins de paie"},
    {"code": "PAYROLL_VALIDATE", "description": "Valider et clôturer une paie"},
    {"code": "HOLIDAY_READ", "description": "Consulter les congés et absences"},
    {"code": "HOLIDAY_MANAGE", "description": "Valider / refuser les congés"},
    {"code": "AUDIT_READ", "description": "Consulter les journaux d'audit"},
    {"code": "AUDIT_MANAGE", "description": "Gérer et exporter les journaux d'audit"},
    {"code": "NOTIFICATION_READ", "description": "Consulter ses notifications"},
    {"code": "NOTIFICATION_MANAGE", "description": "Gérer et envoyer des notifications système"},
    {"code": "SYSTEM_READ", "description": "Consulter les paramètres système"},
    {"code": "SYSTEM_MANAGE", "description": "Gérer les paramètres système"},
    {"code": "REPORT_READ", "description": "Consulter les rapports et statistiques"},
    {"code": "AI_READ", "description": "Consulter les métriques et prédictions IA"},
    {"code": "AI_SIMULATE", "description": "Exécuter des simulations du moteur IA"},
]

DEFAULT_ROLES = [
    {"libelle": "ADMIN", "description": "Administrateur Système (Accès total)"},
    {"libelle": "DIRECTOR", "description": "Direction Générale & Supervision"},
    {"libelle": "HR_MANAGER", "description": "Responsable des Ressources Humaines"},
    {"libelle": "PURCHASE_MANAGER", "description": "Responsable des Achats & Approvisionnements"},
    {"libelle": "SALES_MANAGER", "description": "Responsable des Ventes & Commercial"},
    {"libelle": "STOCK_MANAGER", "description": "Responsable des Stocks & Logistique"},
    {"libelle": "EMPLOYEE", "description": "Employé standard"},
    {"libelle": "ANALYST", "description": "Analyste de données & Moteur IA"},
]

ROLE_PERMISSIONS_MAP = {
    "ADMIN": None,
    "DIRECTOR": [
        "USER_READ", "ROLE_READ",
        "DOLIBARR_READ", "DOLIBARR_SYNC",
        "CATEGORY_READ", "PRODUCT_READ",
        "STOCK_READ",
        "SUPPLIER_READ", "PURCHASE_READ", "PURCHASE_VALIDATE",
        "CUSTOMER_READ", "SALES_READ", "SALES_VALIDATE",
        "HR_READ", "EMPLOYEE_READ", "PAYROLL_READ",
        "HOLIDAY_READ", "HOLIDAY_MANAGE",
        "AUDIT_READ", "NOTIFICATION_READ",
        "SYSTEM_READ", "REPORT_READ", "AI_READ"
    ],
    "HR_MANAGER": [
        "USER_READ", "ROLE_READ",
        "HR_READ", "HR_CREATE", "HR_UPDATE", "HR_MANAGE",
        "EMPLOYEE_READ", "EMPLOYEE_MANAGE",
        "PAYROLL_READ", "PAYROLL_MANAGE", "PAYROLL_VALIDATE",
        "HOLIDAY_READ", "HOLIDAY_MANAGE",
        "NOTIFICATION_READ", "NOTIFICATION_MANAGE",
        "REPORT_READ"
    ],
    "PURCHASE_MANAGER": [
        "DOLIBARR_READ", "DOLIBARR_SYNC",
        "CATEGORY_READ", "PRODUCT_READ",
        "STOCK_READ", "STOCK_UPDATE",
        "SUPPLIER_READ", "SUPPLIER_CREATE", "SUPPLIER_UPDATE", "SUPPLIER_MANAGE",
        "PURCHASE_READ", "PURCHASE_CREATE", "PURCHASE_UPDATE", "PURCHASE_VALIDATE", "PURCHASE_DELETE",
        "NOTIFICATION_READ", "REPORT_READ"
    ],
    "SALES_MANAGER": [
        "DOLIBARR_READ", "DOLIBARR_SYNC",
        "CATEGORY_READ", "PRODUCT_READ",
        "STOCK_READ",
        "CUSTOMER_READ", "CUSTOMER_CREATE", "CUSTOMER_UPDATE", "CUSTOMER_MANAGE",
        "SALES_READ", "SALES_CREATE", "SALES_UPDATE", "SALES_VALIDATE", "SALES_MANAGE",
        "NOTIFICATION_READ", "REPORT_READ"
    ],
    "STOCK_MANAGER": [
        "DOLIBARR_READ",
        "CATEGORY_READ", "PRODUCT_READ",
        "STOCK_READ", "STOCK_UPDATE", "STOCK_MANAGE",
        "SUPPLIER_READ", "PURCHASE_READ",
        "SALES_READ",
        "NOTIFICATION_READ", "REPORT_READ"
    ],
    "EMPLOYEE": [
        "EMPLOYEE_READ",
        "HOLIDAY_READ",
        "PAYROLL_READ",
        "NOTIFICATION_READ"
    ],
    "ANALYST": [
        "DOLIBARR_READ",
        "CATEGORY_READ", "PRODUCT_READ",
        "STOCK_READ",
        "SUPPLIER_READ", "PURCHASE_READ",
        "CUSTOMER_READ", "SALES_READ",
        "HR_READ", "EMPLOYEE_READ", "PAYROLL_READ",
        "AUDIT_READ",
        "REPORT_READ", "AI_READ", "AI_SIMULATE"
    ],
}

DEFAULT_SUPPLIERS = [
    {"code": "SUP-001", "name": "Madagascar Goods Import", "email": "contact@mgi.mg", "phone": "+261 20 22 123 45", "address": "Lot IIM 123 Ampasanimalo, Antananarivo 101", "payment_terms": 30, "status": "ACTIVE"},
    {"code": "SUP-002", "name": "Tech Suppliers SARL", "email": "sales@techsuppliers.mg", "phone": "+261 34 05 888 99", "address": "Saropody, Ivandry, Antananarivo 105", "payment_terms": 15, "status": "ACTIVE"},
    {"code": "SUP-003", "name": "Global Distributors Ltd", "email": "info@global-distributors.mg", "phone": "+261 20 79 456 12", "address": "Ankorondrano, Antananarivo 101", "payment_terms": 45, "status": "ACTIVE"},
    {"code": "SUP-004", "name": "Local Producers Coop", "email": "coop@localproducers.mg", "phone": "+261 33 14 777 22", "address": "Route d'Alsaka, Antsirabe 110", "payment_terms": 0, "status": "ACTIVE"},
]

DEFAULT_CUSTOMERS = [
    {"code": "CLI-001", "name": "Entreprise ABC SA", "email": "contact@abc.mg", "phone": "+261 20 22 999 00", "address": "Avenue de l'Indépendance, Antananarivo 101", "credit_limit": 50000000.0, "payment_terms": 30},
    {"code": "CLI-002", "name": "Société XYZ SARL", "email": "direction@xyz.mg", "phone": "+261 34 01 222 33", "address": "Ivandry, Antananarivo 105", "credit_limit": 20000000.0, "payment_terms": 15},
    {"code": "CLI-003", "name": "Startup Numérique MG", "email": "hello@startup.mg", "phone": "+261 33 08 444 55", "address": "Ankerana, Antananarivo 102", "credit_limit": 5000000.0, "payment_terms": 0},
    {"code": "CLI-004", "name": "Industrie Textile Sud", "email": "commercial@textilesud.mg", "phone": "+261 20 53 666 88", "address": "Z.I. Andohatapenaka, Fianarantsoa 301", "credit_limit": 35000000.0, "payment_terms": 60},
    {"code": "CLI-005", "name": "Ministère de l'Industrie", "email": "achats@industrie.gov.mg", "phone": "+261 20 22 000 11", "address": "Antananarivo 101", "credit_limit": 100000000.0, "payment_terms": 90},
]

DEFAULT_EMPLOYEES = [
    {"matricule": "EMP-2025-001", "last_name": "RAKOTO", "first_name": "Jean", "email": "j.rakoto@entreprise.mg", "phone": "+261 34 11 222 33", "cin": "101 234 567 890", "gender": "H", "marital_status": "MARIE", "number_of_children": 3, "position": "Directeur Général", "department": "DIRECTION", "status": "ACTIF", "hiring_date": date(2020, 1, 15), "base_salary": 3500000.0},
    {"matricule": "EMP-2025-002", "last_name": "RANDRIAMANANTENA", "first_name": "Lala", "email": "l.randriamanantena@entreprise.mg", "phone": "+261 33 44 555 66", "cin": "102 345 678 901", "gender": "F", "marital_status": "MARIE", "number_of_children": 2, "position": "Responsable RH", "department": "RH", "status": "ACTIF", "hiring_date": date(2021, 3, 1), "base_salary": 1800000.0},
    {"matricule": "EMP-2025-003", "last_name": "ANDRIANARIVO", "first_name": "Tolotra", "email": "t.andrianarivo@entreprise.mg", "phone": "+261 32 77 888 99", "cin": "103 456 789 012", "gender": "H", "marital_status": "CELIBATAIRE", "number_of_children": 0, "position": "Responsable Achats", "department": "ACHATS", "status": "ACTIF", "hiring_date": date(2021, 6, 15), "base_salary": 1800000.0},
    {"matricule": "EMP-2025-004", "last_name": "RAZAFINDRAKOTO", "first_name": "Hanta", "email": "h.razafindrakoto@entreprise.mg", "phone": "+261 34 88 999 00", "cin": "104 567 890 123", "gender": "F", "marital_status": "DIVORCE", "number_of_children": 1, "position": "Responsable Commercial", "department": "VENTES", "status": "ACTIF", "hiring_date": date(2022, 2, 10), "base_salary": 1700000.0},
    {"matricule": "EMP-2025-005", "last_name": "RATSIMBAZAFY", "first_name": "Eric", "email": "e.ratsimbazafy@entreprise.mg", "phone": "+261 33 99 000 11", "cin": "105 678 901 234", "gender": "H", "marital_status": "CELIBATAIRE", "number_of_children": 0, "position": "Magasinier Chef", "department": "LOGISTIQUE", "status": "ACTIF", "hiring_date": date(2022, 4, 20), "base_salary": 1100000.0},
    {"matricule": "EMP-2025-006", "last_name": "RAZANAMANJATO", "first_name": "Sitraka", "email": "s.razanamanjato@entreprise.mg", "phone": "+261 32 00 111 22", "cin": "106 789 012 345", "gender": "H", "marital_status": "MARIE", "number_of_children": 2, "position": "Comptable", "department": "FINANCE", "status": "ACTIF", "hiring_date": date(2022, 9, 5), "base_salary": 1400000.0},
    {"matricule": "EMP-2025-007", "last_name": "ANDRIAMANANJARA", "first_name": "Fanja", "email": "f.andriamananjara@entreprise.mg", "phone": "+261 34 22 333 44", "cin": "107 890 123 456", "gender": "F", "marital_status": "MARIE", "number_of_children": 4, "position": "Commercial Sédentaire", "department": "VENTES", "status": "ACTIF", "hiring_date": date(2023, 1, 15), "base_salary": 850000.0},
    {"matricule": "EMP-2025-008", "last_name": "RAKOTONDRAMANANA", "first_name": "Tiana", "email": "t.rakotondramanana@entreprise.mg", "phone": "+261 33 55 666 77", "cin": "108 901 234 567", "gender": "H", "marital_status": "CELIBATAIRE", "number_of_children": 0, "position": "Développeur Full Stack", "department": "SI", "status": "ACTIF", "hiring_date": date(2023, 5, 1), "base_salary": 2200000.0},
]

DEFAULT_CATEGORIES = [
    {"code": "CAT-ELEC", "name": "Équipements Électroniques", "description": "Matériel informatique, téléphonie, électroménager"},
    {"code": "CAT-BUREAU", "name": "Fournitures de Bureau", "description": "Consommables, papeterie, mobilier de bureau"},
    {"code": "CAT-MOBILIER", "name": "Mobilier Professionnel", "description": "Mobilier de bureau et d'agencement"},
    {"code": "CAT-MATIERE", "name": "Matières Premières", "description": "Matières premières pour production"},
    {"code": "CAT-SERVICE", "name": "Services Tiers", "description": "Prestations de services externes"},
]

DEFAULT_PRODUCTS = [
    {"code": "PROD-STK-001", "name": "Ordinateur Portable 15\" i5 8Go/512Go SSD", "description": "Laptop professionnel 15.6 pouces, Intel Core i5 12ème génération, RAM 8Go, SSD 512Go", "category_code": "CAT-ELEC", "unit_price": 3850000.0, "stock_quantity": 12, "min_stock": 3, "is_active": True, "product_type": "STOCK"},
    {"code": "PROD-STK-002", "name": "Imprimante Laser Couleur A4", "description": "Imprimante laser couleur multifonction (impression + scan + copie + fax)", "category_code": "CAT-ELEC", "unit_price": 1450000.0, "stock_quantity": 5, "min_stock": 2, "is_active": True, "product_type": "STOCK"},
    {"code": "PROD-STK-003", "name": "Rame de papier A4 (500 feuilles)", "description": "Rame de papier blanc A4, 80g/m², ramette de 500 feuilles", "category_code": "CAT-BUREAU", "unit_price": 8500.0, "stock_quantity": 150, "min_stock": 30, "is_active": True, "product_type": "STOCK"},
    {"code": "PROD-STK-004", "name": "Cahier de texte 200 pages", "description": "Cahier à reliure intégrale, 200 pages grands carreaux", "category_code": "CAT-BUREAU", "unit_price": 12000.0, "stock_quantity": 85, "min_stock": 20, "is_active": True, "product_type": "STOCK"},
    {"code": "PROD-STK-005", "name": "Bureau professionnel L-shaped", "description": "Bureau d'angle en bois mélaminé avec caisson de rangement", "category_code": "CAT-MOBILIER", "unit_price": 780000.0, "stock_quantity": 7, "min_stock": 2, "is_active": True, "product_type": "STOCK"},
    {"code": "PROD-STK-006", "name": "Chaise ergonomique accoudoirs", "description": "Chaise de bureau ergonomique avec accoudoirs réglables et support lombaire", "category_code": "CAT-MOBILIER", "unit_price": 420000.0, "stock_quantity": 18, "min_stock": 5, "is_active": True, "product_type": "STOCK"},
    {"code": "PROD-SERV-001", "name": "Maintenance informatique (Heure)", "description": "Prestation de maintenance informatique / dépannage à l'heure", "category_code": "CAT-SERVICE", "unit_price": 75000.0, "stock_quantity": 0, "min_stock": 0, "is_active": True, "product_type": "SERVICE"},
    {"code": "PROD-SERV-002", "name": "Formation Excel Avancée (journée)", "description": "Formation professionnelle Excel niveau avancé - 1 journée par participant", "category_code": "CAT-SERVICE", "unit_price": 250000.0, "stock_quantity": 0, "min_stock": 0, "is_active": True, "product_type": "SERVICE"},
    {"code": "PROD-STK-007", "name": "Toner imprimante laser (noir)", "description": "Cartouche toner noir compatible imprimantes laser", "category_code": "CAT-ELEC", "unit_price": 185000.0, "stock_quantity": 24, "min_stock": 8, "is_active": True, "product_type": "STOCK"},
    {"code": "PROD-STK-008", "name": "Clé USB 64Go", "description": "Clé USB 64Go haute vitesse, format compact", "category_code": "CAT-ELEC", "unit_price": 45000.0, "stock_quantity": 35, "min_stock": 10, "is_active": True, "product_type": "STOCK"},
]

DEFAULT_PUBLIC_HOLIDAYS = [
    {"name": "Nouvel An", "date": date(2026, 1, 1), "is_recurring": True, "description": "Jour de l'An"},
    {"name": "Journée Internationale des Femmes", "date": date(2026, 3, 8), "is_recurring": True, "description": "Journée de la Femme"},
    {"name": "Commémoration des Martyrs", "date": date(2026, 3, 29), "is_recurring": True, "description": "Martyrs de 1947"},
    {"name": "Lundi de Pâques", "date": date(2026, 4, 6), "is_recurring": False, "description": "Fête religieuse"},
    {"name": "Fête du Travail", "date": date(2026, 5, 1), "is_recurring": True, "description": "Fête des travailleurs"},
    {"name": "Jeudi de l'Ascension", "date": date(2026, 5, 14), "is_recurring": False, "description": "Fête religieuse"},
    {"name": "Lundi de Pentecôte", "date": date(2026, 5, 25), "is_recurring": False, "description": "Fête religieuse"},
    {"name": "Fête de l'Indépendance", "date": date(2026, 6, 26), "is_recurring": True, "description": "Fête Nationale de Madagascar"},
    {"name": "Assomption", "date": date(2026, 8, 15), "is_recurring": True, "description": "Fête religieuse"},
    {"name": "Toussaint", "date": date(2026, 11, 1), "is_recurring": True, "description": "Fête des Saints"},
    {"name": "Noël", "date": date(2026, 12, 25), "is_recurring": True, "description": "Fête de Noël"}
]

DEFAULT_SYSTEM_PARAMETERS = [
    # RH & Paie Madagascar
    {"category": "RH_PAIE", "key": "cnaps_employee_rate", "value": "0.01", "label": "Cotisation CNaPS Salariale (%)", "description": "Taux de cotisation CNaPS retenu sur le salaire brut (1%)"},
    {"category": "RH_PAIE", "key": "cnaps_employer_rate", "value": "0.13", "label": "Cotisation CNaPS Patronale (%)", "description": "Taux de cotisation CNaPS à la charge de l'employeur (13%)"},
    {"category": "RH_PAIE", "key": "cnaps_ceiling_amount", "value": "568000.0", "label": "Plafond Mensuel CNaPS (Ar)", "description": "Plafond maximal soumis à la CNaPS (568 000 Ar par mois)"},
    {"category": "RH_PAIE", "key": "ostie_employee_rate", "value": "0.01", "label": "Cotisation OSTIE Salariale (%)", "description": "Taux d'assurance santé OSTIE salarié (1%)"},
    {"category": "RH_PAIE", "key": "ostie_employer_rate", "value": "0.05", "label": "Cotisation OSTIE Patronale (%)", "description": "Taux d'assurance santé OSTIE patronal (5%)"},
    {"category": "RH_PAIE", "key": "child_deduction_amount", "value": "2000.0", "label": "Déduction IRSA par Enfant (Ar)", "description": "Montant déductible de l'IRSA pour chaque enfant à charge (2 000 Ar)"},
    {"category": "RH_PAIE", "key": "irsa_min_tax", "value": "3000.0", "label": "IRSA Minimum Légal (Ar)", "description": "Seuil d'impôt IRSA minimal à prélever (3 000 Ar)"},

    # Heures Supplémentaires
    {"category": "HEURES_SUP", "key": "overtime_30_rate", "value": "1.30", "label": "Majoration Heures Sup +30%", "description": "Coefficient applicateur pour les 8 premières HS"},
    {"category": "HEURES_SUP", "key": "overtime_40_rate", "value": "1.40", "label": "Majoration Heures Sup +40%", "description": "Coefficient applicateur au-delà des 8 premières HS"},
    {"category": "HEURES_SUP", "key": "overtime_50_rate", "value": "1.50", "label": "Majoration Dimanche & Férié +50%", "description": "Coefficient applicateur travail jour férié / repos"},
    {"category": "HEURES_SUP", "key": "overtime_100_rate", "value": "2.00", "label": "Majoration Travail de Nuit / Férié +100%", "description": "Coefficient applicateur heures de nuit / jours fériés d'astreinte"},

    # Commercial & Logistique
    {"category": "COMMERCIAL_LOGISTIQUE", "key": "default_tva_rate", "value": "20.0", "label": "Taux de TVA par Défaut (%)", "description": "Taux de Taxe sur la Valeur Ajoutée (20%)"},
    {"category": "COMMERCIAL_LOGISTIQUE", "key": "default_stock_min_threshold", "value": "5", "label": "Seuil d'Alerte Stock Min", "description": "Seuil par défaut déclenchant une alerte de réapprovisionnement"},
    {"category": "COMMERCIAL_LOGISTIQUE", "key": "default_payment_terms_days", "value": "30", "label": "Délai de Paiement Client (Jours)", "description": "Conditions de règlement standards attribuées aux nouveaux clients"}
]


def seed_admin(db: Session) -> None:
    """Initialise les permissions, rôles, administrateur, jours fériés et paramètres système dans PostgreSQL."""

    # 1. Seeding des permissions de base
    permission_objs = {}
    for perm_data in DEFAULT_PERMISSIONS:
        perm = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if perm is None:
            perm = Permission(code=perm_data["code"], description=perm_data["description"])
            db.add(perm)
            db.flush()
        permission_objs[perm_data["code"]] = perm

    # 2. Seeding des rôles métier + affectation des permissions par rôle (RBAC spécialisé)
    role_objs = {}
    for role_data in DEFAULT_ROLES:
        role = db.query(Role).filter(Role.libelle == role_data["libelle"]).first()
        if role is None:
            role = Role(libelle=role_data["libelle"], description=role_data["description"])
            db.add(role)
            db.flush()
        role_objs[role_data["libelle"]] = role

    for role_label, perm_codes in ROLE_PERMISSIONS_MAP.items():
        role_obj = role_objs.get(role_label)
        if role_obj is None:
            continue
        if perm_codes is None:
            role_obj.permissions = list(permission_objs.values())
        else:
            perms = [permission_objs[c] for c in perm_codes if c in permission_objs]
            existing_codes = {p.code for p in role_obj.permissions}
            for p in perms:
                if p.code not in existing_codes:
                    role_obj.permissions.append(p)

    # 3. Seeding des utilisateurs (admin + responsables métiers)
    DEFAULT_USERS = [
        {"email": ADMIN_EMAIL, "name": "Administrateur", "first_name": "Smart ERP", "pwd": ADMIN_PASSWORD, "roles": [ADMIN_ROLE]},
        {"email": "j.rakoto@entreprise.mg", "name": "RAKOTO", "first_name": "Jean", "pwd": "DG@Entreprise2026", "roles": ["DIRECTOR"]},
        {"email": "l.randriamanantena@entreprise.mg", "name": "RANDRIAMANANTENA", "first_name": "Lala", "pwd": "RH@Entreprise2026", "roles": ["HR_MANAGER"]},
        {"email": "t.andrianarivo@entreprise.mg", "name": "ANDRIANARIVO", "first_name": "Tolotra", "pwd": "ACHAT@Entreprise2026", "roles": ["PURCHASE_MANAGER"]},
        {"email": "h.razafindrakoto@entreprise.mg", "name": "RAZAFINDRAKOTO", "first_name": "Hanta", "pwd": "VENTE@Entreprise2026", "roles": ["SALES_MANAGER"]},
        {"email": "e.ratsimbazafy@entreprise.mg", "name": "RATSIMBAZAFY", "first_name": "Eric", "pwd": "STOCK@Entreprise2026", "roles": ["STOCK_MANAGER"]},
        {"email": "t.rakotondramanana@entreprise.mg", "name": "RAKOTONDRAMANANA", "first_name": "Tiana", "pwd": "EMP@Entreprise2026", "roles": ["EMPLOYEE"]},
        {"email": "s.razanamanjato@entreprise.mg", "name": "RAZANAMANJATO", "first_name": "Sitraka", "pwd": "ANA@Entreprise2026", "roles": ["ANALYST"]},
    ]

    now = datetime.now(timezone.utc)
    email_to_user = {}
    for ud in DEFAULT_USERS:
        user = db.query(User).filter(User.email == ud["email"]).first()
        if user is None:
            user = User(
                name=ud["name"],
                first_name=ud["first_name"],
                email=ud["email"],
                password=hash_password(ud["pwd"]),
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            for rl in ud["roles"]:
                if role_objs.get(rl):
                    user.roles.append(role_objs[rl])
            db.add(user)
            db.flush()
        email_to_user[ud["email"]] = user

    # 4. Seeding des Catégories Produits
    category_objs = {}
    for cat_data in DEFAULT_CATEGORIES:
        cat = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if cat is None:
            cat = Category(name=cat_data["name"], description=cat_data.get("description", ""))
            db.add(cat)
            db.flush()
        category_objs[cat_data.get("code", cat_data["name"])] = cat

    # 5. Seeding des Produits (référence Category via category_id)
    for prod_data in DEFAULT_PRODUCTS:
        prod = db.query(Product).filter(Product.reference == prod_data.get("code", prod_data.get("reference", ""))).first()
        if prod is None:
            category_obj = category_objs.get(prod_data.get("category_code", prod_data.get("name", "")))
            prod = Product(
                reference=prod_data.get("code", prod_data.get("reference", f"SKU-{prod_data.get('name','')[:5]}")),
                label=prod_data.get("name", prod_data.get("label", "Produit")),
                description=prod_data.get("description", ""),
                category_id=category_obj.id_category if category_obj else None,
                price_sell=prod_data.get("unit_price", prod_data.get("price_sell", 0.0)),
                price_purchase=prod_data.get("price_purchase", 0.0),
                stock_quantity=prod_data.get("stock_quantity", 0),
                stock_min=prod_data.get("min_stock", prod_data.get("stock_min", 5)),
                status="ACTIF" if prod_data.get("is_active", True) else "INACTIF",
            )
            db.add(prod)

    # 6. Seeding des Fournisseurs
    for sup_data in DEFAULT_SUPPLIERS:
        sup = db.query(Supplier).filter(Supplier.code == sup_data["code"]).first()
        if sup is None:
            sup = Supplier(
                code=sup_data["code"],
                name=sup_data["name"],
                email=sup_data["email"],
                phone=sup_data["phone"],
                address=sup_data["address"],
                payment_terms_days=30,
                status=sup_data.get("status", "ACTIF"),
            )
            db.add(sup)

    # 7. Seeding des Clients
    for cli_data in DEFAULT_CUSTOMERS:
        cli = db.query(Customer).filter(Customer.code_client == cli_data["code"]).first()
        if cli is None:
            cli = Customer(
                code_client=cli_data["code"],
                name=cli_data["name"],
                email=cli_data["email"],
                phone=cli_data["phone"],
                address=cli_data["address"],
                credit_limit=cli_data.get("credit_limit"),
                payment_terms=cli_data.get("payment_terms", "30_DAYS"),
            )
            db.add(cli)

    # 8. Seeding des Employés (lien optionnel vers User via email pro)
    for emp_data in DEFAULT_EMPLOYEES:
        emp = db.query(Employee).filter(Employee.matricule == emp_data["matricule"]).first()
        if emp is None:
            linked_user = email_to_user.get(emp_data["email"])
            emp = Employee(
                matricule=emp_data["matricule"],
                last_name=emp_data["last_name"],
                first_name=emp_data["first_name"],
                email=emp_data["email"],
                phone=emp_data["phone"],
                cin_number=emp_data.get("cin"),
                gender=emp_data.get("gender"),
                marital_status=emp_data.get("marital_status"),
                children_count=emp_data.get("number_of_children", 0),
                job_title=emp_data.get("position", emp_data.get("job_title", "Employé")),
                department=emp_data["department"],
                status=emp_data.get("status", "ACTIF"),
                hire_date=_parse_date(emp_data.get("hiring_date") or emp_data.get("hire_date") or "2026-01-01"),
                base_salary=emp_data.get("base_salary", 0.0),
                user_id=linked_user.id_user if linked_user else None,
            )
            db.add(emp)

    # 9. Seeding des Jours Fériés Madagascar
    for hol_data in DEFAULT_PUBLIC_HOLIDAYS:
        exists = db.query(PublicHoliday).filter(PublicHoliday.name == hol_data["name"]).first()
        if exists is None:
            new_hol = PublicHoliday(
                name=hol_data["name"],
                date=hol_data["date"],
                is_recurring=hol_data["is_recurring"],
                description=hol_data["description"]
            )
            db.add(new_hol)

    # 10. Seeding des Paramètres Système Métiers (Persistés dans PostgreSQL)
    for param_data in DEFAULT_SYSTEM_PARAMETERS:
        exists = db.query(SystemParameter).filter(SystemParameter.key == param_data["key"]).first()
        if exists is None:
            new_param = SystemParameter(
                category=param_data["category"],
                key=param_data["key"],
                value=param_data["value"],
                label=param_data["label"],
                description=param_data["description"]
            )
            db.add(new_param)

    db.commit()


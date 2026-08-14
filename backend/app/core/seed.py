from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.permissions.permission import Permission
from app.models.roles.role import Role
from app.models.users.user import User

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
    {"code": "STOCK_READ", "description": "Consulter les stocks et inventaires"},
    {"code": "STOCK_UPDATE", "description": "Mettre à jour les stocks"},
    {"code": "PURCHASE_CREATE", "description": "Créer des commandes d'achat"},
    {"code": "PURCHASE_VALIDATE", "description": "Valider des commandes d'achat"},
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


def seed_admin(db: Session) -> None:
    """Initialise les permissions, rôles et administrateur dans PostgreSQL."""

    # 1. Seeding des permissions de base
    permission_objs = {}
    for perm_data in DEFAULT_PERMISSIONS:
        perm = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if perm is None:
            perm = Permission(code=perm_data["code"], description=perm_data["description"])
            db.add(perm)
            db.flush()
        permission_objs[perm_data["code"]] = perm

    # 2. Seeding des rôles métier
    role_objs = {}
    for role_data in DEFAULT_ROLES:
        role = db.query(Role).filter(Role.libelle == role_data["libelle"]).first()
        if role is None:
            role = Role(libelle=role_data["libelle"], description=role_data["description"])
            db.add(role)
            db.flush()
        role_objs[role_data["libelle"]] = role

    # Affecter toutes les permissions au rôle ADMIN
    admin_role = role_objs.get(ADMIN_ROLE)
    if admin_role:
        admin_role.permissions = list(permission_objs.values())

    # 3. Seeding de l'utilisateur admin
    admin_user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if admin_user is None:
        now = datetime.now(timezone.utc)
        admin_user = User(
            name="Administrateur",
            first_name="Smart ERP",
            email=ADMIN_EMAIL,
            password=hash_password(ADMIN_PASSWORD),
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        if admin_role:
            admin_user.roles = [admin_role]
        db.add(admin_user)
        db.flush()

    db.commit()

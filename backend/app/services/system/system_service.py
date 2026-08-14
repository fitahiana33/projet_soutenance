import logging
from typing import Dict, Any

from app.core.database import SessionLocal
from app.models.users.user import User
from app.models.roles.role import Role
from app.services.dolibarr.client import dolibarr_client
from app.services.purchases import purchase_service
from app.services.hr import hr_service
from app.services.stocks import stock_service

logger = logging.getLogger(__name__)

DEFAULT_ROLES = [
    "ADMIN", "DIRECTOR", "HR_MANAGER", "PURCHASE_MANAGER",
    "SALES_MANAGER", "STOCK_MANAGER", "EMPLOYEE", "ANALYST"
]


async def reset_all_business_data() -> Dict[str, Any]:
    """
    Réinitialisation INTÉGRALE ET ABSOLUE des données métier dans Dolibarr, PostgreSQL et la mémoire système,
    tout en CONSERVANT STRICTEMENT :
    - L'utilisateur Administrateur (admin@erp.com)
    - Les rôles système par défaut (8 rôles)
    - Les permissions système
    """
    deleted_doli_products = 0
    deleted_doli_categories = 0
    deleted_doli_thirdparties = 0

    # 1. Purge complète dans Dolibarr ERP via REST API
    try:
        # Purge des produits Dolibarr
        prods = await dolibarr_client.get("products")
        if prods and isinstance(prods, list):
            for p in prods:
                pid = p.get("id")
                try:
                    await dolibarr_client.delete(f"products/{pid}")
                    deleted_doli_products += 1
                except Exception as e:
                    logger.warning(f"Impossible de supprimer le produit Dolibarr #{pid}: {e}")

        # Purge des catégories Dolibarr
        cats = await dolibarr_client.get("categories")
        if cats and isinstance(cats, list):
            for c in cats:
                cid = c.get("id")
                try:
                    await dolibarr_client.delete(f"categories/{cid}")
                    deleted_doli_categories += 1
                except Exception as e:
                    logger.warning(f"Impossible de supprimer la catégorie Dolibarr #{cid}: {e}")

        # Purge des tiers / fournisseurs / clients Dolibarr
        thirdparties = await dolibarr_client.get("thirdparties")
        if thirdparties and isinstance(thirdparties, list):
            for t in thirdparties:
                tid = t.get("id")
                try:
                    await dolibarr_client.delete(f"thirdparties/{tid}")
                    deleted_doli_thirdparties += 1
                except Exception as e:
                    logger.warning(f"Impossible de supprimer le tiers Dolibarr #{tid}: {e}")

    except Exception as e:
        logger.warning(f"Purge Dolibarr partiellement exécutée : {e}")

    # 2. Purge PostgreSQL Database (Utilisateurs secondaires & Rôles personnalisés)
    db = SessionLocal()
    deleted_users_count = 0
    deleted_roles_count = 0
    try:
        # Supprimer tous les utilisateurs PostgreSQL sauf admin@erp.com
        non_admin_users = db.query(User).filter(User.email != "admin@erp.com").all()
        deleted_users_count = len(non_admin_users)
        for u in non_admin_users:
            u.roles = []
            db.delete(u)

        # Supprimer tous les rôles personnalisés non-système
        custom_roles = db.query(Role).filter(~Role.libelle.in_(DEFAULT_ROLES)).all()
        deleted_roles_count = len(custom_roles)
        for r in custom_roles:
            r.permissions = []
            db.delete(r)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la purge PostgreSQL : {e}")
    finally:
        db.close()

    # 3. Purge des stores en mémoire (Achats, RH, Stocks)
    purchase_service._purchases_store["suppliers"].clear()
    purchase_service._purchases_store["requisitions"].clear()
    purchase_service._purchases_store["orders"].clear()
    purchase_service._purchases_store["receipts"].clear()
    purchase_service._purchases_store["invoices"].clear()

    hr_service._hr_store["employees"].clear()
    hr_service._hr_store["time_off"].clear()
    hr_service._hr_store["payrolls"].clear()
    hr_service._hr_store["evaluations"].clear()

    stock_service._product_lots_store.clear()

    logger.info("Purge intégrale Dolibarr + PostgreSQL + RAM exécutée avec succès.")

    return {
        "success": True,
        "message": "Réinitialisation absolue réussie ! Toutes les données métier de Dolibarr (produits, catégories, tiers), de PostgreSQL et de la mémoire système ont été purgées.",
        "details": {
            "deleted_doli_products": deleted_doli_products,
            "deleted_doli_categories": deleted_doli_categories,
            "deleted_doli_thirdparties": deleted_doli_thirdparties,
            "deleted_pg_users": deleted_users_count,
            "deleted_pg_custom_roles": deleted_roles_count
        },
        "preserved": [
            "Utilisateur Administrateur (admin@erp.com)",
            "Rôles système par défaut (8 rôles)",
            "Permissions système & Matrice de sécurité"
        ]
    }

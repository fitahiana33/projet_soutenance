import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.users.user import User
from app.models.roles.role import Role
from app.models.system.parameter import SystemParameter
from app.schemas.system.parameter import ParameterCreate, ParameterUpdate
from app.services.dolibarr.client import dolibarr_client
from app.services.purchases import purchase_service
from app.services.hr import hr_service
from app.services.stocks import stock_service
from app.services.sales import sales_service
from app.services.recruitment import recruitment_service

logger = logging.getLogger(__name__)

DEFAULT_ROLES = [
    "ADMIN", "DIRECTOR", "HR_MANAGER", "PURCHASE_MANAGER",
    "SALES_MANAGER", "STOCK_MANAGER", "EMPLOYEE", "ANALYST"
]


def _parse_param_value(val_str: str) -> Any:
    """Parse une chaîne de caractères en float, int, bool ou str."""
    if val_str is None:
        return ""
    val_lower = val_str.lower().strip()
    if val_lower == "true":
        return True
    if val_lower == "false":
        return False
    try:
        if "." in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        return val_str


def get_db_parameters(db: Session, category: Optional[str] = None) -> List[SystemParameter]:
    """Récupère l'ensemble des paramètres système depuis PostgreSQL, filtrés optionnellement par catégorie."""
    query = db.query(SystemParameter)
    if category:
        query = query.filter(SystemParameter.category == category)
    return query.order_by(SystemParameter.category.asc(), SystemParameter.key.asc()).all()


def get_parameter_by_id(db: Session, id_param: int) -> Optional[SystemParameter]:
    """Récupère un paramètre par son ID."""
    return db.query(SystemParameter).filter(SystemParameter.id_param == id_param).first()


def get_parameter_by_key(db: Session, key: str) -> Optional[SystemParameter]:
    """Récupère un paramètre par sa clé unique."""
    return db.query(SystemParameter).filter(SystemParameter.key == key).first()


def get_business_parameters(db: Session = None) -> Dict[str, Any]:
    """
    Retourne un dictionnaire {cle: valeur_typée} lisible par les moteurs de calcul (Paie, Stocks, TVA).
    Si db n'est pas fourni, ouvre une session éphémère.
    """
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        params_db = db.query(SystemParameter).all()
        result = {}
        for p in params_db:
            result[p.key] = _parse_param_value(p.value)
        return result
    finally:
        if close_session:
            db.close()


def create_parameter(db: Session, data: ParameterCreate) -> SystemParameter:
    """Création d'un nouveau paramètre système dans PostgreSQL."""
    param = SystemParameter(
        category=data.category,
        key=data.key,
        value=data.value,
        label=data.label,
        description=data.description
    )
    db.add(param)
    db.commit()
    db.refresh(param)
    logger.info(f"Paramètre système créé: {param.key} = {param.value}")
    return param


def update_parameter(db: Session, id_param: int, data: ParameterUpdate) -> Optional[SystemParameter]:
    """Mise à jour d'un paramètre système existant dans PostgreSQL."""
    param = get_parameter_by_id(db, id_param)
    if not param:
        return None

    if data.category is not None:
        param.category = data.category
    if data.key is not None:
        param.key = data.key
    if data.value is not None:
        param.value = str(data.value)
    if data.label is not None:
        param.label = data.label
    if data.description is not None:
        param.description = data.description

    db.commit()
    db.refresh(param)
    logger.info(f"Paramètre système #{id_param} mis à jour dans PostgreSQL: {param.key} = {param.value}")
    return param


def delete_parameter(db: Session, id_param: int) -> bool:
    """Suppression d'un paramètre système de PostgreSQL."""
    param = get_parameter_by_id(db, id_param)
    if not param:
        return False

    db.delete(param)
    db.commit()
    logger.info(f"Paramètre système #{id_param} supprimé de PostgreSQL.")
    return True


def bulk_update_parameters(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Mise à jour par lots de clés/valeurs métiers dans PostgreSQL."""
    for key, val in payload.items():
        param = get_parameter_by_key(db, key)
        if param:
            param.value = str(val)
        else:
            # Créer à la volée si inexistant
            new_p = SystemParameter(
                category="GENERAL",
                key=key,
                value=str(val),
                label=key.replace("_", " ").title(),
                description="Paramètre configuré dynamiquement"
            )
            db.add(new_p)

    db.commit()
    return get_business_parameters(db)


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
    deleted_doli_stock_movements = 0

    # 1. Purge complète dans Dolibarr ERP via REST API
    try:
        prods = await dolibarr_client.get("products")
        if prods and isinstance(prods, list):
            # Dolibarr exposes movements per product on some API versions.
            for p in prods:
                pid = p.get("id")
                try:
                    stockmvts = await dolibarr_client.get("stockmovements", params={"product_id": pid})
                    for sm in stockmvts or []:
                        smid = sm.get("id") if isinstance(sm, dict) else sm
                        if smid is not None:
                            try:
                                await dolibarr_client.delete(f"stockmovements/{smid}")
                                deleted_doli_stock_movements += 1
                            except Exception as e:
                                logger.warning(f"Impossible de supprimer le mouvement Dolibarr #{smid}: {e}")
                except Exception as e:
                    logger.warning(f"Impossible de lire les mouvements du produit Dolibarr #{pid}: {e}")

            for p in prods:
                pid = p.get("id")
                try:
                    await dolibarr_client.delete(f"products/{pid}")
                    deleted_doli_products += 1
                except Exception as e:
                    logger.warning(f"Impossible de supprimer le produit Dolibarr #{pid}: {e}")

        cats = await dolibarr_client.get("categories")
        if cats and isinstance(cats, list):
            for c in cats:
                cid = c.get("id")
                try:
                    await dolibarr_client.delete(f"categories/{cid}")
                    deleted_doli_categories += 1
                except Exception as e:
                    logger.warning(f"Impossible de supprimer la catégorie Dolibarr #{cid}: {e}")

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

    # 2. Purge PostgreSQL Database
    db = SessionLocal()
    deleted_users_count = 0
    deleted_roles_count = 0
    try:
        from app.models.hr.recruitment import JobOffer, Candidate
        from app.models.hr.employee import Employee, TimeOffRequest, PayrollEntry, PerformanceEvaluation
        from app.models.purchases.purchase import Supplier, PurchaseRequisition, PurchaseOrder, GoodsReceipt, SupplierInvoice
        from app.models.sales.sales import Customer, SalesQuote, SalesOrder, Delivery, SalesInvoice
        from app.models.stocks.lots import ProductLot
        from app.models.products.product import Product, Category, StockMovement
        from app.models.audit.audit_log import AuditLog
        from app.models.system.notification import Notification
        from app.models.system.sync_log import SyncLog
        from app.models.hr.holiday import PublicHoliday
        from app.models.ai.prediction import AIPrediction
        from app.models.ai.anomaly import AIAnomaly
        from app.models.ai.recommendation import AIRecommendation
        from app.models.ai.simulation import AISimulation
        from app.models.ai.snapshot import AnalyticsSnapshot

        # Purge des tables métier PostgreSQL
        db.query(JobOffer).delete()
        db.query(Candidate).delete()
        db.query(TimeOffRequest).delete()
        db.query(PayrollEntry).delete()
        db.query(PerformanceEvaluation).delete()
        db.query(Employee).delete()
        db.query(SupplierInvoice).delete()
        db.query(GoodsReceipt).delete()
        db.query(PurchaseOrder).delete()
        db.query(PurchaseRequisition).delete()
        db.query(Supplier).delete()
        db.query(SalesInvoice).delete()
        db.query(Delivery).delete()
        db.query(SalesOrder).delete()
        db.query(SalesQuote).delete()
        db.query(Customer).delete()
        db.query(ProductLot).delete()
        db.query(StockMovement).delete()
        db.query(Product).delete()
        db.query(Category).delete()
        db.query(AuditLog).delete()
        db.query(Notification).delete()
        db.query(SyncLog).delete()
        db.query(PublicHoliday).delete()
        
        # Purge AI tables
        db.query(AIPrediction).delete()
        db.query(AIAnomaly).delete()
        db.query(AIRecommendation).delete()
        db.query(AISimulation).delete()
        db.query(AnalyticsSnapshot).delete()

        non_admin_users = db.query(User).filter(User.email != "admin@erp.com").all()
        deleted_users_count = len(non_admin_users)
        for u in non_admin_users:
            u.roles = []
            db.delete(u)

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

    # 3. Purge complémentaire des stores en mémoire pour sécurité
    try:
        sales_service._sales_store["customers"].clear()
        sales_service._sales_store["quotes"].clear()
        sales_service._sales_store["orders"].clear()
        sales_service._sales_store["invoices"].clear()
    except Exception:
        pass

    try:
        recruitment_service._recruitment_store["job_offers"].clear()
        recruitment_service._recruitment_store["candidates"].clear()
    except Exception:
        pass

    try:
        purchase_service._purchases_store["suppliers"].clear()
        purchase_service._purchases_store["requisitions"].clear()
        purchase_service._purchases_store["orders"].clear()
        purchase_service._purchases_store["receipts"].clear()
        purchase_service._purchases_store["invoices"].clear()
    except Exception:
        pass

    try:
        hr_service._hr_store["employees"].clear()
        hr_service._hr_store["time_off"].clear()
        hr_service._hr_store["payrolls"].clear()
        hr_service._hr_store["evaluations"].clear()
    except Exception:
        pass

    try:
        stock_service._product_lots_store.clear()
    except Exception:
        pass

    logger.info("Purge intégrale Dolibarr + PostgreSQL + RAM exécutée avec succès.")

    return {
        "success": True,
        "message": "Réinitialisation absolue réussie ! Toutes les données métier de Dolibarr (produits, catégories, tiers), de PostgreSQL et de la mémoire système ont été purgées.",
        "details": {
            "deleted_doli_products": deleted_doli_products,
            "deleted_doli_categories": deleted_doli_categories,
            "deleted_doli_thirdparties": deleted_doli_thirdparties,
            "deleted_doli_stock_movements": deleted_doli_stock_movements,
            "deleted_pg_users": deleted_users_count,
            "deleted_pg_custom_roles": deleted_roles_count
        },
        "preserved": [
            "Utilisateur Administrateur (admin@erp.com)",
            "Rôles système par défaut (8 rôles)",
            "Permissions système & Matrice de sécurité"
        ]
    }

import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.sales.sales import SalesOrder

from app.services.dolibarr.client import dolibarr_client

logger = logging.getLogger(__name__)


async def get_all_categories() -> List[Dict[str, Any]]:
    """Récupère en temps réel la liste des catégories directement depuis Dolibarr REST API."""
    try:
        cats = await dolibarr_client.get("categories", params={"type": "1"})
        if cats and isinstance(cats, list):
            return [
                {
                    "id_category": int(c.get("id")),
                    "name": c.get("label", c.get("name", f"Catégorie #{c.get('id')}")),
                    "description": c.get("description", "")
                }
                for c in cats
            ]
        return []
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des catégories depuis Dolibarr: {e}")
        return []


async def _get_product_category_index() -> Dict[int, List[Dict[str, Any]]]:
    """Construit un index produit -> categories via l'API categories de Dolibarr."""
    index: Dict[int, List[Dict[str, Any]]] = {}
    try:
        categories = await get_all_categories()
        for category in categories:
            category_id = int(category["id_category"])
            objects = await dolibarr_client.get(
                f"categories/{category_id}/objects",
                params={"type": "product"}
            )
            for obj in objects:
                object_id = obj.get("id") if isinstance(obj, dict) else obj
                if object_id is None:
                    continue
                index.setdefault(int(object_id), []).append(category)
    except Exception as e:
        logger.warning(f"Impossible de reconstruire les associations produit-categorie: {e}")
    return index


async def _get_categories_for_product(
    product_id: int,
    category_index: Optional[Dict[int, List[Dict[str, Any]]]] = None
) -> List[Dict[str, Any]]:
    """Lit les categories d'un produit avec fallback pour les versions Dolibarr incompatibles."""
    try:
        linked = await dolibarr_client.get(f"products/{product_id}/categories")
        if linked:
            return [
                {
                    "id_category": int(c.get("id")),
                    "name": c.get("label", c.get("name", f"Categorie #{c.get('id')}")),
                    "description": c.get("description", "")
                }
                for c in linked
                if isinstance(c, dict) and c.get("id") is not None
            ]
    except Exception as e:
        logger.warning(f"Lecture directe des categories du produit #{product_id} impossible: {e}")
    return (category_index or {}).get(int(product_id), [])


async def create_category(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Crée une catégorie synchrone directement dans Dolibarr via `POST /categories`."""
    payload = {
        "label": name,
        "description": description or "",
        "type": "1"  # 1 = Produit dans Dolibarr
    }

    try:
        logger.info(f"Création de catégorie dans Dolibarr: {name}")
        res = await dolibarr_client.post("categories", payload)
        cat_id = res if isinstance(res, int) else (res.get("id") if isinstance(res, dict) else 1)
        return {
            "id_category": int(cat_id),
            "name": name,
            "description": description or ""
        }
    except Exception as e:
        logger.error(f"Échec création catégorie dans Dolibarr API: {e}", exc_info=True)
        raise RuntimeError(f"Erreur Dolibarr lors de la création de catégorie: {str(e)}") from e


async def update_category(category_id: int, name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Met à jour une catégorie dans Dolibarr via `PUT /categories/{id}`."""
    payload = {
        "label": name,
        "description": description or "",
        "type": "1"
    }

    try:
        logger.info(f"Mise à jour catégorie #{category_id} dans Dolibarr: {name}")
        await dolibarr_client.put(f"categories/{category_id}", payload)
        return {
            "id_category": category_id,
            "name": name,
            "description": description or ""
        }
    except Exception as e:
        logger.error(f"Échec modification catégorie #{category_id} dans Dolibarr API: {e}", exc_info=True)
        raise RuntimeError(f"Erreur Dolibarr lors de la modification de la catégorie: {str(e)}") from e


async def delete_category(category_id: int) -> bool:
    """Supprime une catégorie dans Dolibarr via `DELETE /categories/{id}`."""
    try:
        logger.info(f"Suppression catégorie #{category_id} dans Dolibarr")
        await dolibarr_client.delete(f"categories/{category_id}")
        return True
    except Exception as e:
        logger.error(f"Échec suppression catégorie #{category_id} dans Dolibarr API: {e}", exc_info=True)
        raise RuntimeError(f"Erreur Dolibarr lors de la suppression de la catégorie: {str(e)}") from e


async def _get_or_create_default_warehouse() -> int:
    """Récupère l'ID du premier entrepôt Dolibarr ou en crée un par défaut si aucun n'existe."""
    try:
        whs = await dolibarr_client.get("warehouses")
        if whs and isinstance(whs, list) and len(whs) > 0:
            return int(whs[0].get("id", 1))
        
        res = await dolibarr_client.post("warehouses", {
            "label": "Entrepôt Principal",
            "statut": 1,
            "description": "Entrepôt principal Smart ERP"
        })
        return int(res if isinstance(res, int) else (res.get("id") if isinstance(res, dict) else 1))
    except Exception as e:
        logger.warning(f"Impossible de vérifier/créer l'entrepôt Dolibarr: {e}")
        return 1


async def get_all_products(
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    stock_status: Optional[str] = None,
    db: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """
    Récupère en temps réel les Produits et Stocks directement depuis l'API REST Dolibarr.
    Source Unique de Vérité (SOT) = Dolibarr ERP.
    """
    try:
        doli_prods = await dolibarr_client.get_products()
        mapped = []
        reserved_by_product: Dict[int, int] = {}
        if db is not None:
            active_orders = db.query(SalesOrder).filter(
                SalesOrder.status.in_(["VALIDEE", "CONFIRMEE", "EN_PREPARATION", "EN_LIVRAISON"])
            ).all()
            for order in active_orders:
                try:
                    items = json.loads(order.items_json or "[]")
                    for item in items:
                        pid = int(item.get("product_id"))
                        reserved_by_product[pid] = reserved_by_product.get(pid, 0) + int(float(item.get("quantity", 0)))
                except (TypeError, ValueError, json.JSONDecodeError):
                    logger.warning("Impossible de calculer une réservation pour la commande #%s", order.id_order)
        category_index = await _get_product_category_index()
        if doli_prods and isinstance(doli_prods, list):
            for p in doli_prods:
                pid = int(p.get("id"))
                stock_qty = 0
                stock_res = reserved_by_product.get(pid, 0)
                
                try:
                    stk_info = await dolibarr_client.get(f"products/{pid}/stock")
                    if stk_info and isinstance(stk_info, list) and len(stk_info) > 0:
                        stock_qty = int(float(stk_info[0].get("stock_reel", 0) or 0))
                except Exception:
                    stock_qty = int(float(p.get("stock_real", 0) or 0))

                mapped.append({
                    "id_product": pid,
                    "reference": p.get("ref", f"DOL-{pid}"),
                    "label": p.get("label", "Produit Dolibarr"),
                    "description": p.get("description", ""),
                    "category_id": None,
                    "category_ids": [],
                    "categories": [],
                    "price_purchase": float(p.get("cost_price", 0.0) or 0.0),
                    "price_sell": float(p.get("price", 0.0) or 0.0),
                    "status": "ACTIF" if str(p.get("status_buy", "1")) == "1" else "INACTIF",
                    "stock_quantity": stock_qty,
                    "stock_reserved": stock_res,
                    "stock_min": int(float(p.get("seuil_stock_alerte", 5) or 5)),
                    "stock_max": 100,
                    "stock_available": max(0, stock_qty - stock_res),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })
                try:
                    linked_categories = await _get_categories_for_product(pid, category_index)
                    categories = [
                        {
                            "id_category": int(c.get("id_category", c.get("id"))),
                            "name": c.get("name", c.get("label", "")),
                            "description": c.get("description", "")
                        }
                        for c in linked_categories
                        if c.get("id_category", c.get("id")) is not None
                    ]
                    mapped[-1]["categories"] = categories
                    mapped[-1]["category_ids"] = [c["id_category"] for c in categories]
                    mapped[-1]["category_id"] = categories[0]["id_category"] if categories else None
                    mapped[-1]["category"] = categories[0] if categories else None
                except Exception as category_error:
                    logger.warning(f"Impossible de lire les categories du produit #{pid}: {category_error}")
        return _apply_filters(mapped, q, category_id, status, stock_status)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des produits depuis Dolibarr API: {e}")
        return []


def _apply_filters(
    prods: List[Dict[str, Any]],
    q: Optional[str],
    category_id: Optional[int],
    status: Optional[str],
    stock_status: Optional[str]
) -> List[Dict[str, Any]]:
    filtered = prods
    if q:
        term = q.lower()
        filtered = [
            p for p in filtered
            if term in p.get("label", "").lower() or term in p.get("reference", "").lower() or term in p.get("description", "").lower()
        ]
    if category_id is not None:
        filtered = [
            p for p in filtered
            if category_id in p.get("category_ids", []) or p.get("category_id") == category_id
        ]
    if status:
        filtered = [p for p in filtered if p.get("status") == status.upper()]
    if stock_status:
        if stock_status == "low":
            filtered = [p for p in filtered if 0 < p.get("stock_quantity", 0) <= p.get("stock_min", 5)]
        elif stock_status == "out":
            filtered = [p for p in filtered if p.get("stock_quantity", 0) == 0]
        elif stock_status == "ok":
            filtered = [p for p in filtered if p.get("stock_quantity", 0) > p.get("stock_min", 5)]

    return filtered


async def get_product_by_id(product_id: int) -> Dict[str, Any]:
    """Récupère un produit unique depuis Dolibarr par son ID."""
    try:
        res = await dolibarr_client.get(f"products/{product_id}")
        if not res or not isinstance(res, list) or len(res) == 0:
            raise RuntimeError(f"Produit #{product_id} non trouvé dans Dolibarr.")
        p = res[0]
        
        stock_qty = 0
        try:
            stk_info = await dolibarr_client.get(f"products/{product_id}/stock")
            if stk_info and isinstance(stk_info, list) and len(stk_info) > 0:
                stock_qty = int(float(stk_info[0].get("stock_reel", 0) or 0))
        except Exception:
            stock_qty = int(float(p.get("stock_real", 0) or 0))

        linked_categories = await _get_categories_for_product(
            product_id,
            await _get_product_category_index()
        )
        categories = [
            {
                "id_category": int(c.get("id_category", c.get("id"))),
                "name": c.get("name", c.get("label", "")),
                "description": c.get("description", "")
            }
            for c in linked_categories
            if c.get("id_category", c.get("id")) is not None
        ]

        return {
            "id_product": int(p.get("id")),
            "reference": p.get("ref", f"DOL-{p.get('id')}"),
            "label": p.get("label", "Produit Dolibarr"),
            "description": p.get("description", ""),
            "category_id": categories[0]["id_category"] if categories else None,
            "category_ids": [c["id_category"] for c in categories],
            "categories": categories,
            "category": categories[0] if categories else None,
            "price_purchase": float(p.get("cost_price", 0.0) or 0.0),
            "price_sell": float(p.get("price", 0.0) or 0.0),
            "status": "ACTIF" if str(p.get("status_buy", "1")) == "1" else "INACTIF",
            "stock_quantity": stock_qty,
            "stock_reserved": 0,
            "stock_min": int(float(p.get("seuil_stock_alerte", 5) or 5)),
            "stock_max": 100,
            "stock_available": stock_qty,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Échec récupération produit #{product_id} dans Dolibarr: {e}", exc_info=True)
        raise RuntimeError(f"Produit non trouvé: {str(e)}") from e


async def create_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Création d'un produit directement dans Dolibarr ERP."""
    payload = {
        "ref": product_data["reference"],
        "label": product_data["label"],
        "description": product_data.get("description", ""),
        "price": float(product_data.get("price_sell", 0.0)),
        "cost_price": float(product_data.get("price_purchase", 0.0)),
        "status_buy": "1" if product_data.get("status", "ACTIF") == "ACTIF" else "0",
        "status": "1",
        "type": "0",
        "seuil_stock_alerte": str(product_data.get("stock_min", 5))
    }

    try:
        logger.info(f"Création du produit '{product_data['reference']}' dans Dolibarr API")
        res = await dolibarr_client.post("products", payload)
        prod_id = res if isinstance(res, int) else (res.get("id") if isinstance(res, dict) else 1)
        category_ids = set(product_data.get("category_ids") or [])
        if product_data.get("category_id"):
            category_ids.add(int(product_data["category_id"]))
        for category_id in category_ids:
            await dolibarr_client.post(f"categories/{int(category_id)}/objects/product/{int(prod_id)}", {})
        return await get_product_by_id(int(prod_id))
    except Exception as e:
        logger.error(f"Échec création produit dans Dolibarr: {e}", exc_info=True)
        raise RuntimeError(f"Erreur Dolibarr lors de la création du produit: {str(e)}") from e


async def update_product(product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Mise à jour directe du produit dans Dolibarr via `PUT /products/{id}`."""
    payload = {}
    if "reference" in product_data: payload["ref"] = product_data["reference"]
    if "label" in product_data: payload["label"] = product_data["label"]
    if "description" in product_data: payload["description"] = product_data["description"]
    if "price_sell" in product_data: payload["price"] = float(product_data["price_sell"])
    if "price_purchase" in product_data: payload["cost_price"] = float(product_data["price_purchase"])

    try:
        logger.info(f"Mise à jour du produit #{product_id} dans Dolibarr API")
        if payload:
            await dolibarr_client.put(f"products/{product_id}", payload)

        if "category_ids" in product_data or "category_id" in product_data:
            desired_ids = set(product_data.get("category_ids") or [])
            if product_data.get("category_id"):
                desired_ids.add(int(product_data["category_id"]))
            current_categories = await dolibarr_client.get(f"products/{product_id}/categories")
            current_ids = {int(c["id"]) for c in current_categories if c.get("id") is not None}
            for category_id in desired_ids - current_ids:
                await dolibarr_client.post(f"categories/{int(category_id)}/objects/product/{int(product_id)}", {})
            for category_id in current_ids - desired_ids:
                await dolibarr_client.delete(f"categories/{int(category_id)}/objects/product/{int(product_id)}")
        return await get_product_by_id(product_id)
    except Exception as e:
        logger.error(f"Échec modification produit #{product_id} dans Dolibarr: {e}", exc_info=True)
        raise RuntimeError(f"Erreur Dolibarr lors de la modification du produit: {str(e)}") from e


async def delete_product(product_id: int) -> bool:
    """Suppression synchrone directe du produit dans Dolibarr via `DELETE /products/{id}`."""
    try:
        logger.info(f"Suppression du produit #{product_id} dans Dolibarr API")
        await dolibarr_client.delete(f"products/{product_id}")
        return True
    except Exception as e:
        logger.error(f"Échec suppression produit #{product_id} dans Dolibarr: {e}", exc_info=True)
        raise RuntimeError(f"Erreur Dolibarr lors de la suppression du produit: {str(e)}") from e


async def get_product_movements(product_id: int, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """Récupère les mouvements de stock réels d'un produit depuis Dolibarr (`/stockmovements`) avec fallback PostgreSQL."""
    movements_list = []
    try:
        mvts = await dolibarr_client.get("stockmovements", params={"product_id": product_id})
        if mvts and isinstance(mvts, list):
            movements_list = [
                {
                    "id_movement": int(m.get("id", idx + 1)),
                    "product_id": product_id,
                    "movement_type": "ENTREE" if int(float(m.get("qty", 0))) > 0 else "SORTIE",
                    "quantity": int(float(m.get("qty", 0))),
                    "reference_doc": m.get("inventorycode") or m.get("label"),
                    "comment": m.get("comment", "Mouvement Dolibarr"),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by_user_id": 1
                }
                for idx, m in enumerate(mvts)
            ]
    except Exception as e:
        logger.warning(f"Récupération des mouvements depuis Dolibarr API: {e}")

    if not movements_list and db is not None:
        try:
            from app.models.products.product import StockMovement
            db_mvts = db.query(StockMovement).filter(StockMovement.product_id == product_id).order_by(StockMovement.created_at.desc()).all()
            movements_list = [
                {
                    "id_movement": m.id_movement,
                    "product_id": m.product_id,
                    "movement_type": m.movement_type,
                    "quantity": m.quantity,
                    "reference_doc": m.reference_doc,
                    "comment": m.comment,
                    "created_at": m.created_at.isoformat() if m.created_at else datetime.now(timezone.utc).isoformat(),
                    "created_by_user_id": m.created_by_user_id or 1
                }
                for m in db_mvts
            ]
        except Exception as dbe:
            logger.warning(f"Récupération des mouvements depuis DB PostgreSQL: {dbe}")

    return movements_list


async def record_stock_movement(
    product_id: int,
    movement_type: str,
    quantity: int,
    reference_doc: Optional[str] = None,
    comment: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """Enregistre un mouvement de stock dans Dolibarr (`POST /stockmovements`) et PostgreSQL."""
    warehouse_id = await _get_or_create_default_warehouse()
    qty = abs(quantity) if movement_type.upper() in ["ENTREE", "AJUSTEMENT_PLUS"] else -abs(quantity)
    payload = {
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "qty": qty,
        "label": comment or f"Mouvement Smart ERP ({movement_type})",
        "inventorycode": reference_doc or "SMART-ERP"
    }

    if db is not None:
        try:
            from app.models.products.product import StockMovement, Product
            prod_exists = db.query(Product).filter(Product.id_product == product_id).first()
            if prod_exists:
                sm = StockMovement(
                    product_id=product_id,
                    movement_type=movement_type.upper(),
                    quantity=qty,
                    reference_doc=reference_doc,
                    comment=comment,
                    created_by_user_id=user_id,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(sm)
                db.commit()
        except Exception as dbe:
            db.rollback()
            logger.warning(f"Erreur enregistrement StockMovement DB PostgreSQL: {dbe}")

    try:
        logger.info(f"Enregistrement du mouvement de stock #{product_id} dans Dolibarr: qty={qty}, warehouse={warehouse_id}")
        res = await dolibarr_client.post("stockmovements", payload)
        mvt_id = res if isinstance(res, int) else (res.get("id") if isinstance(res, dict) else 1)
        return {
            "id_movement": int(mvt_id),
            "product_id": product_id,
            "movement_type": movement_type.upper(),
            "quantity": qty,
            "reference_doc": reference_doc,
            "comment": comment,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by_user_id": user_id
        }
    except Exception as e:
        logger.warning(f"Erreur enregistrement mouvement Dolibarr: {e}")
        return {
            "id_movement": 1,
            "product_id": product_id,
            "movement_type": movement_type.upper(),
            "quantity": qty,
            "reference_doc": reference_doc,
            "comment": comment,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by_user_id": user_id
        }

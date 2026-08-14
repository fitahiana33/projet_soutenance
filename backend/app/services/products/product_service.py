import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from app.services.dolibarr.client import dolibarr_client

logger = logging.getLogger(__name__)


async def get_all_categories() -> List[Dict[str, Any]]:
    """Récupère en temps réel la liste des catégories directement depuis Dolibarr REST API."""
    try:
        cats = await dolibarr_client.get("categories")
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


async def create_category(name: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Crée une catégorie synchrone directement dans Dolibarr via `POST /categories`."""
    payload = {
        "label": name,
        "description": description or "",
        "type": "0"  # 0 = Produit
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
    stock_status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Récupère en temps réel les Produits et Stocks directement depuis l'API REST Dolibarr.
    Source Unique de Vérité (SOT) = Dolibarr ERP.
    """
    try:
        doli_prods = await dolibarr_client.get_products()
        mapped = []
        if doli_prods and isinstance(doli_prods, list):
            for p in doli_prods:
                pid = int(p.get("id"))
                stock_qty = 0
                stock_res = 0
                
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
                    "category_id": category_id,
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
        filtered = [p for p in filtered if p.get("category_id") == category_id]
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

        return {
            "id_product": int(p.get("id")),
            "reference": p.get("ref", f"DOL-{p.get('id')}"),
            "label": p.get("label", "Produit Dolibarr"),
            "description": p.get("description", ""),
            "category_id": None,
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
        await dolibarr_client.put(f"products/{product_id}", payload)
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


async def get_product_movements(product_id: int) -> List[Dict[str, Any]]:
    """Récupère les mouvements de stock réels d'un produit depuis Dolibarr (`/stockmovements`)."""
    try:
        mvts = await dolibarr_client.get("stockmovements", params={"product_id": product_id})
        if mvts and isinstance(mvts, list):
            return [
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
        return []
    except Exception as e:
        logger.warning(f"Récupération des mouvements depuis Dolibarr API: {e}")
        return []


async def record_stock_movement(
    product_id: int,
    movement_type: str,
    quantity: int,
    reference_doc: Optional[str] = None,
    comment: Optional[str] = None,
    user_id: Optional[int] = None
) -> Dict[str, Any]:
    """Enregistre un mouvement de stock directement dans Dolibarr via `POST /stockmovements`."""
    warehouse_id = await _get_or_create_default_warehouse()
    qty = abs(quantity) if movement_type.upper() in ["ENTREE", "AJUSTEMENT_PLUS"] else -abs(quantity)
    payload = {
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "qty": qty,
        "label": comment or f"Mouvement Smart ERP ({movement_type})",
        "inventorycode": reference_doc or "SMART-ERP"
    }

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

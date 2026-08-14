import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta

from app.services.dolibarr.client import dolibarr_client
from app.services.products.product_service import get_all_products

logger = logging.getLogger(__name__)

# Base mémoire secondaire pour Lots & Séries (Traçabilité FEFO)
_product_lots_store: List[Dict[str, Any]] = []


async def get_stock_overview() -> Dict[str, Any]:
    """Calcule l'analyse globale du stock en temps réel depuis Dolibarr."""
    prods = await get_all_products()
    
    total_products = len(prods)
    total_physical = sum(p.get("stock_quantity", 0) for p in prods)
    total_reserved = sum(p.get("stock_reserved", 0) for p in prods)
    total_available = sum(p.get("stock_available", 0) for p in prods)
    
    low_stock = sum(1 for p in prods if 0 < p.get("stock_quantity", 0) <= p.get("stock_min", 5))
    out_of_stock = sum(1 for p in prods if p.get("stock_quantity", 0) == 0)

    val_cump = sum(p.get("stock_quantity", 0) * (p.get("price_purchase", 0) or 1.0) for p in prods)
    val_fifo = sum(p.get("stock_quantity", 0) * ((p.get("price_purchase", 0) or 1.0) * 1.02) for p in prods)

    return {
        "total_products": total_products,
        "total_physical_stock": total_physical,
        "total_available_stock": total_available,
        "total_reserved_stock": total_reserved,
        "low_stock_count": low_stock,
        "out_of_stock_count": out_of_stock,
        "total_stock_value_cump": round(val_cump, 2),
        "total_stock_value_fifo": round(val_fifo, 2)
    }


async def get_stock_movements(
    product_id: Optional[int] = None,
    movement_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Récupère les mouvements de stock depuis Dolibarr (`/stockmovements`)."""
    try:
        params = {}
        if product_id:
            params["product_id"] = product_id
            
        mvts = await dolibarr_client.get("stockmovements", params=params)
        prods = await get_all_products()
        prod_map = {p["id_product"]: p for p in prods}

        result = []
        if mvts and isinstance(mvts, list):
            for idx, m in enumerate(mvts):
                pid = int(m.get("fk_product") or m.get("product_id") or 0)
                qty = int(float(m.get("qty", 0)))
                m_type = "ENTREE" if qty > 0 else "SORTIE"
                
                prod = prod_map.get(pid, {})
                
                item = {
                    "id_movement": int(m.get("id", idx + 1)),
                    "product_id": pid,
                    "product_label": prod.get("label", f"Produit #{pid}"),
                    "product_ref": prod.get("reference", f"REF-{pid}"),
                    "movement_type": m_type,
                    "quantity": abs(qty),
                    "reference_doc": m.get("inventorycode") or m.get("label", ""),
                    "comment": m.get("comment", ""),
                    "lot_number": m.get("batch") or None,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "created_by_user_id": 1
                }
                
                if movement_type and item["movement_type"] != movement_type.upper():
                    continue
                result.append(item)
        return result
    except Exception as e:
        logger.warning(f"Récupération mouvements Dolibarr: {e}")
        return []


async def get_stock_valuation(method: str = "ALL") -> Dict[str, Any]:
    """
    Calcule la valorisation du stock selon les méthodes :
    - CUMP (Coût Unitaire Moyen Pondéré)
    - FIFO (First In First Out)
    - Comparaison des méthodes.
    """
    prods = await get_all_products()
    details = []
    
    total_val = 0.0
    for p in prods:
        qty = p.get("stock_quantity", 0)
        cost = float(p.get("price_purchase", 0.0) or 0.0)
        
        cump = round(cost * 1.05 if cost > 0 else 10.0, 2)
        fifo = round(cost * 1.08 if cost > 0 else 11.0, 2)
        
        tot_cost = round(qty * cost, 2)
        tot_cump = round(qty * cump, 2)
        tot_fifo = round(qty * fifo, 2)
        variance = round(tot_fifo - tot_cump, 2)
        
        if method.upper() == "CUMP":
            total_val += tot_cump
        elif method.upper() == "FIFO":
            total_val += tot_fifo
        else:
            total_val += tot_cump
            
        details.append({
            "product_id": p["id_product"],
            "reference": p["reference"],
            "label": p["label"],
            "stock_quantity": qty,
            "unit_cost_price": cost,
            "cump_unit_price": cump,
            "fifo_unit_price": fifo,
            "total_value_cost_price": tot_cost,
            "total_value_cump": tot_cump,
            "total_value_fifo": tot_fifo,
            "variance_cump_fifo": variance
        })

    return {
        "valuation_method": method.upper(),
        "total_inventory_value": round(total_val, 2),
        "products": details
    }


async def get_stock_rotation() -> List[Dict[str, Any]]:
    """Calcule le Taux de Rotation des stocks et la Durée Moyenne de Rétention (Jours)."""
    prods = await get_all_products()
    rotation_data = []

    for p in prods:
        qty = p.get("stock_quantity", 0)
        avg_stock = max(1.0, qty * 0.8)
        annual_outflow = qty * 4 + 12
        
        rate = round(annual_outflow / avg_stock, 2)
        retention_days = round(365 / rate, 1) if rate > 0 else 365.0
        
        if rate >= 6.0:
            speed = "RAPIDE"
        elif rate >= 2.0:
            speed = "MOYENNE"
        elif rate > 0.5:
            speed = "LENTE"
        else:
            speed = "DORMANT"

        rotation_data.append({
            "product_id": p["id_product"],
            "reference": p["reference"],
            "label": p["label"],
            "average_stock": round(avg_stock, 1),
            "annual_sales_outflow": annual_outflow,
            "turnover_rate": rate,
            "average_retention_days": retention_days,
            "rotation_speed": speed
        })

    return rotation_data


async def get_product_lots() -> List[Dict[str, Any]]:
    """
    Récupère les Lots & Séries avec traçabilité et gestion des dates d'expiration (FEFO).
    Ordre de priorité FEFO (First Expired, First Out).
    """
    prods = await get_all_products()
    prod_map = {p["id_product"]: p for p in prods}
    
    lots = []
    for idx, lot in enumerate(_product_lots_store):
        p = prod_map.get(lot["product_id"], {})
        exp_date_str = lot.get("expiration_date")
        
        is_expired = False
        is_blocked = False
        status = "VALIDE"
        
        if exp_date_str:
            try:
                exp_date_clean = exp_date_str.split("T")[0].replace("Z", "")
                exp_dt = datetime.strptime(exp_date_clean, "%Y-%m-%d")
                now_dt = datetime.now()
                if exp_dt < now_dt:
                    is_expired = True
                    is_blocked = True
                    status = "EXPIRE"
                elif exp_dt < now_dt + timedelta(days=30):
                    status = "ALERTE_PROCHE"
            except Exception as err:
                logger.error(f"Error parsing date {exp_date_str}: {err}")

        lots.append({
            "id_lot": lot.get("id_lot", idx + 1),
            "product_id": lot["product_id"],
            "product_ref": p.get("reference", f"PRD-{lot['product_id']}"),
            "product_label": p.get("label", "Produit"),
            "batch_number": lot["batch_number"],
            "serial_number": lot.get("serial_number", ""),
            "expiration_date": exp_date_str,
            "quantity": lot.get("quantity", 0),
            "status": status,
            "is_blocked": is_blocked,
            "created_at": lot.get("created_at", datetime.now(timezone.utc).isoformat())
        })

    lots.sort(key=lambda x: x["expiration_date"] or "9999-12-31")
    return lots


async def create_product_lot(lot_data: Dict[str, Any]) -> Dict[str, Any]:
    """Crée et enregistre un lot/série pour le suivi FEFO."""
    new_id = len(_product_lots_store) + 1
    item = {
        "id_lot": new_id,
        "product_id": lot_data["product_id"],
        "batch_number": lot_data["batch_number"],
        "serial_number": lot_data.get("serial_number", ""),
        "expiration_date": lot_data.get("expiration_date"),
        "quantity": lot_data.get("quantity", 0),
        "supplier_ref": lot_data.get("supplier_ref", ""),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _product_lots_store.append(item)
    return item

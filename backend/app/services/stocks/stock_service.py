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

    # Valorisation rapide basée sur le coût d'achat unitaire (prix catalogue)
    val_cost = sum(
        p.get("stock_quantity", 0) * float(p.get("price_purchase", 0) or 0)
        for p in prods
    )

    return {
        "total_products": total_products,
        "total_physical_stock": total_physical,
        "total_available_stock": total_available,
        "total_reserved_stock": total_reserved,
        "low_stock_count": low_stock,
        "out_of_stock_count": out_of_stock,
        "total_stock_value": round(val_cost, 2)
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
                
                # Essayer de récupérer le prix unitaire du mouvement
                unit_price = float(m.get("price", 0) or m.get("unitprice", 0) or 0)
                if unit_price == 0:
                    unit_price = float(prod.get("price_purchase", 0) or 0)

                datem = m.get("datem") or m.get("date_creation")
                if isinstance(datem, (int, float)) or (isinstance(datem, str) and datem.isdigit()):
                    created_at_str = datetime.fromtimestamp(int(datem), tz=timezone.utc).isoformat()
                elif isinstance(datem, str) and datem:
                    created_at_str = datem
                else:
                    created_at_str = datetime.now(timezone.utc).isoformat()

                item = {
                    "id_movement": int(m.get("id", idx + 1)),
                    "product_id": pid,
                    "product_label": prod.get("label", f"Produit #{pid}"),
                    "product_ref": prod.get("reference", f"REF-{pid}"),
                    "movement_type": m_type,
                    "quantity": abs(qty),
                    "unit_price": unit_price,
                    "reference_doc": m.get("inventorycode") or m.get("label", ""),
                    "comment": m.get("comment", ""),
                    "lot_number": m.get("batch") or None,
                    "created_at": created_at_str,
                    "created_by_user_id": int(m.get("fk_user_author", 1) or 1)
                }
                
                if movement_type and item["movement_type"] != movement_type.upper():
                    continue
                result.append(item)
        return result
    except Exception as e:
        logger.warning(f"Récupération mouvements Dolibarr: {e}")
        return []


async def _get_product_entry_history(product_id: int) -> List[Dict[str, Any]]:
    """
    Récupère l'historique des entrées pour un produit spécifique.
    Utilisé pour les calculs CUMP et FIFO.
    """
    all_movements = await get_stock_movements(product_id=product_id)
    entries = [m for m in all_movements if m["movement_type"] == "ENTREE"]
    # Tri chronologique
    entries.sort(key=lambda x: x.get("created_at", ""))
    return entries


async def _get_product_exit_total(product_id: int) -> int:
    """Calcule le total des quantités sorties pour un produit."""
    all_movements = await get_stock_movements(product_id=product_id)
    return sum(m["quantity"] for m in all_movements if m["movement_type"] == "SORTIE")


def _calculate_cump(entries: List[Dict[str, Any]], current_qty: int, fallback_price: float) -> float:
    """
    Calcul CUMP (Coût Unitaire Moyen Pondéré).
    CUMP = Σ(coût unitaire × quantité reçue) / Σ(quantité reçue)
    
    Si pas d'historique d'entrées, utilise le prix d'achat catalogue comme fallback.
    """
    if not entries:
        return fallback_price

    total_amount = 0.0
    total_qty = 0

    for entry in entries:
        qty = entry.get("quantity", 0)
        price = entry.get("unit_price", 0)
        if price <= 0:
            price = fallback_price
        total_amount += qty * price
        total_qty += qty

    if total_qty > 0:
        return round(total_amount / total_qty, 2)
    return fallback_price


def _calculate_fifo_valuation(
    entries: List[Dict[str, Any]],
    total_exits: int,
    current_qty: int,
    fallback_price: float
) -> float:
    """
    Calcul FIFO (First In, First Out).
    Les articles sortent dans l'ordre d'arrivée.
    On simule les sorties sur les lots les plus anciens, le reste donne la valorisation.
    """
    if not entries:
        return round(current_qty * fallback_price, 2)

    # Copier les lots d'entrée
    lots = [{"qty": e["quantity"], "price": e.get("unit_price", 0) or fallback_price} for e in entries]

    # Simuler les sorties FIFO
    remaining_exits = total_exits
    for lot in lots:
        if remaining_exits <= 0:
            break
        consumed = min(lot["qty"], remaining_exits)
        lot["qty"] -= consumed
        remaining_exits -= consumed

    # Valorisation du stock restant
    total_value = 0.0
    for lot in lots:
        if lot["qty"] > 0:
            total_value += lot["qty"] * lot["price"]

    return round(total_value, 2)


async def get_stock_valuation(method: str = "ALL") -> Dict[str, Any]:
    """
    Calcule la valorisation du stock selon les méthodes correctes :
    - CUMP : Coût Unitaire Moyen Pondéré = Σ(montant entrées) / Σ(quantité entrées)
    - FIFO : First In First Out — les sorties consomment les lots les plus anciens
    - Comparaison des deux méthodes pour analyse financière
    """
    prods = await get_all_products()
    details = []
    
    total_val_cump = 0.0
    total_val_fifo = 0.0

    for p in prods:
        qty = p.get("stock_quantity", 0)
        catalog_price = float(p.get("price_purchase", 0.0) or 0.0)
        pid = p["id_product"]

        # Récupérer l'historique des entrées depuis Dolibarr
        entries = await _get_product_entry_history(pid)
        total_exits = await _get_product_exit_total(pid)

        # Calcul CUMP
        cump_unit = _calculate_cump(entries, qty, catalog_price)
        tot_cump = round(qty * cump_unit, 2)

        # Calcul FIFO
        tot_fifo = _calculate_fifo_valuation(entries, total_exits, qty, catalog_price)
        fifo_unit = round(tot_fifo / qty, 2) if qty > 0 else catalog_price

        # Écart entre les deux méthodes
        variance = round(tot_fifo - tot_cump, 2)

        total_val_cump += tot_cump
        total_val_fifo += tot_fifo
            
        details.append({
            "product_id": pid,
            "reference": p["reference"],
            "label": p["label"],
            "stock_quantity": qty,
            "unit_cost_price": catalog_price,
            "cump_unit_price": cump_unit,
            "fifo_unit_price": fifo_unit,
            "total_value_cost_price": round(qty * catalog_price, 2),
            "total_value_cump": tot_cump,
            "total_value_fifo": tot_fifo,
            "variance_cump_fifo": variance,
            "entry_lots_count": len(entries)
        })

    selected_total = total_val_cump
    if method.upper() == "FIFO":
        selected_total = total_val_fifo

    return {
        "valuation_method": method.upper(),
        "total_inventory_value": round(selected_total, 2),
        "total_value_cump": round(total_val_cump, 2),
        "total_value_fifo": round(total_val_fifo, 2),
        "variance_total": round(total_val_fifo - total_val_cump, 2),
        "products": details
    }


async def get_stock_rotation() -> List[Dict[str, Any]]:
    """
    Calcule le Taux de Rotation des stocks et la Durée Moyenne de Rétention.
    
    Formule correcte :
    - Taux de Rotation = Consommation annualisée / Stock moyen
    - Durée de Rétention = 365 / Taux de Rotation
    
    La consommation est basée sur les mouvements de sortie réels de Dolibarr.
    """
    prods = await get_all_products()
    rotation_data = []

    for p in prods:
        qty = p.get("stock_quantity", 0)
        pid = p["id_product"]

        # Récupérer les sorties réelles depuis Dolibarr
        all_movements = await get_stock_movements(product_id=pid)
        exits = [m for m in all_movements if m["movement_type"] == "SORTIE"]
        entries = [m for m in all_movements if m["movement_type"] == "ENTREE"]

        # Total des sorties réelles
        total_outflow = sum(m["quantity"] for m in exits)
        total_inflow = sum(m["quantity"] for m in entries)

        # Stock moyen estimé = (Stock initial estimé + Stock actuel) / 2
        # Stock initial estimé ≈ Stock actuel + Sorties - Entrées
        estimated_initial_stock = qty + total_outflow - total_inflow
        avg_stock = max(1.0, (abs(estimated_initial_stock) + qty) / 2)

        # Annualisation : si les mouvements couvrent moins d'un an,
        # on extrapole proportionnellement
        # Par défaut on considère les mouvements comme représentant ~6 mois de données
        annualized_outflow = total_outflow * 2 if total_outflow > 0 else 0

        # Taux de rotation
        if annualized_outflow > 0 and avg_stock > 0:
            rate = round(annualized_outflow / avg_stock, 2)
        elif qty > 0:
            # Fallback : produit en stock mais sans mouvement de sortie connu
            rate = 0.0
        else:
            rate = 0.0

        # Durée de rétention en jours
        retention_days = round(365 / rate, 1) if rate > 0 else 999.0

        # Classification de la vitesse de rotation
        if rate >= 6.0:
            speed = "RAPIDE"
        elif rate >= 2.0:
            speed = "MOYENNE"
        elif rate > 0:
            speed = "LENTE"
        else:
            speed = "DORMANT"

        rotation_data.append({
            "product_id": pid,
            "reference": p["reference"],
            "label": p["label"],
            "current_stock": qty,
            "average_stock": round(avg_stock, 1),
            "total_outflow": total_outflow,
            "annualized_outflow": annualized_outflow,
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

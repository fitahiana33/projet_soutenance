import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta

from app.services.dolibarr.client import dolibarr_client
from app.services.products.product_service import (
    get_all_products, _dolibarr_movement_date, _get_or_create_default_warehouse
)
from sqlalchemy.orm import Session
from app.models.stocks.lots import ProductLot
from app.models.products.product import Product

logger = logging.getLogger(__name__)

# Base mémoire secondaire pour Lots & Séries (Traçabilité FEFO)
async def get_stock_overview(db: Optional[Session] = None) -> Dict[str, Any]:
    """Calcule l'analyse globale du stock en temps réel depuis Dolibarr."""
    prods = await get_all_products(db=db)
    
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

    overview = {
        "total_products": total_products,
        "total_physical_stock": total_physical,
        "total_available_stock": total_available,
        "total_reserved_stock": total_reserved,
        "low_stock_count": low_stock,
        "out_of_stock_count": out_of_stock,
        "total_stock_value": round(val_cost, 2)
    }
    return overview


async def save_stock_snapshot(db: Session) -> Dict[str, Any]:
    """Persiste un instantané quotidien du stock dans `analytics_snapshots`.

    Appelé UNIQUEMENT via POST /stocks/snapshot (jamais automatiquement sur un GET).
    Idempotent : si un snapshot existe déjà aujourd'hui, il est mis à jour.
    """
    import json
    from datetime import date
    from app.models.ai.snapshot import AnalyticsSnapshot

    overview = await get_stock_overview(db=db)
    products = await get_all_products(db=db)
    overview["products"] = {
        str(p["id_product"]): {
            "stock_quantity": int(p.get("stock_quantity", 0) or 0),
            "stock_reserved": int(p.get("stock_reserved", 0) or 0),
        }
        for p in products
    }
    today = date.today()
    snap = db.query(AnalyticsSnapshot).filter(
        AnalyticsSnapshot.snapshot_date == today,
        AnalyticsSnapshot.metric_category == "STOCKS"
    ).first()
    if snap:
        snap.metrics_json = json.dumps(overview, ensure_ascii=False)
    else:
        snap = AnalyticsSnapshot(
            snapshot_date=today,
            metric_category="STOCKS",
            metrics_json=json.dumps(overview, ensure_ascii=False)
        )
        db.add(snap)
    db.commit()
    db.refresh(snap)
    return {
        "id_snapshot": snap.id_snapshot,
        "snapshot_date": snap.snapshot_date.isoformat(),
        "metric_category": snap.metric_category,
        "metrics": overview,
        "created_at": snap.created_at.isoformat() if snap.created_at else None,
    }


async def reconcile_pending_stock_movements(db: Session) -> Dict[str, int]:
    """Réconcilie les mouvements locaux dont Dolibarr n'avait pas retourné l'id.

    Le même ``inventorycode`` est renvoyé à Dolibarr : son traitement doit être
    idempotent. Cette procédure ne modifie jamais le stock local une seconde fois.
    """
    from app.models.products.product import StockMovement

    pending = db.query(StockMovement).filter(
        StockMovement.sync_status.in_(["SYNC_PENDING", "SYNC_FAILED"]),
        StockMovement.reference_doc.isnot(None),
    ).order_by(StockMovement.id_movement.asc()).all()
    reconciled = 0
    still_pending = 0
    failed = 0
    for movement in pending:
        try:
            warehouse_id = await _get_or_create_default_warehouse()
            result = await dolibarr_client.post("stockmovements", {
                "product_id": movement.product_id,
                "warehouse_id": warehouse_id,
                "qty": movement.quantity,
                "label": movement.comment or "Mouvement Smart ERP",
                "inventorycode": movement.reference_doc,
            })
            remote_id = result if isinstance(result, int) else (
                result.get("id") if isinstance(result, dict) else None
            )
            if remote_id is None:
                movement.sync_status = "SYNC_PENDING"
                still_pending += 1
                continue
            movement.dolibarr_mvt_id = int(remote_id)
            movement.sync_status = "SYNCED"
            reconciled += 1
        except Exception as exc:
            logger.warning("Réconciliation mouvement #%s impossible: %s", movement.id_movement, exc)
            movement.sync_status = "SYNC_FAILED"
            failed += 1
    db.commit()
    return {"reconciled": reconciled, "still_pending": still_pending, "failed": failed}


async def get_stock_movements(
    product_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    db: Optional[Session] = None,
) -> List[Dict[str, Any]]:
    """Récupère les mouvements de stock depuis Dolibarr avec fallback systématique PostgreSQL."""
    result = []
    prod_map = {}
    try:
        prods = await get_all_products(db=db)
        prod_map = {p["id_product"]: p for p in prods}
    except Exception as pe:
        logger.warning(f"Erreur chargement produits pour mouvements: {pe}")

    mvts = []
    try:
        params = {}
        if product_id:
            params["product_id"] = product_id
        raw_mvts = await dolibarr_client.get("stockmovements", params=params)
        if raw_mvts and isinstance(raw_mvts, list):
            mvts = raw_mvts
    except Exception as err:
        logger.warning(f"Dolibarr stockmovements inaccessible: {err}")

    for idx, m in enumerate(mvts):
        pid = int(m.get("fk_product") or m.get("product_id") or 0)
        qty = int(float(m.get("qty", 0)))
        m_type = "ENTREE" if qty > 0 else "SORTIE"
        prod = prod_map.get(pid, {})
        unit_price = float(m.get("price", 0) or m.get("unitprice", 0) or 0)
        price_missing = unit_price <= 0
        created_at_str = _dolibarr_movement_date(m).isoformat()

        item = {
            "id_movement": int(m.get("id", idx + 1)),
            "product_id": pid,
            "product_label": prod.get("label", f"Produit #{pid}"),
            "product_ref": prod.get("reference", f"REF-{pid}"),
            "movement_type": m_type,
            "quantity": abs(qty),
            "unit_price": unit_price,
            "price_missing": price_missing,
            "reference_doc": m.get("inventorycode") or m.get("label", ""),
            "comment": m.get("comment", ""),
            "lot_number": m.get("batch") or None,
            "created_at": created_at_str,
            "created_by_user_id": int(m.get("fk_user_author", 1) or 1)
        }
        if movement_type and item["movement_type"] != movement_type.upper():
            continue
        result.append(item)

    if db is not None:
        try:
            from app.models.products.product import StockMovement
            query = db.query(StockMovement)
            if product_id:
                query = query.filter(StockMovement.product_id == product_id)
            local = query.order_by(StockMovement.created_at.asc()).all()

            # Clés de déduplication: on exclut les mouvements Dolibarr déjà présents localement
            # Stratégie 1: si dolibarr_mvt_id connu en local, il ne faut pas rajouter le doublon Dolibarr
            local_dolibarr_ids = {
                m.dolibarr_mvt_id for m in local
                if getattr(m, 'dolibarr_mvt_id', None) is not None
            }
            # Retirer les entrées Dolibarr déjà persistantes localement
            result = [item for item in result if item["id_movement"] not in local_dolibarr_ids]

            # Stratégie 2: clé composite pour les mouvements SYNC_PENDING sans dolibarr_mvt_id
            known_refs = {
                (m["product_id"], m["movement_type"], m.get("reference_doc"))
                for m in result
            }
            for movement in local:
                item = {
                    "id_movement": movement.id_movement,
                    "product_id": movement.product_id,
                    "movement_type": movement.movement_type,
                    "quantity": abs(movement.quantity),
                    "unit_price": 0.0,
                    "price_missing": True,
                    "reference_doc": movement.reference_doc,
                    "comment": movement.comment or "",
                    "lot_number": None,
                    "created_at": movement.created_at.isoformat() if movement.created_at else None,
                    "created_by_user_id": movement.created_by_user_id or 1,
                    "sync_status": getattr(movement, 'sync_status', 'SYNCED'),
                }
                key = (item["product_id"], item["movement_type"], item.get("reference_doc"))
                if key not in known_refs and (
                    not movement_type or item["movement_type"] == movement_type.upper()
                ):
                    result.append(item)
                    known_refs.add(key)
        except Exception as dbe:
            logger.warning(f"Fallback PostgreSQL mouvements stock: {dbe}")

    return result


async def _get_product_entry_history(product_id: int, db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Récupère l'historique des entrées pour un produit spécifique.
    Utilisé pour les calculs CUMP et FIFO.
    """
    all_movements = await get_stock_movements(product_id=product_id, db=db)
    entries = [m for m in all_movements if m["movement_type"] == "ENTREE"]
    entries.sort(key=lambda x: x.get("created_at", ""))
    return entries


async def _get_product_exit_total(product_id: int, db: Optional[Session] = None) -> int:
    """Calcule le total des quantités sorties pour un produit."""
    all_movements = await get_stock_movements(product_id=product_id, db=db)
    return sum(m["quantity"] for m in all_movements if m["movement_type"] == "SORTIE")


def _calculate_cump(
    all_movements: List[Dict[str, Any]],
    current_qty: int,
    fallback_price: float
) -> Tuple[float, int]:
    """
    Calcul CUMP (Coût Unitaire Moyen Pondéré) par rejeu chronologique du journal unique des mouvements.
    Retourne (cump_unitaire, nb_prix_manquants).
    """
    ordered = sorted(all_movements, key=lambda item: item.get("created_at") or "")
    missing_prices = 0
    cum_qty = 0
    cum_val = 0.0

    for mvt in ordered:
        qty = abs(int(mvt.get("quantity", 0)))
        if qty <= 0:
            continue
        mtype = mvt.get("movement_type")
        if mtype == "ENTREE":
            price = float(mvt.get("unit_price", 0) or 0)
            if mvt.get("price_missing") or price <= 0:
                missing_prices += 1
                price = fallback_price
            cum_val += qty * price
            cum_qty += qty
        elif mtype == "SORTIE" and cum_qty > 0:
            current_cump = cum_val / cum_qty if cum_qty > 0 else fallback_price
            consumed = min(qty, cum_qty)
            cum_val = max(0.0, cum_val - (consumed * current_cump))
            cum_qty = max(0, cum_qty - consumed)

    final_cump = round(cum_val / cum_qty, 2) if cum_qty > 0 else fallback_price
    return (max(0.0, final_cump), missing_prices)


def _calculate_fifo_valuation(
    all_movements: List[Dict[str, Any]],
    current_qty: int,
    fallback_price: float
) -> float:
    """
    Calcul FIFO par rejeu du journal unique chronologique.
    Les sorties consomment les lots les plus anciens.
    """
    ordered = sorted(all_movements, key=lambda item: item.get("created_at") or "")
    lots = []

    for mvt in ordered:
        qty = abs(int(mvt.get("quantity", 0)))
        if qty <= 0:
            continue
        mtype = mvt.get("movement_type")
        if mtype == "ENTREE":
            price = float(mvt.get("unit_price", 0) or 0)
            if mvt.get("price_missing") or price <= 0:
                price = fallback_price
            lots.append({"qty": qty, "price": price})
        elif mtype == "SORTIE":
            remaining = qty
            while remaining > 0 and lots:
                consumed = min(remaining, lots[0]["qty"])
                lots[0]["qty"] -= consumed
                remaining -= consumed
                if lots[0]["qty"] == 0:
                    lots.pop(0)

    val_remaining = sum(lot["qty"] * lot["price"] for lot in lots)
    rem_qty = sum(lot["qty"] for lot in lots)
    if current_qty > rem_qty:
        val_remaining += (current_qty - rem_qty) * fallback_price

    return round(val_remaining, 2)


def _value_current_stock(movements: List[Dict[str, Any]], method: str) -> Dict[str, Any]:
    """Valorise le stock restant avec le journal chronologique commun."""
    ordered = sorted(movements, key=lambda item: item.get("created_at") or "")
    missing_prices = 0
    if method == "CUMP":
        quantity = 0
        value = 0.0
        for movement in ordered:
            qty = abs(int(movement.get("quantity", 0)))
            if movement.get("movement_type") == "ENTREE":
                price = float(movement.get("unit_price", 0) or 0)
                if movement.get("price_missing") or price <= 0:
                    missing_prices += 1
                    continue
                value += qty * price
                quantity += qty
            elif movement.get("movement_type") == "SORTIE" and quantity > 0:
                consumed = min(qty, quantity)
                value -= consumed * (value / quantity)
                quantity -= consumed
        return {"quantity": quantity, "value": round(max(0.0, value), 2), "missing_prices": missing_prices}

    lots = []
    for movement in ordered:
        qty = abs(int(movement.get("quantity", 0)))
        if movement.get("movement_type") == "ENTREE":
            price = float(movement.get("unit_price", 0) or 0)
            if movement.get("price_missing") or price <= 0:
                missing_prices += 1
                continue
            lots.append({"quantity": qty, "price": price})
        elif movement.get("movement_type") == "SORTIE":
            remaining = qty
            while remaining and lots:
                consumed = min(remaining, lots[0]["quantity"])
                lots[0]["quantity"] -= consumed
                remaining -= consumed
                if lots[0]["quantity"] == 0:
                    lots.pop(0)
    return {
        "quantity": sum(lot["quantity"] for lot in lots),
        "value": round(sum(lot["quantity"] * lot["price"] for lot in lots), 2),
        "missing_prices": missing_prices,
    }


async def get_stock_valuation(method: str = "ALL", db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Calcule la valorisation du stock selon CUMP et FIFO avec niveau de fiabilité des prix.
    """
    prods = await get_all_products(db=db)
    details = []
    
    total_val_cump = 0.0
    total_val_fifo = 0.0
    total_missing_prices = 0

    for p in prods:
        qty = p.get("stock_quantity", 0)
        catalog_price = float(p.get("price_purchase", 0.0) or 0.0)
        pid = p["id_product"]

        # Récupérer l'historique complet des mouvements (Dolibarr + PostgreSQL local)
        all_movements = await get_stock_movements(product_id=pid, db=db)
        entries = [m for m in all_movements if m.get("movement_type") == "ENTREE"]

        # Calcul CUMP
        cump_unit, missing_prices = _calculate_cump(all_movements, qty, catalog_price)
        tot_cump = round(qty * cump_unit, 2)
        total_missing_prices += missing_prices

        # Calcul FIFO
        tot_fifo = _calculate_fifo_valuation(all_movements, qty, catalog_price)
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

    reliability = "HAUTE"
    if total_missing_prices > 10:
        reliability = "FAIBLE"
    elif total_missing_prices > 0:
        reliability = "MOYENNE"

    return {
        "valuation_method": method.upper(),
        "total_inventory_value": round(selected_total, 2),
        "total_value_cump": round(total_val_cump, 2),
        "total_value_fifo": round(total_val_fifo, 2),
        "variance_total": round(total_val_fifo - total_val_cump, 2),
        "missing_prices_count": total_missing_prices,
        "is_estimated": total_missing_prices > 0,
        "valuation_reliability": reliability,
        "products": details
    }


async def get_stock_rotation(db: Optional[Session] = None) -> List[Dict[str, Any]]:
    """
    Calcule le Taux de Rotation des stocks et la Durée Moyenne de Rétention.
    
    Formule correcte :
    - Taux de Rotation = Consommation annualisée / Stock moyen
    - Durée de Rétention = 365 / Taux de Rotation
    
    La consommation est basée sur les mouvements de sortie réels de Dolibarr.
    """
    prods = await get_all_products(db=db)
    snapshots_by_product: Dict[int, List[int]] = {}
    if db is not None:
        import json
        from app.models.ai.snapshot import AnalyticsSnapshot
        snapshots = db.query(AnalyticsSnapshot).filter(
            AnalyticsSnapshot.metric_category == "STOCKS"
        ).order_by(AnalyticsSnapshot.snapshot_date.asc()).all()
        for snapshot in snapshots:
            try:
                metrics = json.loads(snapshot.metrics_json)
                for product_id, values in (metrics.get("products") or {}).items():
                    snapshots_by_product.setdefault(int(product_id), []).append(
                        int(values.get("stock_quantity", 0) or 0)
                    )
            except (TypeError, ValueError, AttributeError):
                logger.warning("Snapshot stock illisible: #%s", snapshot.id_snapshot)
    rotation_data = []

    for p in prods:
        qty = p.get("stock_quantity", 0)
        pid = p["id_product"]

        # Récupérer les sorties réelles depuis Dolibarr
        all_movements = await get_stock_movements(product_id=pid, db=db)
        exits = [m for m in all_movements if m["movement_type"] == "SORTIE"]
        entries = [m for m in all_movements if m["movement_type"] == "ENTREE"]

        # Total des sorties réelles
        total_outflow = sum(m["quantity"] for m in exits)
        total_inflow = sum(m["quantity"] for m in entries)

        snapshot_values = snapshots_by_product.get(pid, [])
        if snapshot_values:
            avg_stock = max(1.0, sum(snapshot_values) / len(snapshot_values))
            average_stock_source = "SNAPSHOTS"
        else:
            # Compatibilité pour les produits sans historique de snapshots.
            estimated_initial_stock = qty + total_outflow - total_inflow
            avg_stock = max(1.0, (abs(estimated_initial_stock) + qty) / 2)
            average_stock_source = "ESTIMATION_MOUVEMENTS"

        # Annualisation : si les mouvements couvrent moins d'un an,
        # on extrapole proportionnellement
        # Par défaut on considère les mouvements comme représentant ~6 mois de données
        movement_dates = [
            datetime.fromisoformat(m["created_at"].replace("Z", "+00:00"))
            for m in all_movements if m.get("created_at")
        ]
        if movement_dates:
            delta_days = (max(movement_dates) - min(movement_dates)).days
            observed_days = max(1, delta_days)
        else:
            observed_days = 30

        annualized_outflow = round((total_outflow / observed_days) * 365) if observed_days > 0 else 0

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
            "average_stock_source": average_stock_source,
            "snapshot_count": len(snapshot_values),
            "total_outflow": total_outflow,
            "observed_days": observed_days,
            "annualized_outflow": annualized_outflow,
            "turnover_rate": rate,
            "average_retention_days": retention_days,
            "rotation_speed": speed
        })

    return rotation_data


async def get_product_lots(db: Session) -> List[Dict[str, Any]]:
    """
    Récupère les Lots & Séries avec traçabilité et gestion des dates d'expiration (FEFO).
    Ordre de priorité FEFO (First Expired, First Out).
    """
    prods = await get_all_products()
    prod_map = {p["id_product"]: p for p in prods}
    
    lots = []
    db_lots = db.query(ProductLot).order_by(ProductLot.expiry_date.asc().nullslast(), ProductLot.id_lot.asc()).all()
    for lot in db_lots:
        p = prod_map.get(lot.product_id, {})
        exp_date_str = lot.expiry_date.isoformat() if lot.expiry_date else None
        
        is_expired = False
        is_blocked = False
        status = "VALIDE"
        
        if exp_date_str:
            try:
                exp_date_clean = exp_date_str.split("T")[0].replace("Z", "")
                exp_dt = datetime.strptime(exp_date_clean, "%Y-%m-%d")
                now_dt = datetime.now(timezone.utc).date()
                if exp_dt.date() < now_dt:
                    is_expired = True
                    is_blocked = True
                    status = "EXPIRE"
                elif exp_dt.date() < now_dt + timedelta(days=30):
                    status = "ALERTE_PROCHE"
            except Exception as err:
                logger.error(f"Error parsing date {exp_date_str}: {err}")

        lots.append({
            "id_lot": lot.id_lot,
            "product_id": lot.product_id,
            "product_ref": lot.product_ref or p.get("reference", f"PRD-{lot.product_id}"),
            "product_label": p.get("label", "Produit"),
            "batch_number": lot.lot_number,
            "serial_number": lot.serial_number or "",
            "expiration_date": exp_date_str,
            "quantity": lot.quantity,
            "status": status,
            "is_blocked": is_blocked,
            "created_at": lot.created_at.isoformat() if lot.created_at else None
        })

    lots.sort(key=lambda x: x["expiration_date"] or "9999-12-31")
    return lots


async def create_product_lot(db: Session, lot_data: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
    """Crée et enregistre un lot/série pour le suivi FEFO.

    Validations :
    - Le produit doit exister en base locale.
    - Le numéro de lot (lot_number) doit être unique — IntegrityError si doublon.
    - Le numéro de série (serial_number), s'il est fourni, doit être unique dans le produit.
    """
    from datetime import date
    product = db.query(Product).filter(Product.id_product == lot_data["product_id"]).first()
    if product is None:
        raise RuntimeError("Le produit associé au lot n'existe pas en base locale.")

    lot_number = lot_data.get("batch_number") or lot_data.get("lot_number")
    if not lot_number:
        raise ValueError("Le numéro de lot (batch_number) est obligatoire.")

    # Vérification unicité lot_number
    if db.query(ProductLot).filter(ProductLot.lot_number == lot_number).first():
        raise ValueError(f"Un lot avec le numéro '{lot_number}' existe déjà.")

    # Vérification unicité serial_number au sein du produit
    serial = lot_data.get("serial_number")
    if serial:
        existing_serial = db.query(ProductLot).filter(
            ProductLot.product_id == lot_data["product_id"],
            ProductLot.serial_number == serial,
        ).first()
        if existing_serial:
            raise ValueError(
                f"Le numéro de série '{serial}' est déjà utilisé pour ce produit (lot #{existing_serial.id_lot})."
            )

    expiry = lot_data.get("expiration_date")
    expiry_date = date.fromisoformat(expiry[:10]) if expiry else None
    lot = ProductLot(
        lot_number=lot_number,
        serial_number=serial,
        product_id=lot_data["product_id"],
        product_label=product.label,
        product_ref=product.reference,
        quantity=lot_data.get("quantity", 0),
        initial_quantity=lot_data.get("quantity", 0),
        unit_price=lot_data.get("unit_price", 0.0),
        expiry_date=expiry_date,
        reception_date=datetime.now(timezone.utc).date(),
        notes=lot_data.get("supplier_ref"),
        created_by_user_id=user_id,
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return {
        "id_lot": lot.id_lot,
        "product_id": lot.product_id,
        "product_ref": lot.product_ref,
        "product_label": lot.product_label,
        "batch_number": lot.lot_number,
        "serial_number": lot.serial_number,
        "expiration_date": lot.expiry_date.isoformat() if lot.expiry_date else None,
        "quantity": lot.quantity,
        "created_at": lot.created_at.isoformat() if lot.created_at else None,
    }

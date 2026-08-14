import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta

from app.services.dolibarr.client import dolibarr_client
from app.services.products.product_service import get_all_products, record_stock_movement

logger = logging.getLogger(__name__)

# Primary in-memory store for Purchase Workflow & Supplier Analytics
_purchases_store: Dict[str, List[Dict[str, Any]]] = {
    "suppliers": [],
    "requisitions": [],
    "orders": [],
    "receipts": [],
    "invoices": []
}


# --- FOURNISSEURS (SUPPLIERS) ---

async def get_suppliers() -> List[Dict[str, Any]]:
    """
    Récupère la liste des fournisseurs depuis Dolibarr (`thirdparties?category=supplier`)
    avec synchronisation du store local.
    """
    try:
        doli_suppliers = await dolibarr_client.get_thirdparties(category="supplier")
        if doli_suppliers and isinstance(doli_suppliers, list):
            existing_ids = {s.get("dolibarr_id") for s in _purchases_store["suppliers"] if s.get("dolibarr_id")}
            for s in doli_suppliers:
                d_id = int(s.get("id"))
                if d_id not in existing_ids:
                    _purchases_store["suppliers"].append({
                        "id_supplier": len(_purchases_store["suppliers"]) + 1,
                        "dolibarr_id": d_id,
                        "code": s.get("code_fournisseur") or f"FOURN-{d_id}",
                        "name": s.get("name") or s.get("nom") or f"Fournisseur Dolibarr #{d_id}",
                        "email": s.get("email") or "",
                        "phone": s.get("phone") or "",
                        "address": s.get("address") or "",
                        "status": "ACTIF",
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
    except Exception as e:
        logger.warning(f"Récupération fournisseurs Dolibarr API: {e}")

    return _purchases_store["suppliers"]


async def create_supplier(supplier_data: Dict[str, Any]) -> Dict[str, Any]:
    """Création d'un nouveau fournisseur dans Dolibarr et en local."""
    new_id = len(_purchases_store["suppliers"]) + 1
    doli_id = None
    
    # Payload pour Dolibarr API
    payload = {
        "name": supplier_data["name"],
        "code_fournisseur": supplier_data.get("code") or f"FOURN-{new_id:03d}",
        "fournisseur": "1",
        "client": "0",
        "email": supplier_data.get("email", ""),
        "phone": supplier_data.get("phone", ""),
        "address": supplier_data.get("address", "")
    }

    try:
        res = await dolibarr_client.post("thirdparties", payload)
        doli_id = res if isinstance(res, int) else (res.get("id") if isinstance(res, dict) else None)
    except Exception as e:
        logger.warning(f"Création fournisseur Dolibarr ignorée ou indisponible: {e}")

    item = {
        "id_supplier": new_id,
        "dolibarr_id": doli_id,
        "code": payload["code_fournisseur"],
        "name": supplier_data["name"],
        "email": supplier_data.get("email", ""),
        "phone": supplier_data.get("phone", ""),
        "address": supplier_data.get("address", ""),
        "status": supplier_data.get("status", "ACTIF"),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _purchases_store["suppliers"].append(item)
    return item


# --- DEMANDES D'ACHAT (WORKFLOW ETAPE 1 & 2) ---

async def get_purchase_requisitions() -> List[Dict[str, Any]]:
    """Récupère toutes les demandes d'achat enregistrées."""
    return _purchases_store["requisitions"]


async def create_purchase_requisition(req_data: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
    """Étape 1 : Enregistre une nouvelle Demande d'Achat."""
    prods = await get_all_products()
    prod_map = {p["id_product"]: p for p in prods}
    p = prod_map.get(req_data["product_id"], {})

    suppliers = await get_suppliers()
    sup_map = {s["id_supplier"]: s for s in suppliers}
    s = sup_map.get(req_data.get("supplier_id"), {}) if req_data.get("supplier_id") else {}

    new_id = len(_purchases_store["requisitions"]) + 1
    ref = f"DA-2026-{new_id:03d}"
    qty = req_data["quantity"]
    unit_price = req_data["estimated_unit_price"]

    item = {
        "id_requisition": new_id,
        "reference": ref,
        "product_id": req_data["product_id"],
        "product_label": p.get("label", f"Produit #{req_data['product_id']}"),
        "product_ref": p.get("reference", "REF-PRD"),
        "supplier_id": req_data.get("supplier_id"),
        "supplier_name": s.get("name") or "Fournisseur non attribué",
        "quantity": qty,
        "estimated_unit_price": unit_price,
        "total_estimated": round(qty * unit_price, 2),
        "status": "DEMANDE",
        "reason": req_data.get("reason", "Besoin d'approvisionnement"),
        "created_by_user_id": user_id or 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "validated_at": None
    }
    _purchases_store["requisitions"].append(item)
    return item


async def validate_purchase_requisition(requisition_id: int, action: str, comment: Optional[str] = None) -> Dict[str, Any]:
    """Étape 2 : Validation ou Rejet de la Demande d'Achat selon le rôle."""
    req = next((r for r in _purchases_store["requisitions"] if r["id_requisition"] == requisition_id), None)
    if not req:
        raise RuntimeError(f"Demande d'achat #{requisition_id} non trouvée.")

    if action.upper() == "VALIDER":
        req["status"] = "VALIDEE"
        req["validated_at"] = datetime.now(timezone.utc).isoformat()
    elif action.upper() == "REJETER":
        req["status"] = "REJETEE"
        req["reason"] = f"{req.get('reason', '')} | Motifs rejet : {comment or 'Non spécifié'}"
    else:
        raise ValueError("Action invalide. Utilisez 'VALIDER' ou 'REJETER'.")

    return req


# --- COMMANDES D'ACHAT (WORKFLOW ETAPE 3) ---

async def get_purchase_orders() -> List[Dict[str, Any]]:
    """Récupère la liste des Commandes d'Achat."""
    return _purchases_store["orders"]


async def create_purchase_order(order_data: Dict[str, Any]) -> Dict[str, Any]:
    """Étape 3 : Création de la Commande d'Achat (depuis demande ou directe)."""
    prods = await get_all_products()
    prod_map = {p["id_product"]: p for p in prods}
    p = prod_map.get(order_data["product_id"], {})

    suppliers = await get_suppliers()
    sup_map = {s["id_supplier"]: s for s in suppliers}
    s = sup_map.get(order_data["supplier_id"], {})

    new_id = len(_purchases_store["orders"]) + 1
    ref = f"CFA-2026-{new_id:03d}"
    qty = order_data["quantity"]
    unit_price = order_data["unit_price"]

    exp_date = order_data.get("expected_delivery_date") or (datetime.now(timezone.utc) + timedelta(days=5)).strftime("%Y-%m-%d")

    item = {
        "id_order": new_id,
        "reference": ref,
        "requisition_id": order_data.get("requisition_id"),
        "supplier_id": order_data["supplier_id"],
        "supplier_name": s.get("name", f"Fournisseur #{order_data['supplier_id']}"),
        "product_id": order_data["product_id"],
        "product_label": p.get("label", f"Produit #{order_data['product_id']}"),
        "product_ref": p.get("reference", "REF-PRD"),
        "quantity": qty,
        "unit_price": unit_price,
        "total_amount": round(qty * unit_price, 2),
        "status": "COMMANDEE",
        "order_date": datetime.now(timezone.utc).isoformat(),
        "expected_delivery_date": exp_date,
        "actual_delivery_date": None
    }

    _purchases_store["orders"].append(item)

    # Si issue d'une demande, mettre à jour son statut
    if order_data.get("requisition_id"):
        req = next((r for r in _purchases_store["requisitions"] if r["id_requisition"] == order_data["requisition_id"]), None)
        if req:
            req["status"] = "COMMANDEE"

    return item


# --- RÉCEPTION & CONTRÔLE (WORKFLOW ETAPE 4 & 5) ---

async def get_goods_receipts() -> List[Dict[str, Any]]:
    """Récupère l'historique des Réceptions et Contrôles qualité."""
    return _purchases_store["receipts"]


async def record_goods_receipt(receipt_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Étape 4 & 5 : Réception des marchandises & Contrôle qualité.
    Impacte immédiatement le stock réel dans Dolibarr via `record_stock_movement`.
    """
    order = next((o for o in _purchases_store["orders"] if o["id_order"] == receipt_data["order_id"]), None)
    if not order:
        raise RuntimeError(f"Commande d'achat #{receipt_data['order_id']} non trouvée.")

    new_id = len(_purchases_store["receipts"]) + 1
    ref = f"REC-2026-{new_id:03d}"
    now_iso = datetime.now(timezone.utc).isoformat()

    receipt_item = {
        "id_receipt": new_id,
        "reference": ref,
        "order_id": order["id_order"],
        "order_ref": order["reference"],
        "product_label": order["product_label"],
        "quantity_received": receipt_data["quantity_received"],
        "quality_control_status": receipt_data.get("quality_control_status", "CONFORME"),
        "quality_notes": receipt_data.get("quality_notes", "Contrôle effectué lors de la réception"),
        "received_at": now_iso
    }
    _purchases_store["receipts"].append(receipt_item)

    # Mise à jour du statut de la commande
    order["status"] = "RECUE"
    order["actual_delivery_date"] = now_iso

    # Mise à jour directe du stock dans Dolibarr (Entrée de stock)
    try:
        await record_stock_movement(
            product_id=order["product_id"],
            movement_type="ENTREE",
            quantity=receipt_data["quantity_received"],
            reference_doc=order["reference"],
            comment=f"Réception Commande Achat ({ref})"
        )
    except Exception as e:
        logger.warning(f"Mouvement de stock lors de la réception: {e}")

    return receipt_item


# --- FACTURATION FOURNISSEUR (WORKFLOW ETAPE 6) ---

async def get_supplier_invoices() -> List[Dict[str, Any]]:
    """Récupère la liste des Factures Fournisseurs."""
    return _purchases_store["invoices"]


async def create_supplier_invoice(inv_data: Dict[str, Any]) -> Dict[str, Any]:
    """Étape 6 : Création et comptabilisation de la Facture Fournisseur."""
    order = next((o for o in _purchases_store["orders"] if o["id_order"] == inv_data["order_id"]), None)
    if not order:
        raise RuntimeError(f"Commande d'achat #{inv_data['order_id']} non trouvée.")

    new_id = len(_purchases_store["invoices"]) + 1
    ht = float(inv_data["amount_ht"])
    vat = float(inv_data.get("vat_rate", 20.0))
    ttc = round(ht * (1 + vat / 100.0), 2)

    item = {
        "id_invoice": new_id,
        "invoice_number": inv_data["invoice_number"],
        "order_id": order["id_order"],
        "order_ref": order["reference"],
        "supplier_name": order["supplier_name"],
        "amount_ht": ht,
        "vat_rate": vat,
        "amount_ttc": ttc,
        "status": "VALIDEE",
        "invoice_date": inv_data.get("invoice_date") or datetime.now(timezone.utc).isoformat()
    }
    _purchases_store["invoices"].append(item)
    return item


# --- MODULE 6 : ANALYSE DES FOURNISSEURS & SCORE IA ---

async def get_supplier_performance_analysis(
    weights: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    MODULE 6 — Calcule l'analyse de performance et le Score % pour chaque fournisseur.
    Pondération par défaut :
      - Prix : 30%
      - Délai : 25%
      - Qualité : 25%
      - Fiabilité : 20%
    """
    w_price = weights.get("price_weight", 0.30) if weights else 0.30
    w_delay = weights.get("delay_weight", 0.25) if weights else 0.25
    w_quality = weights.get("quality_weight", 0.25) if weights else 0.25
    w_rel = weights.get("reliability_weight", 0.20) if weights else 0.20

    suppliers = await get_suppliers()
    orders = _purchases_store["orders"]
    receipts = _purchases_store["receipts"]

    results = []

    # Données simulées / réelles enrichies par fournisseur
    base_metrics = {
        1: {"avg_price": 200.0, "avg_days": 2.5, "delay_rate": 4.0, "conformity": 98.0, "freq": 14.0, "trend": "STABLE"},
        2: {"avg_price": 185.0, "avg_days": 4.0, "delay_rate": 12.0, "conformity": 92.0, "freq": 8.0, "trend": "BAISSE"},
        3: {"avg_price": 220.0, "avg_days": 1.8, "delay_rate": 2.0, "conformity": 99.5, "freq": 18.0, "trend": "HAUSSE"}
    }

    for sup in suppliers:
        s_id = sup["id_supplier"]
        m = base_metrics.get(s_id, {
            "avg_price": 210.0, "avg_days": 3.0, "delay_rate": 8.0, "conformity": 95.0, "freq": 6.0, "trend": "STABLE"
        })

        # Compter les commandes réelles si disponibles
        sup_orders = [o for o in orders if o["supplier_id"] == s_id]
        total_orders = len(sup_orders) or int(m["freq"])

        # Calcul des scores partiels sur 100
        # Prix (Plus le prix moyen est bas, meilleur est le score)
        score_price = max(50.0, min(100.0, 100.0 - (m["avg_price"] - 180.0) * 0.5))
        
        # Délai (Plus les jours de livraison sont courts, meilleur est le score)
        score_delay = max(40.0, min(100.0, 100.0 - (m["avg_days"] * 8.0)))
        
        # Qualité (% de conformité lors du contrôle)
        score_quality = m["conformity"]
        
        # Fiabilité (100 - Taux de retard %)
        score_reliability = max(0.0, 100.0 - m["delay_rate"])

        # Score Global %
        overall_score = round(
            (score_price * w_price) +
            (score_delay * w_delay) +
            (score_quality * w_quality) +
            (score_reliability * w_rel),
            1
        )

        if overall_score >= 88.0:
            badge = "RECOMMANDÉ"
        elif overall_score >= 75.0:
            badge = "ACCEPTABLE"
        else:
            badge = "À RISQUE"

        results.append({
            "supplier_id": s_id,
            "supplier_name": sup["name"],
            "total_orders": total_orders,
            "avg_price": m["avg_price"],
            "avg_delivery_days": m["avg_days"],
            "delay_rate_percent": m["delay_rate"],
            "conformity_rate_percent": m["conformity"],
            "quality_score": round(score_quality, 1),
            "order_frequency_per_year": m["freq"],
            "price_trend": m["trend"],
            "score_price": round(score_price, 1),
            "score_delay": round(score_delay, 1),
            "score_quality": round(score_quality, 1),
            "score_reliability": round(score_reliability, 1),
            "overall_score_percent": overall_score,
            "recommendation_badge": badge
        })

    # Trier du meilleur au moins bon score
    results.sort(key=lambda x: x["overall_score_percent"], reverse=True)
    return results


async def get_ai_supplier_recommendation(
    priority: str = "BALANCED",
    product_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    IA Assistant : Propose le meilleur fournisseur selon la stratégie choisie par l'utilisateur.
    """
    weights_map = {
        "BALANCED": {"price_weight": 0.30, "delay_weight": 0.25, "quality_weight": 0.25, "reliability_weight": 0.20},
        "PRIX": {"price_weight": 0.60, "delay_weight": 0.15, "quality_weight": 0.15, "reliability_weight": 0.10},
        "DELAI": {"price_weight": 0.15, "delay_weight": 0.60, "quality_weight": 0.15, "reliability_weight": 0.10},
        "QUALITE": {"price_weight": 0.15, "delay_weight": 0.15, "quality_weight": 0.60, "reliability_weight": 0.10},
        "FIABILITE": {"price_weight": 0.15, "delay_weight": 0.15, "quality_weight": 0.15, "reliability_weight": 0.55}
    }

    w = weights_map.get(priority.upper(), weights_map["BALANCED"])
    analysis = await get_supplier_performance_analysis(weights=w)

    best_supplier = analysis[0] if analysis else None

    if not best_supplier:
        return {
            "priority_criterion": priority.upper(),
            "recommended_supplier": None,
            "ai_explanation": "Aucun fournisseur disponible pour la recommandation.",
            "all_rankings": []
        }

    reasons = {
        "BALANCED": f"{best_supplier['supplier_name']} offre le meilleur équilibre global avec un score de {best_supplier['overall_score_percent']}%.",
        "PRIX": f"{best_supplier['supplier_name']} est sélectionné pour son tarif le plus compétitif ({best_supplier['avg_price']} € en moyenne).",
        "DELAI": f"{best_supplier['supplier_name']} garantit la livraison la plus rapide ({best_supplier['avg_delivery_days']} jours en moyenne).",
        "QUALITE": f"{best_supplier['supplier_name']} détient le meilleur taux de conformité qualité ({best_supplier['conformity_rate_percent']}%).",
        "FIABILITE": f"{best_supplier['supplier_name']} présente le plus faible taux de retard ({best_supplier['delay_rate_percent']}%)."
    }

    return {
        "priority_criterion": priority.upper(),
        "recommended_supplier": best_supplier,
        "ai_explanation": reasons.get(priority.upper(), reasons["BALANCED"]),
        "all_rankings": analysis
    }


async def get_purchases_overview() -> Dict[str, Any]:
    """KPIs synthétiques du module Achats."""
    suppliers = await get_suppliers()
    reqs = _purchases_store["requisitions"]
    orders = _purchases_store["orders"]
    invoices = _purchases_store["invoices"]

    total_spent = sum(o["total_amount"] for o in orders if o["status"] in ["COMMANDEE", "RECUE"])
    pending_reqs = sum(1 for r in reqs if r["status"] == "DEMANDE")
    active_orders = sum(1 for o in orders if o["status"] == "COMMANDEE")

    analysis = await get_supplier_performance_analysis()
    top_supplier = analysis[0]["supplier_name"] if analysis else "N/A"

    return {
        "total_suppliers": len(suppliers),
        "total_purchase_amount": round(total_spent, 2),
        "pending_requisitions_count": pending_reqs,
        "active_orders_count": active_orders,
        "invoices_count": len(invoices),
        "top_performing_supplier": top_supplier
    }

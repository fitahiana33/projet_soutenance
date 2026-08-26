import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.dolibarr.client import dolibarr_client
from app.services.products.product_service import get_all_products
from app.services.audit.audit_service import log_action
from app.models.sales.sales import (
    Customer,
    SalesQuote,
    SalesOrder,
    Delivery,
    SalesInvoice,
)

logger = logging.getLogger(__name__)


def _serialize_customer(c: Customer) -> Dict[str, Any]:
    return {
        "id_customer": c.id_customer,
        "dolibarr_id": c.dolibarr_id,
        "code_client": c.code_client,
        "name": c.name,
        "email": c.email,
        "phone": c.phone,
        "address": c.address,
        "city": c.city,
        "country": c.country,
        "tax_number": c.tax_number,
        "credit_limit": c.credit_limit,
        "payment_terms": c.payment_terms,
        "payment_terms_days": c.payment_terms_days,
        "status": c.status,
        "total_revenue_generated": c.total_revenue_generated,
        "notes": c.notes,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def _serialize_quote(q: SalesQuote) -> Dict[str, Any]:
    items = []
    try:
        if q.items_json:
            items = json.loads(q.items_json) if isinstance(q.items_json, str) else q.items_json
    except Exception:
        items = []
    return {
        "id_quote": q.id_quote,
        "quote_ref": q.reference,
        "customer_id": q.customer_id,
        "customer_name": q.customer_name,
        "title": q.title,
        "items": items,
        "total_amount_ht": q.total_ht,
        "total_amount_ttc": q.total_ttc,
        "total_tva": q.vat_amount,
        "vat_rate": q.vat_rate,
        "discount_percent": q.discount_percent,
        "status": q.status,
        "quote_date": q.quote_date.isoformat() if q.quote_date else None,
        "validity_date": q.validity_date.isoformat() if q.validity_date else None,
        "accepted_date": q.accepted_date.isoformat() if q.accepted_date else None,
        "notes": q.notes,
        "created_by_user_id": q.created_by_user_id,
        "created_at": q.created_at.isoformat() if q.created_at else None,
        "updated_at": q.updated_at.isoformat() if q.updated_at else None,
    }


def _serialize_order(o: SalesOrder) -> Dict[str, Any]:
    items = []
    try:
        if o.items_json:
            items = json.loads(o.items_json) if isinstance(o.items_json, str) else o.items_json
    except Exception:
        items = []
    items_count = len(items)
    stock_reserved = o.status in ["CONFIRMEE", "EN_PREPARATION", "LIVREE", "VALIDEE", "FACTUREE"]
    return {
        "id_order": o.id_order,
        "order_ref": o.reference,
        "quote_id": o.quote_id,
        "customer_id": o.customer_id,
        "customer_name": o.customer_name,
        "items": items,
        "items_count": items_count,
        "total_amount_ht": o.total_ht,
        "total_amount_ttc": o.total_ttc,
        "total_tva": o.vat_amount,
        "vat_rate": o.vat_rate,
        "discount_percent": o.discount_percent,
        "status": o.status,
        "stock_reserved": stock_reserved,
        "order_date": o.order_date.isoformat() if o.order_date else None,
        "expected_delivery_date": o.expected_delivery_date.isoformat() if o.expected_delivery_date else None,
        "actual_delivery_date": o.actual_delivery_date.isoformat() if o.actual_delivery_date else None,
        "delivery_address": o.shipping_address,
        "billing_address": o.billing_address,
        "shipping_address": o.shipping_address,
        "notes": o.notes,
        "created_by_user_id": o.created_by_user_id,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "updated_at": o.updated_at.isoformat() if o.updated_at else None,
    }


def _serialize_delivery(d: Delivery) -> Dict[str, Any]:
    items = []
    try:
        if d.items_json:
            items = json.loads(d.items_json) if isinstance(d.items_json, str) else d.items_json
    except Exception:
        items = []
    return {
        "id_delivery": d.id_delivery,
        "reference": d.reference,
        "order_id": d.order_id,
        "order_ref": d.order_ref,
        "customer_name": d.customer_name,
        "items": items,
        "total_quantity": d.total_quantity,
        "tracking_number": d.tracking_number,
        "carrier_name": d.carrier,
        "delivery_address": None,
        "delivery_date": d.delivery_date.isoformat() if d.delivery_date else None,
        "status": d.status,
        "customer_signature": d.customer_signature,
        "received_by": None,
        "received_at": None,
        "delivered_by_user_id": d.delivered_by_user_id,
        "notes": d.notes,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
    }


def _serialize_invoice(i: SalesInvoice) -> Dict[str, Any]:
    items = []
    try:
        if i.items_json:
            items = json.loads(i.items_json) if isinstance(i.items_json, str) else i.items_json
    except Exception:
        items = []
    balance_due = max(0.0, i.total_ttc - i.amount_paid)
    return {
        "id_invoice": i.id_invoice,
        "invoice_ref": i.invoice_number,
        "invoice_number": i.invoice_number,
        "order_id": i.order_id,
        "order_ref": i.order_ref,
        "customer_id": i.customer_id,
        "customer_name": i.customer_name,
        "items": items,
        "total_amount_ht": i.total_ht,
        "total_amount_ttc": i.total_ttc,
        "total_tva": i.vat_amount,
        "vat_rate": i.vat_rate,
        "discount_percent": i.discount_percent,
        "amount_paid": i.amount_paid,
        "balance_due": balance_due,
        "remaining_amount": i.remaining_amount,
        "is_paid": i.is_paid,
        "payment_status": i.status,
        "payment_mode": i.payment_method,
        "payment_method": i.payment_method,
        "status": i.status,
        "invoice_date": i.invoice_date.isoformat() if i.invoice_date else None,
        "due_date": i.due_date.isoformat() if i.due_date else None,
        "paid_date": i.paid_date.isoformat() if i.paid_date else None,
        "payment_ref": i.payment_ref,
        "notes": i.notes,
        "created_by_user_id": i.created_by_user_id,
        "created_at": i.created_at.isoformat() if i.created_at else None,
        "updated_at": i.updated_at.isoformat() if i.updated_at else None,
    }


async def get_all_customers(db: Session, actor_user: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Récupère les clients depuis Dolibarr puis synchronise en base, ou retourne la base."""
    try:
        thirdparties = await dolibarr_client.get("thirdparties", params={"sqlfilters": "(t.client:=:1 OR t.client:=:2)"})
        if thirdparties and isinstance(thirdparties, list):
            for t in thirdparties:
                cid = int(t.get("id", 0))
                if cid <= 0:
                    continue
                existing = db.query(Customer).filter(Customer.dolibarr_id == cid).first()
                code = t.get("code_client") or f"CLI-{cid:04d}"
                name = t.get("name") or t.get("nom") or f"Client #{cid}"
                status = "ACTIF" if t.get("status") == "1" else "INACTIF"
                if not existing:
                    obj = Customer(
                        dolibarr_id=cid,
                        code_client=code,
                        name=name,
                        email=t.get("email") or None,
                        phone=t.get("phone") or None,
                        address=t.get("address") or None,
                        city=t.get("town") or None,
                        payment_terms=t.get("cond_reglement_code") or "30_DAYS",
                        total_revenue_generated=float(t.get("outstanding_limit", 0.0) or 0.0),
                        status=status,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                    db.add(obj)
                else:
                    existing.name = name
                    existing.email = t.get("email") or existing.email
                    existing.phone = t.get("phone") or existing.phone
                    existing.address = t.get("address") or existing.address
                    existing.city = t.get("town") or existing.city
                    existing.status = status
                    existing.updated_at = datetime.now(timezone.utc)
            db.commit()
    except Exception as e:
        logger.warning(f"Récupération clients Dolibarr: {e}")

    customers = db.query(Customer).order_by(Customer.created_at.desc()).all()
    return [_serialize_customer(c) for c in customers]


def create_customer(
    db: Session,
    cust_data: Dict[str, Any],
    actor_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Création d'un nouveau tiers client en base PostgreSQL."""
    last_id = db.query(func.max(Customer.id_customer)).scalar() or 0
    new_id = last_id + 1
    code = cust_data.get("code_client") or f"CLI-2026-{new_id:03d}"

    payment_terms = cust_data.get("payment_terms", "30_DAYS")
    payment_terms_days_map = {
        "CASH": 0,
        "15_DAYS": 15,
        "30_DAYS": 30,
        "45_DAYS": 45,
        "60_DAYS": 60,
        "90_DAYS": 90,
    }
    ptd = payment_terms_days_map.get(payment_terms, 30)

    obj = Customer(
        code_client=code,
        name=cust_data["name"],
        email=cust_data.get("email"),
        phone=cust_data.get("phone"),
        address=cust_data.get("address"),
        city=cust_data.get("city"),
        tax_number=cust_data.get("siret_nif") or cust_data.get("tax_number"),
        status="ACTIF",
        payment_terms=payment_terms,
        payment_terms_days=cust_data.get("payment_terms_days", ptd),
        total_revenue_generated=0.0,
        credit_limit=cust_data.get("credit_limit"),
        notes=cust_data.get("notes"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    if actor_user is not None:
        try:
            log_action(
                db,
                action="CREATE",
                module="VENTES",
                user_id=getattr(actor_user, "id_user", None),
                username=getattr(actor_user, "username", "SYSTEM"),
                user_role=getattr(actor_user, "role", None),
                target_entity=f"Client {obj.name}",
                details=f"Création client {obj.code_client}",
                new_values=_serialize_customer(obj),
            )
        except Exception as ae:
            logger.warning(f"Audit log create_customer: {ae}")

    return _serialize_customer(obj)


def get_customer_by_id(db: Session, customer_id: int) -> Optional[Dict[str, Any]]:
    """Récupère un client par son ID."""
    c = db.query(Customer).filter(Customer.id_customer == customer_id).first()
    return _serialize_customer(c) if c else None


def update_customer(
    db: Session,
    customer_id: int,
    cust_data: Dict[str, Any],
    actor_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Met à jour un client existant."""
    obj = db.query(Customer).filter(Customer.id_customer == customer_id).first()
    if not obj:
        raise RuntimeError(f"Client #{customer_id} non trouvé.")

    old = _serialize_customer(obj)

    for field in [
        "name",
        "code_client",
        "email",
        "phone",
        "address",
        "city",
        "country",
        "credit_limit",
        "payment_terms",
        "payment_terms_days",
        "status",
        "notes",
    ]:
        if field in cust_data and cust_data[field] is not None:
            setattr(obj, field, cust_data[field])
    if "siret_nif" in cust_data and cust_data["siret_nif"]:
        obj.tax_number = cust_data["siret_nif"]
    if "tax_number" in cust_data and cust_data["tax_number"]:
        obj.tax_number = cust_data["tax_number"]

    obj.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(obj)

    if actor_user is not None:
        try:
            log_action(
                db,
                action="UPDATE",
                module="VENTES",
                user_id=getattr(actor_user, "id_user", None),
                username=getattr(actor_user, "username", "SYSTEM"),
                user_role=getattr(actor_user, "role", None),
                target_entity=f"Client {obj.name}",
                details=f"Mise à jour client {obj.code_client}",
                old_values=old,
                new_values=_serialize_customer(obj),
            )
        except Exception as ae:
            logger.warning(f"Audit log update_customer: {ae}")

    return _serialize_customer(obj)


def delete_customer(
    db: Session,
    customer_id: int,
    actor_user: Optional[Any] = None,
) -> bool:
    """Supprime un client (soft delete via status INACTIF + suppression physique si pas de liens)."""
    obj = db.query(Customer).filter(Customer.id_customer == customer_id).first()
    if not obj:
        raise RuntimeError(f"Client #{customer_id} non trouvé.")

    old = _serialize_customer(obj)
    linked_orders = db.query(SalesOrder).filter(SalesOrder.customer_id == customer_id).count()
    linked_quotes = db.query(SalesQuote).filter(SalesQuote.customer_id == customer_id).count()
    linked_invoices = db.query(SalesInvoice).filter(SalesInvoice.customer_id == customer_id).count()

    if linked_orders == 0 and linked_quotes == 0 and linked_invoices == 0:
        db.delete(obj)
        db.commit()
        result = True
    else:
        obj.status = "INACTIF"
        obj.updated_at = datetime.now(timezone.utc)
        db.commit()
        result = True

    if actor_user is not None:
        try:
            log_action(
                db,
                action="DELETE",
                module="VENTES",
                user_id=getattr(actor_user, "id_user", None),
                username=getattr(actor_user, "username", "SYSTEM"),
                user_role=getattr(actor_user, "role", None),
                target_entity=f"Client #{customer_id}",
                details=f"Suppression client (status={obj.status if not result else 'DELETED'})",
                old_values=old,
            )
        except Exception as ae:
            logger.warning(f"Audit log delete_customer: {ae}")

    return result


def get_sales_quotes(db: Session, actor_user: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Récupère la liste des devis & pro-formas de vente depuis PostgreSQL."""
    quotes = db.query(SalesQuote).order_by(SalesQuote.created_at.desc()).all()
    return [_serialize_quote(q) for q in quotes]


def get_sales_quote_by_id(db: Session, quote_id: int) -> Optional[Dict[str, Any]]:
    q = db.query(SalesQuote).filter(SalesQuote.id_quote == quote_id).first()
    return _serialize_quote(q) if q else None


async def create_sales_quote(
    db: Session,
    quote_data: Dict[str, Any],
    actor_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Création d'un devis client en base PostgreSQL."""
    cust = db.query(Customer).filter(Customer.id_customer == quote_data["customer_id"]).first()
    if not cust:
        raise RuntimeError(f"Client #{quote_data['customer_id']} non trouvé.")

    products = await get_all_products()
    prod_map = {p["id_product"]: p for p in products}

    tot_ht = 0.0
    items_detail = []
    items_input = quote_data.get("items") or []
    if items_input:
        for it in items_input:
            pid = it.get("product_id", 1)
            qty = float(it.get("quantity", 1))
            p = prod_map.get(pid, {})
            unit_p = float(it.get("unit_price") or p.get("price", 10.0))
            disc = float(it.get("discount_percent", 0.0))

            line_tot = qty * unit_p * (1 - disc / 100.0)
            tot_ht += line_tot

            items_detail.append({
                "product_id": pid,
                "reference": p.get("reference", f"PRD-{pid}"),
                "label": p.get("label", "Produit"),
                "quantity": qty,
                "unit_price": unit_p,
                "discount_percent": disc,
                "discount_amount": round(qty * unit_p * disc / 100.0, 2),
                "gross_line_ht": round(qty * unit_p, 2),
                "total_line_ht": round(line_tot, 2),
            })
    else:
        tot_ht = float(quote_data.get("total_amount_ttc", 1000.0)) / 1.20

    gross_ht = sum(float(it.get("quantity", 1)) * float(it.get("unit_price") or 0) for it in items_input)
    discount_amount = max(0.0, gross_ht - tot_ht)
    vat_rate = float(quote_data.get("vat_rate", 20.0))
    vat_amount = round(tot_ht * vat_rate / 100.0, 2)
    tot_ttc = round(tot_ht + vat_amount, 2)

    last_id = db.query(func.max(SalesQuote.id_quote)).scalar() or 0
    new_id = last_id + 1
    reference = f"DEV-2026-{new_id:04d}"
    validity_days = int(quote_data.get("validity_days", 30))
    today = datetime.now(timezone.utc).date()

    obj = SalesQuote(
        reference=reference,
        customer_id=cust.id_customer,
        customer_name=cust.name,
        title=quote_data.get("title"),
        items_json=json.dumps(items_detail, ensure_ascii=False),
        total_ht=round(tot_ht, 2),
        vat_rate=vat_rate,
        vat_amount=vat_amount,
        total_ttc=tot_ttc,
        discount_percent=round((discount_amount / gross_ht) * 100, 2) if gross_ht else 0.0,
        status="EN_ATTENTE",
        quote_date=today,
        validity_date=today + timedelta(days=validity_days),
        notes=quote_data.get("notes"),
        created_by_user_id=getattr(actor_user, "id_user", None) if actor_user else quote_data.get("created_by_user_id"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    if actor_user is not None:
        try:
            log_action(
                db,
                action="CREATE",
                module="VENTES",
                user_id=getattr(actor_user, "id_user", None),
                username=getattr(actor_user, "username", "SYSTEM"),
                user_role=getattr(actor_user, "role", None),
                target_entity=f"Devis {reference}",
                details=f"Devis client #{cust.id_customer} - {cust.name}",
                new_values=_serialize_quote(obj),
            )
        except Exception as ae:
            logger.warning(f"Audit log create_sales_quote: {ae}")

    return _serialize_quote(obj)


def update_sales_quote_status(
    db: Session,
    quote_id: int,
    new_status: str,
    actor_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Mise à jour du statut d'un devis."""
    obj = db.query(SalesQuote).filter(SalesQuote.id_quote == quote_id).first()
    if not obj:
        raise RuntimeError(f"Devis #{quote_id} non trouvé.")

    old = _serialize_quote(obj)
    valid_statuses = ["DRAFT", "ENVOYE", "ACCEPTE", "REFUSE", "PERDU", "EN_ATTENTE", "EXPIRE"]
    if new_status not in valid_statuses:
        logger.warning(f"Statut devis invalide {new_status}, utilisation brutale.")
    obj.status = new_status
    if new_status == "ACCEPTE":
        obj.accepted_date = datetime.now(timezone.utc).date()
    obj.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(obj)

    if actor_user is not None:
        try:
            log_action(
                db,
                action="UPDATE",
                module="VENTES",
                user_id=getattr(actor_user, "id_user", None),
                username=getattr(actor_user, "username", "SYSTEM"),
                user_role=getattr(actor_user, "role", None),
                target_entity=f"Devis {obj.reference}",
                details=f"Statut devis -> {new_status}",
                old_values=old,
                new_values=_serialize_quote(obj),
            )
        except Exception as ae:
            logger.warning(f"Audit log update_sales_quote_status: {ae}")

    return _serialize_quote(obj)


def get_sales_orders(db: Session, actor_user: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Récupère l'historique des commandes de vente depuis PostgreSQL."""
    orders = db.query(SalesOrder).order_by(SalesOrder.created_at.desc()).all()
    return [_serialize_order(o) for o in orders]


def get_sales_order_by_id(db: Session, order_id: int) -> Optional[Dict[str, Any]]:
    o = db.query(SalesOrder).filter(SalesOrder.id_order == order_id).first()
    return _serialize_order(o) if o else None


async def create_sales_order(
    db: Session,
    order_data: Dict[str, Any],
    actor_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Création d'une commande client avec réservation de stock en base PostgreSQL."""
    cust = db.query(Customer).filter(Customer.id_customer == order_data["customer_id"]).first()
    if not cust:
        raise RuntimeError(f"Client #{order_data['customer_id']} non trouvé.")

    products = await get_all_products()
    prod_map = {p["id_product"]: p for p in products}

    tot_ht = 0.0
    items_detail = []
    for it in order_data["items"]:
        pid = it["product_id"]
        qty = float(it["quantity"])
        p = prod_map.get(pid, {})
        unit_p = float(it.get("unit_price") or p.get("price", 10.0))
        disc = float(it.get("discount_percent", 0.0))

        gross_line = qty * unit_p
        discount_amount = gross_line * disc / 100.0
        line_tot = gross_line - discount_amount
        tot_ht += line_tot

        items_detail.append({
            "product_id": pid,
            "reference": p.get("reference", f"PRD-{pid}"),
            "label": p.get("label", "Produit"),
            "quantity": qty,
            "unit_price": unit_p,
            "discount_percent": disc,
            "discount_amount": round(discount_amount, 2),
            "gross_line_ht": round(gross_line, 2),
            "total_line_ht": round(line_tot, 2),
        })

    gross_ht = sum(float(it.get("quantity", 1)) * float(it.get("unit_price") or 0) for it in order_data["items"])
    discount_amount = max(0.0, gross_ht - tot_ht)
    vat_rate = float(order_data.get("vat_rate", 20.0))
    vat_amount = round(tot_ht * vat_rate / 100.0, 2)
    tot_ttc = round(tot_ht + vat_amount, 2)

    last_id = db.query(func.max(SalesOrder.id_order)).scalar() or 0
    new_id = last_id + 1
    reference = f"CMD-2026-{new_id:04d}"

    quote_id = order_data.get("quote_id")
    quote_ref_in_order = None
    if quote_id:
        q = db.query(SalesQuote).filter(SalesQuote.id_quote == quote_id).first()
        if q:
            quote_ref_in_order = q.reference
            if q.status != "ACCEPTE":
                q.status = "ACCEPTE"
                q.accepted_date = datetime.now(timezone.utc).date()
                q.updated_at = datetime.now(timezone.utc)

    obj = SalesOrder(
        reference=reference,
        quote_id=quote_id,
        customer_id=cust.id_customer,
        customer_name=cust.name,
        items_json=json.dumps(items_detail, ensure_ascii=False),
        total_ht=round(tot_ht, 2),
        vat_rate=vat_rate,
        vat_amount=vat_amount,
        total_ttc=tot_ttc,
        discount_percent=round((discount_amount / gross_ht) * 100, 2) if gross_ht else 0.0,
        status="VALIDEE",
        order_date=datetime.now(timezone.utc),
        expected_delivery_date=order_data.get("expected_delivery_date"),
        shipping_address=order_data.get("shipping_address"),
        billing_address=order_data.get("billing_address"),
        notes=order_data.get("comment") or order_data.get("notes"),
        created_by_user_id=getattr(actor_user, "id_user", None) if actor_user else order_data.get("created_by_user_id"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(obj)

    cust.total_revenue_generated = (cust.total_revenue_generated or 0.0) + tot_ttc
    cust.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(obj)

    if actor_user is not None:
        try:
            log_action(
                db,
                action="CREATE",
                module="VENTES",
                user_id=getattr(actor_user, "id_user", None),
                username=getattr(actor_user, "username", "SYSTEM"),
                user_role=getattr(actor_user, "role", None),
                target_entity=f"Commande {reference}",
                details=f"Commande client #{cust.id_customer} - Montant TTC: {tot_ttc} €",
                new_values=_serialize_order(obj),
            )
        except Exception as ae:
            logger.warning(f"Audit log create_sales_order: {ae}")

    return _serialize_order(obj)


def update_sales_order_status(
    db: Session,
    order_id: int,
    new_status: str,
    actor_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Mise à jour du statut d'une commande (VALIDEE, LIVREE, ANNULEE, etc.)."""
    obj = db.query(SalesOrder).filter(SalesOrder.id_order == order_id).first()
    if not obj:
        raise RuntimeError(f"Commande #{order_id} non trouvée.")

    old = _serialize_order(obj)

    valid_statuses = ["BROUILLON", "CONFIRMEE", "EN_PREPARATION", "LIVREE", "ANNULEE", "VALIDEE", "EN_LIVRAISON", "FACTUREE"]
    if new_status not in valid_statuses:
        logger.warning(f"Statut commande hors liste standard: {new_status}")
    obj.status = new_status

    if new_status == "ANNULEE":
        pass
    elif new_status in ["VALIDEE", "LIVREE", "CONFIRMEE", "FACTUREE"]:
        if new_status == "LIVREE":
            obj.actual_delivery_date = datetime.now(timezone.utc)

    obj.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(obj)

    if actor_user is not None:
        try:
            log_action(
                db,
                action="UPDATE",
                module="VENTES",
                user_id=getattr(actor_user, "id_user", None),
                username=getattr(actor_user, "username", "SYSTEM"),
                user_role=getattr(actor_user, "role", None),
                target_entity=f"Commande {obj.reference}",
                details=f"Statut commande -> {new_status}",
                old_values=old,
                new_values=_serialize_order(obj),
            )
        except Exception as ae:
            logger.warning(f"Audit log update_sales_order_status: {ae}")

    return _serialize_order(obj)


def get_deliveries(db: Session, actor_user: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Récupère la liste des livraisons."""
    deliveries = db.query(Delivery).order_by(Delivery.created_at.desc()).all()
    return [_serialize_delivery(d) for d in deliveries]


def get_deliveries_by_order(db: Session, order_id: int) -> List[Dict[str, Any]]:
    """Récupère les livraisons associées à une commande."""
    deliveries = db.query(Delivery).filter(Delivery.order_id == order_id).order_by(Delivery.created_at.desc()).all()
    return [_serialize_delivery(d) for d in deliveries]


def create_delivery(
    db: Session,
    delivery_data: Dict[str, Any],
    actor_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Crée une nouvelle livraison pour une commande."""
    order = db.query(SalesOrder).filter(SalesOrder.id_order == delivery_data["order_id"]).first()
    if not order:
        raise RuntimeError(f"Commande #{delivery_data['order_id']} non trouvée.")

    items = []
    try:
        if order.items_json:
            items = json.loads(order.items_json) if isinstance(order.items_json, str) else order.items_json
    except Exception:
        items = []
    total_qty = 0
    for it in items:
        total_qty += int(float(it.get("quantity", 0)))

    last_id = db.query(func.max(Delivery.id_delivery)).scalar() or 0
    new_id = last_id + 1
    reference = f"LIV-2026-{new_id:04d}"

    obj = Delivery(
        reference=reference,
        order_id=order.id_order,
        order_ref=order.reference,
        customer_name=order.customer_name,
        items_json=json.dumps(items, ensure_ascii=False) if items else None,
        total_quantity=delivery_data.get("total_quantity", total_qty),
        status=delivery_data.get("status", "PREPAREE"),
        delivery_date=delivery_data.get("delivery_date"),
        tracking_number=delivery_data.get("tracking_number"),
        carrier=delivery_data.get("carrier") or delivery_data.get("carrier_name"),
        delivered_by_user_id=getattr(actor_user, "id_user", None) if actor_user else delivery_data.get("delivered_by_user_id"),
        customer_signature=delivery_data.get("customer_signature"),
        notes=delivery_data.get("notes"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(obj)

    if delivery_data.get("status") == "LIVREE" or order.status not in ["LIVREE", "FACTUREE"]:
        if order.status in ["CONFIRMEE", "VALIDEE", "EN_PREPARATION", "EN_LIVRAISON"]:
            if delivery_data.get("status") == "LIVREE":
                order.status = "LIVREE"
                order.actual_delivery_date = datetime.now(timezone.utc)
                order.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(obj)

    if actor_user is not None:
        try:
            log_action(
                db,
                action="CREATE",
                module="VENTES",
                user_id=getattr(actor_user, "id_user", None),
                username=getattr(actor_user, "username", "SYSTEM"),
                user_role=getattr(actor_user, "role", None),
                target_entity=f"Livraison {reference}",
                details=f"Livraison commande {order.reference}",
                new_values=_serialize_delivery(obj),
            )
        except Exception as ae:
            logger.warning(f"Audit log create_delivery: {ae}")

    return _serialize_delivery(obj)


def get_sales_invoices(db: Session, actor_user: Optional[Any] = None) -> List[Dict[str, Any]]:
    """Récupère les factures de vente et règlements clients depuis PostgreSQL."""
    invoices = db.query(SalesInvoice).order_by(SalesInvoice.created_at.desc()).all()
    return [_serialize_invoice(i) for i in invoices]


def get_sales_invoice_by_id(db: Session, invoice_id: int) -> Optional[Dict[str, Any]]:
    i = db.query(SalesInvoice).filter(SalesInvoice.id_invoice == invoice_id).first()
    return _serialize_invoice(i) if i else None


def create_sales_invoice(
    db: Session,
    inv_data: Dict[str, Any],
    actor_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Émission d'une facture de vente basée sur une commande en base PostgreSQL."""
    order = db.query(SalesOrder).filter(SalesOrder.id_order == inv_data["order_id"]).first()
    if not order:
        raise RuntimeError(f"Commande #{inv_data['order_id']} non trouvée.")

    last_id = db.query(func.max(SalesInvoice.id_invoice)).scalar() or 0
    new_id = last_id + 1
    invoice_number = f"FAC-2026-{new_id:04d}"

    today = datetime.now(timezone.utc).date()
    invoice_date_raw = inv_data.get("invoice_date")
    if invoice_date_raw:
        try:
            invoice_date = datetime.fromisoformat(str(invoice_date_raw).replace("Z", "+00:00")).date()
        except ValueError:
            raise RuntimeError("La date de facture est invalide. Utilisez le format AAAA-MM-JJ.")
    else:
        invoice_date = today
    payment_method = inv_data.get("payment_mode") or inv_data.get("payment_method", "VIREMENT")
    amount_paid_default = order.total_ttc if payment_method in ["ESPÈCES", "CB", "ESPECES"] else 0.0
    status_default = "PAYEE" if amount_paid_default >= order.total_ttc else "EMISE"

    obj = SalesInvoice(
        invoice_number=invoice_number,
        order_id=order.id_order,
        order_ref=order.reference,
        customer_id=order.customer_id,
        customer_name=order.customer_name,
        items_json=order.items_json,
        total_ht=order.total_ht,
        vat_rate=order.vat_rate,
        vat_amount=order.vat_amount,
        total_ttc=order.total_ttc,
        discount_percent=order.discount_percent,
        amount_paid=inv_data.get("amount_paid", amount_paid_default),
        status=inv_data.get("status", status_default),
        invoice_date=invoice_date,
        due_date=inv_data.get("due_date") or today + timedelta(days=order.customer.payment_terms_days if order.customer else 30),
        paid_date=invoice_date if (inv_data.get("amount_paid", amount_paid_default) >= order.total_ttc and order.total_ttc > 0) else None,
        payment_method=payment_method,
        payment_ref=inv_data.get("payment_ref"),
        notes=inv_data.get("notes"),
        created_by_user_id=getattr(actor_user, "id_user", None) if actor_user else inv_data.get("created_by_user_id"),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(obj)

    old_order_status = order.status
    if old_order_status not in ["FACTUREE", "LIVREE"]:
        order.status = "FACTUREE"
        order.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(obj)

    if actor_user is not None:
        try:
            log_action(
                db,
                action="CREATE",
                module="VENTES",
                user_id=getattr(actor_user, "id_user", None),
                username=getattr(actor_user, "username", "SYSTEM"),
                user_role=getattr(actor_user, "role", None),
                target_entity=f"Facture {invoice_number}",
                details=f"Facturation commande #{order.id_order} - {order.reference}",
                new_values=_serialize_invoice(obj),
            )
        except Exception as ae:
            logger.warning(f"Audit log create_sales_invoice: {ae}")

    return _serialize_invoice(obj)


def update_invoice_payment(
    db: Session,
    invoice_id: int,
    amount_paid: float,
    payment_method: Optional[str] = None,
    payment_ref: Optional[str] = None,
    actor_user: Optional[Any] = None,
) -> Dict[str, Any]:
    """Enregistre un paiement partiel ou total sur une facture."""
    obj = db.query(SalesInvoice).filter(SalesInvoice.id_invoice == invoice_id).first()
    if not obj:
        raise RuntimeError(f"Facture #{invoice_id} non trouvée.")
    if amount_paid > obj.total_ttc:
        raise ValueError("Le montant payé ne peut pas dépasser le total TTC de la facture.")

    old = _serialize_invoice(obj)
    obj.amount_paid = amount_paid
    if payment_method:
        obj.payment_method = payment_method
    if payment_ref:
        obj.payment_ref = payment_ref
    if obj.amount_paid >= obj.total_ttc and obj.total_ttc > 0:
        obj.status = "PAYEE"
        obj.paid_date = datetime.now(timezone.utc).date()
    elif obj.amount_paid > 0:
        obj.status = "PARTIELLEMENT_PAYEE"
    else:
        obj.status = "EMISE"

    obj.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(obj)

    if actor_user is not None:
        try:
            log_action(
                db,
                action="UPDATE",
                module="VENTES",
                user_id=getattr(actor_user, "id_user", None),
                username=getattr(actor_user, "username", "SYSTEM"),
                user_role=getattr(actor_user, "role", None),
                target_entity=f"Facture {obj.invoice_number}",
                details=f"Paiement facture: {amount_paid} €",
                old_values=old,
                new_values=_serialize_invoice(obj),
            )
        except Exception as ae:
            logger.warning(f"Audit log update_invoice_payment: {ae}")

    return _serialize_invoice(obj)


def get_sales_overview(db: Session, actor_user: Optional[Any] = None) -> Dict[str, Any]:
    """KPIs et synthèse analytique du module Ventes depuis PostgreSQL."""
    total_customers = db.query(func.count(Customer.id_customer)).scalar() or 0
    total_quotes = db.query(func.count(SalesQuote.id_quote)).scalar() or 0
    total_orders = db.query(func.count(SalesOrder.id_order)).scalar() or 0
    total_invoices = db.query(func.count(SalesInvoice.id_invoice)).scalar() or 0

    total_revenue = (
        db.query(func.coalesce(func.sum(SalesInvoice.amount_paid), 0.0)).scalar() or 0.0
    )

    orders_pending = (
        db.query(func.count(SalesOrder.id_order))
        .filter(SalesOrder.status.in_(["BROUILLON", "VALIDEE", "CONFIRMEE", "EN_PREPARATION", "EN_LIVRAISON"]))
        .scalar()
        or 0
    )

    invoices_paid_count = (
        db.query(func.count(SalesInvoice.id_invoice))
        .filter(SalesInvoice.amount_paid >= SalesInvoice.total_ttc)
        .filter(SalesInvoice.total_ttc > 0)
        .scalar()
        or 0
    )
    avg_order_val = round(total_revenue / invoices_paid_count, 2) if invoices_paid_count > 0 else 0.0

    total_quote_value = (
        db.query(func.coalesce(func.sum(SalesQuote.total_ttc), 0.0)).scalar() or 0.0
    )
    quotes_accepted = (
        db.query(func.count(SalesQuote.id_quote))
        .filter(SalesQuote.status.in_(["ACCEPTE"]))
        .scalar()
        or 0
    )

    outstanding_invoices_amount = (
        db.query(
            func.coalesce(
                func.sum(SalesInvoice.total_ttc - SalesInvoice.amount_paid),
                0.0,
            )
        )
        .filter(SalesInvoice.total_ttc > SalesInvoice.amount_paid)
        .scalar()
        or 0.0
    )

    return {
        "total_customers": total_customers,
        "total_revenue": round(float(total_revenue), 2),
        "total_orders_count": total_orders,
        "pending_orders_count": orders_pending,
        "total_quotes_count": total_quotes,
        "average_order_value": avg_order_val,
        "total_invoices_count": total_invoices,
        "invoices_paid_count": invoices_paid_count,
        "total_quote_value": round(float(total_quote_value), 2),
        "quotes_accepted_count": quotes_accepted,
        "outstanding_invoices_amount": round(float(outstanding_invoices_amount), 2),
    }

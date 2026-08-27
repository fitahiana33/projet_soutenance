from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    pass


def init_db():
    """Importe les modèles PostgreSQL puis crée les tables manquantes."""
    from app.models.users.user import User  # noqa: F401
    from app.models.roles.role import Role  # noqa: F401
    from app.models.permissions.permission import Permission  # noqa: F401
    from app.models.authentication.user_role import user_roles  # noqa: F401
    from app.models.authentication.role_permission import role_permissions  # noqa: F401
    from app.models.audit.audit_log import AuditLog  # noqa: F401
    from app.models.hr.holiday import PublicHoliday  # noqa: F401
    from app.models.hr.employee import (  # noqa: F401
        Employee, TimeOffRequest, PayrollEntry, PerformanceEvaluation
    )
    from app.models.hr.recruitment import JobOffer, Candidate  # noqa: F401
    from app.models.system.parameter import SystemParameter  # noqa: F401
    from app.models.system.notification import Notification  # noqa: F401
    from app.models.system.sync_log import SyncLog  # noqa: F401
    from app.models.ai.prediction import AIPrediction  # noqa: F401
    from app.models.ai.anomaly import AIAnomaly  # noqa: F401
    from app.models.ai.recommendation import AIRecommendation  # noqa: F401
    from app.models.ai.simulation import AISimulation  # noqa: F401
    from app.models.ai.snapshot import AnalyticsSnapshot  # noqa: F401
    from app.models.products.product import Product, Category, StockMovement  # noqa: F401
    from app.models.stocks.lots import ProductLot  # noqa: F401
    from app.models.purchases.purchase import (  # noqa: F401
        Supplier, PurchaseRequisition, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, SupplierInvoice
    )
    from app.models.sales.sales import (  # noqa: F401
        Customer, SalesQuote, SalesOrder, SalesOrderLine, Delivery, SalesInvoice
    )

    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

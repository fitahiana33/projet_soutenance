from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.core.database import Base

# Import all models to populate Base.metadata for Alembic migrations
from app.models.users.user import User  # noqa: F401
from app.models.roles.role import Role  # noqa: F401
from app.models.permissions.permission import Permission  # noqa: F401
from app.models.authentication.user_role import user_roles  # noqa: F401
from app.models.authentication.role_permission import role_permissions  # noqa: F401
from app.models.audit.audit_log import AuditLog  # noqa: F401
from app.models.hr.holiday import PublicHoliday  # noqa: F401
from app.models.hr.employee import Employee, TimeOffRequest, PayrollEntry, PerformanceEvaluation  # noqa: F401
from app.models.hr.recruitment import JobOffer, Candidate, CandidateEvaluation, CandidateInterview  # noqa: F401
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
from app.models.purchases.purchase import Supplier, PurchaseRequisition, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, SupplierInvoice  # noqa: F401
from app.models.sales.sales import Customer, SalesQuote, SalesOrder, SalesOrderLine, Delivery, SalesInvoice  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url.replace("%", "%%"))
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

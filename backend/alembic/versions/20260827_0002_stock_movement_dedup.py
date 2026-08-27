"""Add dolibarr_mvt_id, sync_status to stock_movements and uq constraint."""
from alembic import op
import sqlalchemy as sa

revision = "20260827_0002"
down_revision = "20260827_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Colonne dolibarr_mvt_id : nullable, unique (NULL != NULL en SQL donc la contrainte est safe)
    op.add_column(
        "stock_movements",
        sa.Column("dolibarr_mvt_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "stock_movements",
        sa.Column("sync_status", sa.String(20), nullable=False, server_default="SYNCED")
    )
    # Index unique sur dolibarr_mvt_id (exclut les NULLs en PostgreSQL)
    op.create_index(
        "ix_stock_movements_dolibarr_mvt_id",
        "stock_movements",
        ["dolibarr_mvt_id"],
        unique=True,
        postgresql_where=sa.text("dolibarr_mvt_id IS NOT NULL")
    )
    # Index sur reference_doc pour accélérer les lookups d'idempotence
    op.create_index(
        "ix_stock_movements_reference_doc",
        "stock_movements",
        ["reference_doc"],
    )
    # Contrainte d'unicité composite : évite les doublons locaux pour le même document
    # On utilise un index partiel qui exclut les reference_doc NULL
    op.create_index(
        "uq_movement_product_type_ref",
        "stock_movements",
        ["product_id", "movement_type", "reference_doc"],
        unique=True,
        postgresql_where=sa.text("reference_doc IS NOT NULL")
    )


def downgrade() -> None:
    op.drop_index("uq_movement_product_type_ref", table_name="stock_movements")
    op.drop_index("ix_stock_movements_reference_doc", table_name="stock_movements")
    op.drop_index("ix_stock_movements_dolibarr_mvt_id", table_name="stock_movements")
    op.drop_column("stock_movements", "sync_status")
    op.drop_column("stock_movements", "dolibarr_mvt_id")

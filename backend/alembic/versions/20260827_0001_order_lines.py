"""Add normalized sales and purchase order lines."""
from alembic import op
import sqlalchemy as sa

revision = "20260827_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sales_order_lines",
        sa.Column("id_line", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("sales_orders.id_order", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_reference", sa.String(100)),
        sa.Column("product_label", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("discount_percent", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_ht", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index("ix_sales_order_lines_order_id", "sales_order_lines", ["order_id"])
    op.create_index("ix_sales_order_lines_product_id", "sales_order_lines", ["product_id"])
    op.create_table(
        "purchase_order_lines",
        sa.Column("id_line", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("purchase_orders.id_order", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_reference", sa.String(100)),
        sa.Column("product_label", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_ht", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index("ix_purchase_order_lines_order_id", "purchase_order_lines", ["order_id"])
    op.create_index("ix_purchase_order_lines_product_id", "purchase_order_lines", ["product_id"])
    # Reprise des historiques existants avant de supprimer progressivement items_json.
    op.execute(sa.text("""
        INSERT INTO sales_order_lines
            (order_id, product_id, product_reference, product_label, quantity,
             unit_price, discount_percent, total_ht)
        SELECT o.id_order,
               (item->>'product_id')::integer,
               item->>'reference',
               COALESCE(item->>'label', 'Produit'),
               COALESCE((item->>'quantity')::double precision, 0),
               COALESCE((item->>'unit_price')::double precision, 0),
               COALESCE((item->>'discount_percent')::double precision, 0),
               COALESCE((item->>'total_line_ht')::double precision, 0)
        FROM sales_orders o
        CROSS JOIN LATERAL jsonb_array_elements(COALESCE(o.items_json, '[]')::jsonb) item
        WHERE (item->>'product_id') IS NOT NULL
    """))
    op.execute(sa.text("""
        INSERT INTO purchase_order_lines
            (order_id, product_id, product_reference, product_label, quantity, unit_price, total_ht)
        SELECT id_order, product_id, product_ref, product_label, quantity, unit_price, total_amount
        FROM purchase_orders
    """))


def downgrade() -> None:
    op.drop_table("purchase_order_lines")
    op.drop_table("sales_order_lines")

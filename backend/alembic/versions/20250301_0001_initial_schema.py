"""Initial schema — tabelas earthquakes, volcanoes e alerts

Revision ID: 0001
Revises:
Create Date: 2025-03-01 00:00:00.000000 UTC

Esta é a migration inicial que cria toda a estrutura do banco.
Em vez de usar autogenerate, escrevi manualmente para ter controle
total sobre os tipos e índices desde o início.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None   # primeira migration — sem predecessor
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Tabela: earthquakes ───────────────────────────────────
    op.create_table(
        "earthquakes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("usgs_id", sa.String(20), nullable=False),
        sa.Column("magnitude", sa.Float(), nullable=False),
        sa.Column("magnitude_type", sa.String(10), nullable=True),
        sa.Column("place", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at_usgs", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("depth_km", sa.Float(), nullable=True),
        sa.Column("status", sa.String(20), nullable=True),
        sa.Column("tsunami", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("alert", sa.String(10), nullable=True),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("detail_url", sa.String(500), nullable=True),
        sa.Column(
            "created_in_db",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_earthquakes_usgs_id", "earthquakes", ["usgs_id"], unique=True)
    op.create_index("ix_earthquakes_occurred_at", "earthquakes", ["occurred_at"])
    op.create_index("ix_earthquake_mag_time", "earthquakes", ["magnitude", "occurred_at"])
    op.create_index("ix_earthquake_geo", "earthquakes", ["latitude", "longitude"])

    # ── Tabela: volcanoes ─────────────────────────────────────
    op.create_table(
        "volcanoes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("gvp_id", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("subregion", sa.String(100), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("elevation_m", sa.Integer(), nullable=True),
        sa.Column("volcano_type", sa.String(100), nullable=True),
        sa.Column("last_eruption_year", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("activity_level", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("wikipedia_url", sa.String(500), nullable=True),
        sa.Column(
            "created_in_db",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_volcanoes_gvp_id", "volcanoes", ["gvp_id"], unique=True)

    # ── Tabela: alerts ────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "alert_type",
            sa.Enum("earthquake", "volcano", "tsunami", name="alerttype"),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum("low", "medium", "high", "critical", name="alertseverity"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_id", sa.String(50), nullable=False),
        sa.Column("magnitude", sa.Float(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_in_db",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_alerts_alert_type", "alerts", ["alert_type"])
    op.create_index("ix_alerts_severity", "alerts", ["severity"])
    op.create_index("ix_alerts_occurred_at", "alerts", ["occurred_at"])


def downgrade() -> None:
    """Reverte a migration — remove todas as tabelas criadas."""
    op.drop_table("alerts")
    op.drop_table("volcanoes")
    op.drop_table("earthquakes")

    # Remove os tipos ENUM do PostgreSQL
    op.execute("DROP TYPE IF EXISTS alerttype")
    op.execute("DROP TYPE IF EXISTS alertseverity")

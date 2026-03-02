"""Remove frequency_per_day column

Revision ID: 0005
Revises: 0004
Create Date: 2024-12-19 15:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Drop the frequency_per_day column from drug_schedules table."""
    op.drop_column("drug_schedules", "frequency_per_day")


def downgrade() -> None:
    """Add back the frequency_per_day column."""
    import sqlalchemy as sa
    from sqlalchemy import Integer

    op.add_column(
        "drug_schedules",
        sa.Column("frequency_per_day", Integer(), nullable=False, server_default="1"),
    )

"""Remove meal_timing column and use signed meal_offset_minutes

Revision ID: 0004
Revises: 0003
Create Date: 2024-12-19 14:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Convert meal_timing + meal_offset_minutes to signed meal_offset_minutes, then drop meal_timing column."""
    connection = op.get_bind()

    # Convert existing data: if meal_timing is 'before', make meal_offset_minutes negative
    # If meal_timing is 'after' or NULL, keep meal_offset_minutes positive
    connection.execute(
        text(
            """
            UPDATE drug_schedules
            SET meal_offset_minutes =
                CASE
                    WHEN meal_timing = 'before' AND meal_offset_minutes > 0
                    THEN -meal_offset_minutes
                    WHEN meal_timing = 'after' AND meal_offset_minutes < 0
                    THEN ABS(meal_offset_minutes)
                    ELSE meal_offset_minutes
                END
            WHERE meal_offset_minutes IS NOT NULL
        """
        )
    )
    op.execute("COMMIT")

    # Drop the meal_timing column
    op.drop_column("drug_schedules", "meal_timing")


def downgrade() -> None:
    """Add back meal_timing column and convert signed offsets back to separate fields."""
    # Add the meal_timing column back
    op.add_column(
        "drug_schedules", sa.Column("meal_timing", sa.String(10), nullable=True)
    )

    connection = op.get_bind()

    # Convert signed meal_offset_minutes back to meal_timing + absolute meal_offset_minutes
    connection.execute(
        text(
            """
            UPDATE drug_schedules
            SET
                meal_timing = CASE
                    WHEN meal_offset_minutes < 0 THEN 'before'
                    WHEN meal_offset_minutes > 0 THEN 'after'
                    ELSE NULL
                END,
                meal_offset_minutes = ABS(meal_offset_minutes)
            WHERE meal_offset_minutes IS NOT NULL
        """
        )
    )
    op.execute("COMMIT")

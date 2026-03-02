"""Change depends_on_drug_id to depends_on_schedule_id

Revision ID: 0002
Revises: 0001
Create Date: 2024-12-19 12:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing foreign key constraint on depends_on_drug_id
    op.drop_constraint(
        "drug_schedules_depends_on_drug_id_fkey", "drug_schedules", type_="foreignkey"
    )

    # Drop the old column
    op.drop_column("drug_schedules", "depends_on_drug_id")

    # Add the new column
    op.add_column(
        "drug_schedules",
        sa.Column("depends_on_schedule_id", sa.Integer(), nullable=True),
    )

    # Add the new foreign key constraint pointing to drug_schedules.id (self-referential)
    op.create_foreign_key(
        "drug_schedules_depends_on_schedule_id_fkey",
        "drug_schedules",
        "drug_schedules",
        ["depends_on_schedule_id"],
        ["id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )


def downgrade() -> None:
    # Drop the new foreign key constraint
    op.drop_constraint(
        "drug_schedules_depends_on_schedule_id_fkey",
        "drug_schedules",
        type_="foreignkey",
    )

    # Drop the new column
    op.drop_column("drug_schedules", "depends_on_schedule_id")

    # Add back the old column
    op.add_column(
        "drug_schedules",
        sa.Column("depends_on_drug_id", sa.Integer(), nullable=True),
    )

    # Add back the old foreign key constraint
    op.create_foreign_key(
        "drug_schedules_depends_on_drug_id_fkey",
        "drug_schedules",
        "drugs",
        ["depends_on_drug_id"],
        ["id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )

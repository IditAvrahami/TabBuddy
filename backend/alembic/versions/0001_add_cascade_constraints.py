"""Add CASCADE constraints to foreign keys

Revision ID: 0001
Revises:
Create Date: 2024-10-23 17:30:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing foreign key constraints
    op.drop_constraint(
        "drug_schedules_drug_id_fkey", "drug_schedules", type_="foreignkey"
    )
    op.drop_constraint(
        "drug_schedules_depends_on_drug_id_fkey", "drug_schedules", type_="foreignkey"
    )
    op.drop_constraint(
        "drug_schedules_meal_schedule_id_fkey", "drug_schedules", type_="foreignkey"
    )
    op.drop_constraint(
        "notification_overrides_schedule_id_fkey",
        "notification_overrides",
        type_="foreignkey",
    )

    # Add new foreign key constraints with CASCADE
    op.create_foreign_key(
        "drug_schedules_drug_id_fkey",
        "drug_schedules",
        "drugs",
        ["drug_id"],
        ["id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )

    op.create_foreign_key(
        "drug_schedules_depends_on_drug_id_fkey",
        "drug_schedules",
        "drugs",
        ["depends_on_drug_id"],
        ["id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )

    op.create_foreign_key(
        "drug_schedules_meal_schedule_id_fkey",
        "drug_schedules",
        "meal_schedules",
        ["meal_schedule_id"],
        ["id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )

    op.create_foreign_key(
        "notification_overrides_schedule_id_fkey",
        "notification_overrides",
        "drug_schedules",
        ["schedule_id"],
        ["id"],
        ondelete="CASCADE",
        onupdate="CASCADE",
    )


def downgrade() -> None:
    # Drop CASCADE constraints
    op.drop_constraint(
        "drug_schedules_drug_id_fkey", "drug_schedules", type_="foreignkey"
    )
    op.drop_constraint(
        "drug_schedules_depends_on_drug_id_fkey", "drug_schedules", type_="foreignkey"
    )
    op.drop_constraint(
        "drug_schedules_meal_schedule_id_fkey", "drug_schedules", type_="foreignkey"
    )
    op.drop_constraint(
        "notification_overrides_schedule_id_fkey",
        "notification_overrides",
        type_="foreignkey",
    )

    # Add back original constraints (without CASCADE)
    op.create_foreign_key(
        "drug_schedules_drug_id_fkey", "drug_schedules", "drugs", ["drug_id"], ["id"]
    )

    op.create_foreign_key(
        "drug_schedules_depends_on_drug_id_fkey",
        "drug_schedules",
        "drugs",
        ["depends_on_drug_id"],
        ["id"],
    )

    op.create_foreign_key(
        "drug_schedules_meal_schedule_id_fkey",
        "drug_schedules",
        "meal_schedules",
        ["meal_schedule_id"],
        ["id"],
    )

    op.create_foreign_key(
        "notification_overrides_schedule_id_fkey",
        "notification_overrides",
        "drug_schedules",
        ["schedule_id"],
        ["id"],
    )

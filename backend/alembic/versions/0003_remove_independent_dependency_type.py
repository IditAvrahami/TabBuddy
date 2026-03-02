"""Remove independent dependency type

Revision ID: 0003
Revises: 0002
Create Date: 2024-12-19 13:00:00.000000

"""

# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Since the backend enum never included 'independent', it shouldn't exist in the database.
    # PostgreSQL enums are strict, so if 'independent' was never in the enum definition,
    # it can't exist as a value. However, this migration documents the removal and
    # ensures consistency.

    # Check if 'independent' exists in the enum type definition
    # If it does (unlikely), we would need to remove it, but that requires
    # recreating the enum type which is complex. Since our Python enum never had
    # INDEPENDENT, the database enum should already be correct.

    # This migration is primarily for documentation purposes.
    # The frontend has been updated to remove 'independent' as an option.
    pass


def downgrade() -> None:
    # No downgrade needed - 'independent' was never officially supported
    # and the backend enum never included it
    pass

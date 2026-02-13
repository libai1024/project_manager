"""Initial baseline migration

This is a baseline migration that marks the current database state
as the starting point for future migrations. No schema changes are made.

Revision ID: 001_baseline
Revises:
Create Date: 2026-02-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '001_baseline'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is a baseline migration - tables already exist
    # Mark the database as being at this revision without creating tables
    pass


def downgrade() -> None:
    # Baseline migration cannot be downgraded without losing all data
    pass

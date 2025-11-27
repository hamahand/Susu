"""merge_multiple_heads

Revision ID: cfa573da2176
Revises: 20251022_cash_payments, 20251022_add_kyc_fields
Create Date: 2025-10-22 09:54:48.617371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfa573da2176'
down_revision = ('20251022_cash_payments', '20251022_add_kyc_fields')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass


"""create_invitations_table

Revision ID: 20251022_invitations
Revises: 20251022_create_otp
Create Date: 2025-10-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251022_invitations'
down_revision = '20251022_create_otp_codes_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create group_invitations table."""
    op.create_table(
        'group_invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=False),
        sa.Column('invited_by', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', 'EXPIRED', name='invitationstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], )
    )
    op.create_index(op.f('ix_group_invitations_id'), 'group_invitations', ['id'], unique=False)
    op.create_index(op.f('ix_group_invitations_group_id'), 'group_invitations', ['group_id'], unique=False)
    op.create_index(op.f('ix_group_invitations_phone_number'), 'group_invitations', ['phone_number'], unique=False)
    op.create_index(op.f('ix_group_invitations_status'), 'group_invitations', ['status'], unique=False)


def downgrade() -> None:
    """Drop group_invitations table."""
    op.drop_index(op.f('ix_group_invitations_status'), table_name='group_invitations')
    op.drop_index(op.f('ix_group_invitations_phone_number'), table_name='group_invitations')
    op.drop_index(op.f('ix_group_invitations_group_id'), table_name='group_invitations')
    op.drop_index(op.f('ix_group_invitations_id'), table_name='group_invitations')
    op.drop_table('group_invitations')


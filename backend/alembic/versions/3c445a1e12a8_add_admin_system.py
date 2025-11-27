"""add_admin_system

Revision ID: 3c445a1e12a8
Revises: fb2618dd1dd4
Create Date: 2025-10-22 10:19:23.296542

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c445a1e12a8'
down_revision = 'fb2618dd1dd4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create admin_role enum type
    admin_role_enum = sa.Enum('super_admin', 'finance_admin', 'support_admin', name='adminrole')
    admin_role_enum.create(op.get_bind(), checkfirst=True)
    
    # Add system admin fields to users table
    op.add_column('users', sa.Column('is_system_admin', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('admin_role', admin_role_enum, nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    
    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('setting_key', sa.String(), nullable=False),
        sa.Column('setting_value', sa.Text(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_settings_category'), 'system_settings', ['category'], unique=False)
    op.create_index(op.f('ix_system_settings_id'), 'system_settings', ['id'], unique=False)
    op.create_index(op.f('ix_system_settings_setting_key'), 'system_settings', ['setting_key'], unique=True)


def downgrade() -> None:
    # Drop system_settings table
    op.drop_index(op.f('ix_system_settings_setting_key'), table_name='system_settings')
    op.drop_index(op.f('ix_system_settings_id'), table_name='system_settings')
    op.drop_index(op.f('ix_system_settings_category'), table_name='system_settings')
    op.drop_table('system_settings')
    
    # Remove admin fields from users table
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'admin_role')
    op.drop_column('users', 'is_system_admin')
    
    # Drop admin_role enum type
    admin_role_enum = sa.Enum('super_admin', 'finance_admin', 'support_admin', name='adminrole')
    admin_role_enum.drop(op.get_bind(), checkfirst=True)


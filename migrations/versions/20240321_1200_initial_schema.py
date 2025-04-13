"""initial schema

Revision ID: 20240321_1200
Revises: 
Create Date: 2024-03-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240321_1200'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('address', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'))
    )

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('order_number', sa.String(20), unique=True, nullable=False),
        sa.Column('customer_id', sa.String(36), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('items', sa.JSON, nullable=False),
        sa.Column('total_amount', sa.Float, nullable=False),
        sa.Column('shipping_address', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'))
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('customer_id', sa.String(36), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('direction', sa.String(10), nullable=False),  # 'incoming' or 'outgoing'
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # Create indexes
    op.create_index('ix_customers_phone', 'customers', ['phone'])
    op.create_index('ix_customers_email', 'customers', ['email'])
    op.create_index('ix_orders_order_number', 'orders', ['order_number'])
    op.create_index('ix_orders_customer_id', 'orders', ['customer_id'])
    op.create_index('ix_messages_customer_id', 'messages', ['customer_id'])

def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_messages_customer_id')
    op.drop_index('ix_orders_customer_id')
    op.drop_index('ix_orders_order_number')
    op.drop_index('ix_customers_email')
    op.drop_index('ix_customers_phone')

    # Drop tables
    op.drop_table('messages')
    op.drop_table('orders')
    op.drop_table('customers') 
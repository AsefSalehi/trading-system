"""Add trading system tables

Revision ID: e3576b2b0b11
Revises: bbfbcd806ceb
Create Date: 2025-09-03 04:11:25.593412

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e3576b2b0b11'
down_revision = 'bbfbcd806ceb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    transaction_type_enum = postgresql.ENUM('buy', 'sell', 'deposit', 'withdrawal', name='transactiontype')
    transaction_type_enum.create(op.get_bind())
    
    order_status_enum = postgresql.ENUM('pending', 'executed', 'cancelled', 'partial', name='orderstatus')
    order_status_enum.create(op.get_bind())
    
    order_type_enum = postgresql.ENUM('market', 'limit', 'stop_loss', 'take_profit', name='ordertype')
    order_type_enum.create(op.get_bind())
    
    # Create wallets table
    op.create_table('wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('usd_balance', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('total_invested', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('total_profit_loss', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('total_portfolio_value', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('daily_pnl', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('total_trades', sa.Integer(), nullable=False),
        sa.Column('winning_trades', sa.Integer(), nullable=False),
        sa.Column('losing_trades', sa.Integer(), nullable=False),
        sa.Column('max_drawdown', sa.DECIMAL(precision=8, scale=4), nullable=False),
        sa.Column('win_rate', sa.DECIMAL(precision=8, scale=4), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_wallets_id'), 'wallets', ['id'], unique=False)
    
    # Create holdings table
    op.create_table('holdings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=False),
        sa.Column('cryptocurrency_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('average_buy_price', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('current_price', sa.DECIMAL(precision=20, scale=8), nullable=True),
        sa.Column('total_cost', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('current_value', sa.DECIMAL(precision=20, scale=8), nullable=True),
        sa.Column('unrealized_pnl', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('unrealized_pnl_percentage', sa.DECIMAL(precision=8, scale=4), nullable=False),
        sa.Column('first_purchase_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['cryptocurrency_id'], ['cryptocurrencies.id'], ),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_holdings_id'), 'holdings', ['id'], unique=False)
    op.create_index(op.f('ix_holdings_symbol'), 'holdings', ['symbol'], unique=False)
    
    # Create transactions table
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=False),
        sa.Column('cryptocurrency_id', sa.Integer(), nullable=True),
        sa.Column('transaction_type', transaction_type_enum, nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=True),
        sa.Column('quantity', sa.DECIMAL(precision=20, scale=8), nullable=True),
        sa.Column('price', sa.DECIMAL(precision=20, scale=8), nullable=True),
        sa.Column('total_amount', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('fee', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('fee_percentage', sa.DECIMAL(precision=8, scale=4), nullable=False),
        sa.Column('realized_pnl', sa.DECIMAL(precision=20, scale=8), nullable=True),
        sa.Column('realized_pnl_percentage', sa.DECIMAL(precision=8, scale=4), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['cryptocurrency_id'], ['cryptocurrencies.id'], ),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_symbol'), 'transactions', ['symbol'], unique=False)
    
    # Create orders table
    op.create_table('orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('wallet_id', sa.Integer(), nullable=False),
        sa.Column('cryptocurrency_id', sa.Integer(), nullable=False),
        sa.Column('order_type', order_type_enum, nullable=False),
        sa.Column('transaction_type', transaction_type_enum, nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('executed_quantity', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('price', sa.DECIMAL(precision=20, scale=8), nullable=True),
        sa.Column('executed_price', sa.DECIMAL(precision=20, scale=8), nullable=True),
        sa.Column('status', order_status_enum, nullable=False),
        sa.Column('total_amount', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('fee', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('stop_price', sa.DECIMAL(precision=20, scale=8), nullable=True),
        sa.Column('trigger_price', sa.DECIMAL(precision=20, scale=8), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['cryptocurrency_id'], ['cryptocurrencies.id'], ),
        sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index(op.f('ix_orders_symbol'), 'orders', ['symbol'], unique=False)
    
    # Create trading_sessions table
    op.create_table('trading_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_name', sa.String(length=100), nullable=False),
        sa.Column('starting_balance', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('current_balance', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('total_pnl', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('total_pnl_percentage', sa.DECIMAL(precision=8, scale=4), nullable=False),
        sa.Column('max_balance', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('min_balance', sa.DECIMAL(precision=20, scale=8), nullable=False),
        sa.Column('total_trades', sa.Integer(), nullable=False),
        sa.Column('winning_trades', sa.Integer(), nullable=False),
        sa.Column('losing_trades', sa.Integer(), nullable=False),
        sa.Column('win_rate', sa.DECIMAL(precision=8, scale=4), nullable=False),
        sa.Column('max_drawdown', sa.DECIMAL(precision=8, scale=4), nullable=False),
        sa.Column('sharpe_ratio', sa.DECIMAL(precision=8, scale=4), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trading_sessions_id'), 'trading_sessions', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_trading_sessions_id'), table_name='trading_sessions')
    op.drop_table('trading_sessions')
    op.drop_index(op.f('ix_orders_symbol'), table_name='orders')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_transactions_symbol'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_holdings_symbol'), table_name='holdings')
    op.drop_index(op.f('ix_holdings_id'), table_name='holdings')
    op.drop_table('holdings')
    op.drop_index(op.f('ix_wallets_id'), table_name='wallets')
    op.drop_table('wallets')
    
    # Drop enums
    transaction_type_enum = postgresql.ENUM('buy', 'sell', 'deposit', 'withdrawal', name='transactiontype')
    transaction_type_enum.drop(op.get_bind())
    order_status_enum = postgresql.ENUM('pending', 'executed', 'cancelled', 'partial', name='orderstatus')
    order_status_enum.drop(op.get_bind())
    order_type_enum = postgresql.ENUM('market', 'limit', 'stop_loss', 'take_profit', name='ordertype')
    order_type_enum.drop(op.get_bind())
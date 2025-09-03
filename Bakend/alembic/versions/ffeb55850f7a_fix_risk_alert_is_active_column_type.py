"""fix_risk_alert_is_active_column_type

Revision ID: ffeb55850f7a
Revises: b5dcf76b4290
Create Date: 2025-09-03 18:21:05.604666

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffeb55850f7a'
down_revision = 'b5dcf76b4290'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert is_active column from VARCHAR to BOOLEAN
    # First, update any existing string values to boolean equivalents
    op.execute("UPDATE risk_alerts SET is_active = 'true' WHERE is_active = 'True' OR is_active = '1' OR is_active = 'true'")
    op.execute("UPDATE risk_alerts SET is_active = 'false' WHERE is_active = 'False' OR is_active = '0' OR is_active = 'false'")
    
    # Alter column type to BOOLEAN
    op.alter_column('risk_alerts', 'is_active',
                    existing_type=sa.VARCHAR(),
                    type_=sa.Boolean(),
                    existing_nullable=False,
                    postgresql_using='is_active::boolean')


def downgrade() -> None:
    # Convert back to VARCHAR
    op.alter_column('risk_alerts', 'is_active',
                    existing_type=sa.Boolean(),
                    type_=sa.VARCHAR(),
                    existing_nullable=False)
"""Add back_populates relationship between Booking and Service

Revision ID: 0e14552a5e33
Revises: eaa2b049a1b4
Create Date: 2025-05-10 15:04:11.642874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e14552a5e33'
down_revision: Union[str, None] = 'eaa2b049a1b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('services', 'description',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=True)
    op.drop_index('ix_services_category', table_name='services')
    op.drop_index('ix_services_name', table_name='services')
    op.drop_constraint('services_career_type_id_fkey', 'services', type_='foreignkey')
    op.drop_column('services', 'currency')
    op.drop_column('services', 'career_type_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('services', sa.Column('career_type_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('services', sa.Column('currency', sa.VARCHAR(length=3), server_default=sa.text("'USD'::character varying"), autoincrement=False, nullable=True))
    op.create_foreign_key('services_career_type_id_fkey', 'services', 'career_types', ['career_type_id'], ['id'])
    op.create_index('ix_services_name', 'services', ['name'], unique=False)
    op.create_index('ix_services_category', 'services', ['category'], unique=False)
    op.alter_column('services', 'description',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    # ### end Alembic commands ###

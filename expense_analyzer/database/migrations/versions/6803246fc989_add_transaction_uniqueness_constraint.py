"""add transaction uniqueness constraint

Revision ID: 6803246fc989
Revises: 5fa38fda2f87
Create Date: 2025-03-18 16:09:10.406615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6803246fc989'
down_revision: Union[str, None] = '5fa38fda2f87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_categories_name', table_name='categories')
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_unique_constraint('uix_category_name_parent', 'categories', ['name', 'parent_id'])
    op.create_unique_constraint('uix_transaction_unique', 'transactions', ['date', 'amount', 'vendor', 'description'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uix_transaction_unique', 'transactions', type_='unique')
    op.drop_constraint('uix_category_name_parent', 'categories', type_='unique')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.create_index('ix_categories_name', 'categories', ['name'], unique=True)
    # ### end Alembic commands ###

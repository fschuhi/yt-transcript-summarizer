"""Migration

Revision ID: 2fbcf1b8fad2
Revises: f517287df8b0
Create Date: 2024-08-10 06:47:03.295778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fbcf1b8fad2'
down_revision: Union[str, None] = 'f517287df8b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('token_issuance_date', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.String(length=100), nullable=False))
    op.add_column('users', sa.Column('identity_provider', sa.String(length=30), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'identity_provider')
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'token_issuance_date')
    # ### end Alembic commands ###
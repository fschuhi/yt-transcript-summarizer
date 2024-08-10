"""Migration

Revision ID: 8ff1f1bc5f08
Revises: 2fbcf1b8fad2
Create Date: 2024-08-10 08:44:56.601232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ff1f1bc5f08'
down_revision: Union[str, None] = '2fbcf1b8fad2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user_name', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_users_user_name'), 'users', ['user_name'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_user_name'), table_name='users')
    op.drop_column('users', 'user_name')
    # ### end Alembic commands ###

"""Migration

Revision ID: 5a18f8d457f1
Revises: 8ff1f1bc5f08
Create Date: 2024-08-10 13:14:10.059156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a18f8d457f1'
down_revision: Union[str, None] = '8ff1f1bc5f08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
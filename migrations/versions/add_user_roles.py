"""add user roles

Revision ID: add_user_roles
Revises: 
Create Date: 2024-03-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_user_roles'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type
    op.execute("CREATE TYPE userrole AS ENUM ('user', 'admin')")
    
    # Add role column with default value 'user'
    op.add_column('users', sa.Column('role', postgresql.ENUM('user', 'admin', name='userrole'), server_default='user', nullable=False))
    
    # Update existing users to have 'user' role
    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")


def downgrade() -> None:
    # Remove role column
    op.drop_column('users', 'role')
    
    # Drop enum type
    op.execute('DROP TYPE userrole') 
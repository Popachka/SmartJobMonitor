\
\
\
\
\
\
   
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

                                        
revision: str = 'cb0a0beda94c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
                         
                                                                 
    op.create_table('raw_vacancies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source', sa.String(length=255), nullable=False),
    sa.Column('raw_text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vacancies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('raw_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('tech_stack', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.ForeignKeyConstraint(['raw_id'], ['raw_vacancies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
                                  


def downgrade() -> None:
                           
                                                                 
    op.drop_table('vacancies')
    op.drop_table('raw_vacancies')
                                  

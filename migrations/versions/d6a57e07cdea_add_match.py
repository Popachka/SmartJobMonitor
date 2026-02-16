\
\
\
\
\
\
   
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


                                        
revision: str = 'd6a57e07cdea'
down_revision: Union[str, Sequence[str], None] = '82f0acbc75e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
                         
                                                                 
    op.create_table('vacancy_matches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vacancy_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['vacancy_id'], ['vacancies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
                                  


def downgrade() -> None:
                           
                                                                 
    op.drop_table('vacancy_matches')
                                  

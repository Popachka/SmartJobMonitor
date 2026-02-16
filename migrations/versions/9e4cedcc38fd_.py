\
\
\
\
\
\
   
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


                                        
revision: str = '9e4cedcc38fd'
down_revision: Union[str, Sequence[str], None] = 'b8f838cc6b3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
                         
                                                                 
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('text_resume', sa.Text(), nullable=True),
    sa.Column('tech_stack', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tg_id')
    )
                                  


def downgrade() -> None:
                           
                                                                 
    op.drop_table('users')
                                  

\
\
\
\
\
\
   
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


                                        
revision: str = '3a1007d2d014'
down_revision: Union[str, Sequence[str], None] = 'd6a57e07cdea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
                         
                                                                 
    op.drop_column('vacancy_matches', 'reason')
                                  


def downgrade() -> None:
                           
                                                                 
    op.add_column('vacancy_matches', sa.Column('reason', sa.TEXT(), autoincrement=False, nullable=False))
                                  

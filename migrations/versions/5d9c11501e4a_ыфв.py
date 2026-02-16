\
\
\
\
\
\
   
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


                                        
revision: str = '5d9c11501e4a'
down_revision: Union[str, Sequence[str], None] = '9e4cedcc38fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
                         
                                                                 
    op.add_column('users', sa.Column('primary_language', sa.String(), nullable=True))
                                  


def downgrade() -> None:
                           
                                                                 
    op.drop_column('users', 'primary_language')
                                  

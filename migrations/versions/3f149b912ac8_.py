\
\
\
\
\
\
   
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


                                        
revision: str = '3f149b912ac8'
down_revision: Union[str, Sequence[str], None] = '31ccfc502e51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
                         
                                                                 
    op.drop_column('raw_vacancies', 'source')
                                  


def downgrade() -> None:
                           
                                                                 
    op.add_column('raw_vacancies', sa.Column('source', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
                                  

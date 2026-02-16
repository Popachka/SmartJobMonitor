\
\
\
\
\
\
   
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


                                        
revision: str = '31ccfc502e51'
down_revision: Union[str, Sequence[str], None] = '1ca1aaca3f85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
                         
                                                                 
    op.add_column('raw_vacancies', sa.Column('chat_id', sa.BigInteger(), nullable=True))
    op.add_column('raw_vacancies', sa.Column('message_id', sa.BigInteger(), nullable=True))
                                  


def downgrade() -> None:
                           
                                                                 
    op.drop_column('raw_vacancies', 'message_id')
    op.drop_column('raw_vacancies', 'chat_id')
                                  

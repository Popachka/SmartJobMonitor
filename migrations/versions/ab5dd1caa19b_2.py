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

                                        
revision: str = 'ab5dd1caa19b'
down_revision: Union[str, Sequence[str], None] = '3a1007d2d014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
                         
                                                                 
    op.add_column('users', sa.Column('specializations', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('users', sa.Column('primary_languages', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('users', sa.Column('experience_months', sa.Integer(), nullable=False))
    op.drop_column('users', 'main_programming_language')
    op.add_column('vacancies', sa.Column('specializations', postgresql.JSONB(astext_type=sa.Text()), nullable=False))
    op.add_column('vacancies', sa.Column('primary_languages', postgresql.JSONB(astext_type=sa.Text()), nullable=False))
    op.add_column('vacancies', sa.Column('min_experience_months', sa.Integer(), nullable=False))
    op.drop_column('vacancies', 'main_programming_language')
                                  


def downgrade() -> None:
                           
                                                                 
    op.add_column('vacancies', sa.Column('main_programming_language', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.drop_column('vacancies', 'min_experience_months')
    op.drop_column('vacancies', 'primary_languages')
    op.drop_column('vacancies', 'specializations')
    op.add_column('users', sa.Column('main_programming_language', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('users', 'experience_months')
    op.drop_column('users', 'primary_languages')
    op.drop_column('users', 'specializations')
                                  

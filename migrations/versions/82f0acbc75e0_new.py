"""new

Revision ID: 82f0acbc75e0
Revises: 5d9c11501e4a
Create Date: 2026-02-10 17:53:57.545627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '82f0acbc75e0'
down_revision: Union[str, Sequence[str], None] = '5d9c11501e4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Сначала удаляем связь, чтобы избежать DependentObjectsStillExistError
    # Используем if_exists=True нет в Alembic по умолчанию, поэтому просто один вызов вручную
    op.drop_constraint('vacancies_raw_id_fkey', 'vacancies', type_='foreignkey')
    op.drop_table('raw_vacancies')
    # 3. Обновляем юзеров
    op.add_column('users', sa.Column('main_programming_language', sa.String(), nullable=True))
    op.alter_column('users', 'tech_stack',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               type_=postgresql.JSONB(astext_type=sa.Text()),
               existing_nullable=True)
    op.drop_column('users', 'primary_language')

# 2. Добавляем колонку 'text' как nullable
    op.add_column('vacancies', sa.Column('text', sa.Text(), nullable=True))
    # Заполняем существующие строки заглушкой
    op.execute("UPDATE vacancies SET text = 'No content' WHERE text IS NULL")
    # Теперь ставим NOT NULL
    op.alter_column('vacancies', 'text', nullable=False)

    # 3. Аналогично для mirror_chat_id и mirror_message_id, если там тоже NOT NULL
    op.add_column('vacancies', sa.Column('mirror_chat_id', sa.BigInteger(), nullable=True))
    op.execute("UPDATE vacancies SET mirror_chat_id = 0 WHERE mirror_chat_id IS NULL")
    op.alter_column('vacancies', 'mirror_chat_id', nullable=False)

    op.add_column('vacancies', sa.Column('mirror_message_id', sa.BigInteger(), nullable=True))
    op.execute("UPDATE vacancies SET mirror_message_id = 0 WHERE mirror_message_id IS NULL")
    op.alter_column('vacancies', 'mirror_message_id', nullable=False)

    # Остальное
    op.add_column('vacancies', sa.Column('main_programming_language', sa.String(length=100), nullable=True))
    op.drop_column('vacancies', 'title')
    op.drop_column('vacancies', 'raw_id')


def downgrade() -> None:
    # 1. Сначала создаем таблицу, чтобы на нее можно было сослаться
    op.create_table('raw_vacancies',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('raw_text', sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('now()'), autoincrement=False, nullable=False),
        sa.Column('status', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('chat_id', sa.BIGINT(), autoincrement=False, nullable=True),
        sa.Column('message_id', sa.BIGINT(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='raw_vacancies_pkey')
    )

    # 2. Возвращаем старые колонки в вакансии
    op.add_column('vacancies', sa.Column('raw_id', sa.INTEGER(), autoincrement=False, nullable=True)) # nullable=True для безопасности
    op.add_column('vacancies', sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=True))

    # 3. Создаем внешний ключ ОБРАТНО
    op.create_foreign_key('vacancies_raw_id_fkey', 'vacancies', 'raw_vacancies', ['raw_id'], ['id'])

    # 4. Удаляем новые колонки
    op.drop_column('vacancies', 'mirror_message_id')
    op.drop_column('vacancies', 'mirror_chat_id')
    op.drop_column('vacancies', 'main_programming_language')
    op.drop_column('vacancies', 'text')

    # 5. Возвращаем юзеров
    op.add_column('users', sa.Column('primary_language', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.alter_column('users', 'tech_stack',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=postgresql.JSON(astext_type=sa.Text()),
               existing_nullable=True)
    op.drop_column('users', 'main_programming_language')
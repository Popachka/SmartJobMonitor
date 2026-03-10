"""replace languages with skills

Revision ID: b1a2c3d4e5f6
Revises: 89d7ab44d1f2
Create Date: 2026-03-10 13:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1a2c3d4e5f6"
down_revision: str | Sequence[str] | None = "89d7ab44d1f2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "vacancies",
        sa.Column(
            "skills",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "cv_skills",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.execute(
        """
        UPDATE vacancies
        SET skills = COALESCE(
            (
                SELECT jsonb_agg(skill ORDER BY skill)
                FROM (
                    SELECT DISTINCT CASE lower(value)
                        WHEN 'python' THEN 'Python'
                        WHEN 'javascript' THEN 'JavaScript'
                        WHEN 'react' THEN 'React'
                        WHEN 'vue' THEN 'Vue'
                        ELSE NULL
                    END AS skill
                    FROM jsonb_array_elements_text(
                        COALESCE(primary_languages, '[]'::jsonb) || COALESCE(tech_stack, '[]'::jsonb)
                    ) AS value
                ) normalized
                WHERE skill IS NOT NULL
            ),
            '[]'::jsonb
        )
        """
    )
    op.execute(
        """
        UPDATE users
        SET cv_skills = COALESCE(
            (
                SELECT jsonb_agg(skill ORDER BY skill)
                FROM (
                    SELECT DISTINCT CASE lower(value)
                        WHEN 'python' THEN 'Python'
                        WHEN 'javascript' THEN 'JavaScript'
                        WHEN 'react' THEN 'React'
                        WHEN 'vue' THEN 'Vue'
                        ELSE NULL
                    END AS skill
                    FROM jsonb_array_elements_text(
                        COALESCE(cv_primary_languages, '[]'::jsonb) || COALESCE(COALESCE(cv_tech_stack, '[]'::jsonb), '[]'::jsonb)
                    ) AS value
                ) normalized
                WHERE skill IS NOT NULL
            ),
            '[]'::jsonb
        )
        """
    )

    op.alter_column("vacancies", "skills", server_default=None)
    op.alter_column("users", "cv_skills", server_default=None)

    op.drop_column("vacancies", "primary_languages")
    op.drop_column("vacancies", "tech_stack")
    op.drop_column("users", "cv_primary_languages")
    op.drop_column("users", "cv_tech_stack")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "vacancies",
        sa.Column(
            "primary_languages",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "vacancies",
        sa.Column(
            "tech_stack",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "cv_primary_languages",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "cv_tech_stack",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    op.execute("UPDATE vacancies SET primary_languages = COALESCE(skills, '[]'::jsonb)")
    op.execute("UPDATE vacancies SET tech_stack = '[]'::jsonb")
    op.execute("UPDATE users SET cv_primary_languages = COALESCE(cv_skills, '[]'::jsonb)")
    op.execute("UPDATE users SET cv_tech_stack = NULL")

    op.alter_column("vacancies", "primary_languages", server_default=None)
    op.alter_column("vacancies", "tech_stack", server_default=None)
    op.alter_column("users", "cv_primary_languages", server_default=None)

    op.drop_column("vacancies", "skills")
    op.drop_column("users", "cv_skills")

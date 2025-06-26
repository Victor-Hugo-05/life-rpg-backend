"""Renomeando Carisma para Saúde

Revision ID: 83d5cea448e6
Revises: 36a650a4a33e
Create Date: 2025-06-23 18:57:59.757074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83d5cea448e6'
down_revision = '36a650a4a33e'
branch_labels = None
depends_on = None


def upgrade():
    # Alterações na tabela character_attributes
    with op.batch_alter_table('character_attributes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('health_xp', sa.Integer(), nullable=True))
        batch_op.drop_column('charisma_xp')

    # Alterações na tabela character_missions
    with op.batch_alter_table('character_missions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('difficulty', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('health', sa.Boolean(), nullable=True))
        batch_op.drop_column('charisma')

    # Preencher missões existentes com dificuldade padrão "Fácil"
    op.execute("UPDATE character_missions SET difficulty = 'Fácil' WHERE difficulty IS NULL")

    # Alterar a coluna difficulty para NOT NULL depois de populada
    with op.batch_alter_table('character_missions', schema=None) as batch_op:
        batch_op.alter_column('difficulty', nullable=False)

    # Alterações na tabela mission_templates
    with op.batch_alter_table('mission_templates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('difficulty', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('health', sa.Boolean(), nullable=True))
        batch_op.drop_column('charisma')

    # Preencher templates existentes com dificuldade padrão "Fácil"
    op.execute("UPDATE mission_templates SET difficulty = 'Fácil' WHERE difficulty IS NULL")

    # Alterar a coluna difficulty para NOT NULL depois de populada
    with op.batch_alter_table('mission_templates', schema=None) as batch_op:
        batch_op.alter_column('difficulty', nullable=False)


def downgrade():
    # Reverter mission_templates
    with op.batch_alter_table('mission_templates', schema=None) as batch_op:
        batch_op.add_column(sa.Column('charisma', sa.BOOLEAN(), nullable=True))
        batch_op.drop_column('health')
        batch_op.drop_column('difficulty')

    # Reverter character_missions
    with op.batch_alter_table('character_missions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('charisma', sa.BOOLEAN(), nullable=True))
        batch_op.drop_column('health')
        batch_op.drop_column('difficulty')

    # Reverter character_attributes
    with op.batch_alter_table('character_attributes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('charisma_xp', sa.INTEGER(), nullable=True))
        batch_op.drop_column('health_xp')

"""add pgvector extension, documents, and chunks tables

Revision ID: 20240710_add_pgvector_and_memory_tables
Revises: <previous_revision>
Create Date: 2024-07-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240710_add_pgvector_and_memory_tables'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None

def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgvector";')
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String, nullable=False),
        sa.Column('text', sa.Text, nullable=True),
        sa.Column('embedding', postgresql.VECTOR(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_table(
        'chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('chunk_idx', sa.Integer, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('embedding', postgresql.VECTOR(1536), nullable=False),
    )
    op.create_index('ix_chunks_embedding', 'chunks', ['embedding'], postgresql_using='gist')

def downgrade():
    op.drop_index('ix_chunks_embedding', table_name='chunks')
    op.drop_table('chunks')
    op.drop_table('documents')
    op.execute('DROP EXTENSION IF EXISTS "pgvector";')

"""migrate_users_to_personal_workspaces

Revision ID: 5b00c24be077
Revises: 3ec8b3aaa12b
Create Date: 2026-01-08 15:29:23.898686

Migra usuários existentes para workspaces pessoais e calculations para esses workspaces.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b00c24be077'
down_revision: Union[str, Sequence[str], None] = '3ec8b3aaa12b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrate existing users to personal workspaces."""
    
    # 1. Criar workspace pessoal para cada usuário existente
    op.execute("""
        INSERT INTO workspace (name, slug, description, type, owner_id, is_active, created_at, updated_at)
        SELECT 
            'Workspace de ' || COALESCE(username, email),
            'workspace-' || id || '-' || LOWER(REGEXP_REPLACE(COALESCE(username, email), '[^a-zA-Z0-9]', '-', 'g')),
            'Workspace pessoal',
            'personal',
            id,
            true,
            COALESCE(created_at, NOW()),
            NOW()
        FROM "user"
        WHERE NOT EXISTS (
            SELECT 1 FROM workspace WHERE owner_id = "user".id AND type = 'personal'
        )
    """)
    
    # 2. Migrar calculations para o workspace pessoal do owner
    # Prioridade: created_by_user_id > user_id
    op.execute("""
        UPDATE calculation
        SET workspace_id = workspace.id
        FROM workspace
        WHERE workspace.owner_id = COALESCE(calculation.created_by_user_id, calculation.user_id)
          AND workspace.type = 'personal'
          AND calculation.workspace_id IS NULL
    """)
    
    # 3. Para calculations ainda órfãos (edge case), usar o primeiro workspace disponível
    op.execute("""
        UPDATE calculation
        SET workspace_id = (SELECT id FROM workspace WHERE type = 'personal' LIMIT 1)
        WHERE workspace_id IS NULL
    """)
    
    print("✅ Usuários migrados para workspaces pessoais")
    print("✅ Calculations migrados para workspaces respectivos")


def downgrade() -> None:
    """Downgrade: remover workspaces pessoais criados automaticamente."""
    
    # Limpar workspace_id de calculations
    op.execute("""
        UPDATE calculation
        SET workspace_id = NULL
        WHERE workspace_id IN (
            SELECT id FROM workspace WHERE type = 'personal'
        )
    """)
    
    # Remover workspaces pessoais auto-criados
    op.execute("""
        DELETE FROM workspace
        WHERE type = 'personal'
          AND description = 'Workspace pessoal'
    """)
    
    print("⚠️ Workspaces pessoais removidos")

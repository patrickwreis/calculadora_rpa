"""simplify_to_organizations_only

Revision ID: bbbab191b44e
Revises: 
Create Date: 2026-01-08 15:17:01.548943

Simplifica o schema removendo teams e usando apenas organizations.
- Adiciona organization_id na tabela calculation
- Migra team_id → organization_id
- Remove tabelas team e team_member
- Remove team_id de calculation
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbbab191b44e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: simplifica para usar apenas organizations."""
    
    # 1. Adicionar organization_id na tabela calculation (temporariamente nullable)
    op.add_column('calculation', sa.Column('organization_id', sa.Integer(), nullable=True))
    
    # 2. Migrar dados: calculation.organization_id = team.organization_id
    op.execute("""
        UPDATE calculation
        SET organization_id = team.organization_id
        FROM team
        WHERE calculation.team_id = team.id
    """)
    
    # 3. Para calculations órfãos (sem team_id), usar a organização do usuário criador
    op.execute("""
        UPDATE calculation
        SET organization_id = (
            SELECT id FROM organization 
            WHERE created_by_user_id = calculation.created_by_user_id
            LIMIT 1
        )
        WHERE organization_id IS NULL 
        AND created_by_user_id IS NOT NULL
    """)
    
    # 4. Para qualquer calculation ainda órfão, usar a primeira organização disponível
    op.execute("""
        UPDATE calculation
        SET organization_id = (SELECT id FROM organization LIMIT 1)
        WHERE organization_id IS NULL
    """)
    
    # 5. Tornar organization_id NOT NULL e adicionar foreign key
    op.alter_column('calculation', 'organization_id', nullable=False)
    op.create_foreign_key(
        'fk_calculation_organization',
        'calculation', 'organization',
        ['organization_id'], ['id']
    )
    
    # 6. Remover team_id de calculation
    op.drop_constraint('calculation_team_id_fkey', 'calculation', type_='foreignkey')
    op.drop_column('calculation', 'team_id')
    
    # 7. Remover tabela team_member
    op.drop_table('team_member')
    
    # 8. Remover tabela team
    op.drop_table('team')
    
    print("✅ Migration concluída: Schema simplificado para usar apenas Organizations")


def downgrade() -> None:
    """Downgrade schema: restaura teams (requer dados perdidos)."""
    
    # Recriar tabelas team e team_member
    op.create_table(
        'team',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organization.id'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    op.create_table(
        'team_member',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('team_id', sa.Integer(), sa.ForeignKey('team.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='member'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # Adicionar team_id de volta em calculation
    op.add_column('calculation', sa.Column('team_id', sa.Integer(), nullable=True))
    
    # AVISO: Não é possível restaurar dados de team/team_member automaticamente
    # Os usuários precisarão recriar suas teams manualmente
    print("⚠️ ATENÇÃO: Tabelas team/team_member foram recriadas, mas SEM DADOS")
    print("⚠️ calculation.organization_id foi mantido, mas team_id está NULL")
    print("⚠️ Você precisará migrar manualmente ou restaurar um backup")
    
    # Remover organization_id de calculation
    op.drop_constraint('fk_calculation_organization', 'calculation', type_='foreignkey')
    op.drop_column('calculation', 'organization_id')


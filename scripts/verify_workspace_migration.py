"""Script to verify workspace migration"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

print("📊 Verificando workspaces criados...\n")

with engine.connect() as conn:
    # Check workspaces
    result = conn.execute(text("""
        SELECT id, name, type, owner_id 
        FROM workspace 
        ORDER BY id
    """))
    workspaces = result.fetchall()
    
    print(f"✅ {len(workspaces)} workspaces criados:")
    for ws in workspaces:
        print(f"   - ID {ws[0]}: {ws[1]} ({ws[2]}) - owner: {ws[3]}")
    
    # Check calculations with workspace
    result = conn.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(workspace_id) as com_workspace,
            COUNT(*) FILTER (WHERE workspace_id IS NULL) as sem_workspace
        FROM calculation
    """))
    stats = result.fetchone()
    
    print(f"\n📈 Calculations:")
    print(f"   - Total: {stats[0]}")
    print(f"   - Com workspace: {stats[1]}")
    print(f"   - Sem workspace: {stats[2]}")
    
    if stats[2] > 0:
        print(f"\n⚠️ Atenção: {stats[2]} calculations sem workspace!")
    else:
        print(f"\n✅ Todos os calculations têm workspace!")

print("\n✅ Verificação concluída!")

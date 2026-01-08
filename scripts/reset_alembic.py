"""Script to reset Alembic version table"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

# Connect to database
engine = create_engine(DATABASE_URL)

print("🔄 Limpando tabela alembic_version...")

with engine.connect() as conn:
    # Drop and recreate alembic_version table
    conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
    conn.commit()
    print("✅ Tabela alembic_version removida")

print("✅ Alembic resetado - pronto para novas migrations")

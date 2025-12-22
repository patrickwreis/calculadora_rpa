#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para adicionar colunas de session_token à tabela user."""
import sys
from pathlib import Path

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from config import DATABASE_URL
from sqlalchemy import create_engine

def migrate_add_session_token():
    """Adiciona colunas session_token e session_token_expiry."""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        try:
            # Verificar se a coluna já existe
            result = connection.execute(text(
                "PRAGMA table_info(user)"
            ))
            columns = [row[1] for row in result]
            
            if "session_token" not in columns:
                connection.execute(text(
                    "ALTER TABLE user ADD COLUMN session_token VARCHAR(100)"
                ))
                print("✅ Coluna session_token adicionada")
            else:
                print("⚠️ Coluna session_token já existe")
            
            if "session_token_expiry" not in columns:
                connection.execute(text(
                    "ALTER TABLE user ADD COLUMN session_token_expiry DATETIME"
                ))
                print("✅ Coluna session_token_expiry adicionada")
            else:
                print("⚠️ Coluna session_token_expiry já existe")
            
            # Criar índice em session_token
            try:
                connection.execute(text(
                    "CREATE INDEX idx_session_token ON user(session_token)"
                ))
                print("✅ Índice em session_token criado")
            except:
                print("⚠️ Índice em session_token já existe")
            
            connection.commit()
            print("\n✅ Migração concluída com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro durante migração: {str(e)}")
            connection.rollback()
            raise

if __name__ == "__main__":
    migrate_add_session_token()

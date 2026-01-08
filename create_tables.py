#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initialize database tables for Neon PostgreSQL.

Run this script once after setting up your DATABASE_URL in .env:
    python create_tables.py
"""
from sqlalchemy import create_engine
from sqlmodel import SQLModel
from config.settings import DATABASE_URL
from src.models import User, Calculation


def create_tables():
    """Create all tables in the database."""
    try:
        engine = create_engine(DATABASE_URL)
        SQLModel.metadata.create_all(engine)
        print("✓ Tabelas criadas com sucesso no banco de dados!")
    except Exception as e:
        print(f"✗ Erro ao criar tabelas: {e}")
        raise


if __name__ == "__main__":
    create_tables()

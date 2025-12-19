# -*- coding: utf-8 -*-
"""SQLModel base configuration with shared registry"""
from sqlmodel import SQLModel as _SQLModel
from sqlalchemy.orm import registry

# Create a single, reusable registry
_registry = registry()


class SQLModel(_SQLModel, registry=_registry):
    """Base SQLModel class with shared registry to avoid redefinition errors"""
    pass

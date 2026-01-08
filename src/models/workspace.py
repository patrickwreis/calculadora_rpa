# -*- coding: utf-8 -*-
"""Workspace models for SaaS-style multi-tenancy"""
from datetime import datetime
from sqlmodel import Field
from typing import Optional, Literal
from src.database.base import SQLModel


if "Workspace" not in globals():
    class Workspace(SQLModel, table=True):
        """
        Workspace model - can be personal or shared.
        
        Personal workspaces:
        - Auto-created on user signup
        - One per user
        - Only the owner can see/edit
        - Name: "Workspace de [Nome]"
        
        Shared workspaces:
        - Created manually by users
        - Multiple members with roles
        - Used for collaboration (teams, clients, projects)
        """
        __tablename__ = "workspace"
        __table_args__ = {"extend_existing": True}
        
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str = Field(index=True)
        slug: str = Field(unique=True, index=True)
        description: Optional[str] = Field(default=None)
        
        # Type: "personal" (default, auto-created) or "shared" (manual, for collaboration)
        type: str = Field(default="personal", index=True)  # "personal" | "shared"
        
        # Owner (creator) - for personal workspaces, this is the user
        owner_id: int = Field(foreign_key="user.id", index=True)
        
        # Soft delete
        is_active: bool = Field(default=True)
        
        # Timestamps
        created_at: datetime = Field(default_factory=datetime.utcnow)
        updated_at: datetime = Field(default_factory=datetime.utcnow)
        
        def __repr__(self):
            return f"Workspace(id={self.id}, name='{self.name}', type='{self.type}', owner={self.owner_id})"


if "WorkspaceMember" not in globals():
    class WorkspaceMember(SQLModel, table=True):
        """
        Association between users and SHARED workspaces.
        
        Note: Personal workspaces don't have members (only owner).
        
        Roles:
        - admin: Can manage members, settings, and all calculations
        - editor: Can create/edit/delete calculations
        - viewer: Read-only access to calculations
        """
        __tablename__ = "workspace_member"
        __table_args__ = {"extend_existing": True}
        
        id: Optional[int] = Field(default=None, primary_key=True)
        workspace_id: int = Field(foreign_key="workspace.id", index=True)
        user_id: int = Field(foreign_key="user.id", index=True)
        
        # Role: "admin" | "editor" | "viewer"
        role: str = Field(default="editor")
        
        # Soft delete
        is_active: bool = Field(default=True)
        
        # Timestamps
        joined_at: datetime = Field(default_factory=datetime.utcnow)
        
        def __repr__(self):
            return f"WorkspaceMember(workspace={self.workspace_id}, user={self.user_id}, role='{self.role}')"

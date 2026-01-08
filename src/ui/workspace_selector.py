# -*- coding: utf-8 -*-
"""Workspace selector component for sidebar"""
import streamlit as st
from typing import Optional
from src.database.db_manager import get_database_manager, DatabaseManager


def render_workspace_selector() -> Optional[int]:
    """
    Render workspace selector in sidebar.
    Shows personal workspace + shared workspaces.
    
    Returns:
        Selected workspace_id or None
    """
    if "auth_user_id" not in st.session_state or st.session_state.auth_user_id is None:
        return None
    
    user_id = st.session_state.auth_user_id
    db = get_database_manager()

    # Fallback para instâncias antigas em cache que não possuam os métodos novos
    if not hasattr(db, "get_user_workspaces"):
        db = DatabaseManager()
    
    # Get all user workspaces
    workspaces = db.get_user_workspaces(user_id)
    
    if not workspaces:
        st.sidebar.warning("⚠️ Você não tem nenhum workspace. Contate o administrador.")
        return None
    
    # Separate personal and shared
    personal_workspaces = [ws for ws in workspaces if ws.type == "personal"]
    shared_workspaces = [ws for ws in workspaces if ws.type == "shared"]
    
    # Initialize active_workspace_id if not set
    if "active_workspace_id" not in st.session_state:
        # Default to personal workspace
        if personal_workspaces:
            st.session_state.active_workspace_id = personal_workspaces[0].id
        elif workspaces:
            st.session_state.active_workspace_id = workspaces[0].id
    
    # Build workspace options
    workspace_options = {}
    
    # Add personal workspace (always first)
    if personal_workspaces:
        for ws in personal_workspaces:
            workspace_options[f"🏠 {ws.name}"] = ws.id
    
    # Add shared workspaces
    if shared_workspaces:
        for ws in shared_workspaces:
            role = db.get_user_role_in_workspace(ws.id, user_id)
            emoji = "👑" if role == "owner" else "📁"
            workspace_options[f"{emoji} {ws.name}"] = ws.id
    
    # Find current selection
    current_ws_id = st.session_state.active_workspace_id
    current_label = None
    for label, ws_id in workspace_options.items():
        if ws_id == current_ws_id:
            current_label = label
            break
    
    if current_label is None and workspace_options:
        # Fallback to first workspace
        current_label = list(workspace_options.keys())[0]
        st.session_state.active_workspace_id = workspace_options[current_label]
    
    # Render selector
    st.sidebar.markdown("### 📂 Workspace")
    
    selected_label = st.sidebar.selectbox(
        "Selecione o workspace:",
        options=list(workspace_options.keys()),
        index=list(workspace_options.keys()).index(current_label) if current_label else 0,
        key="workspace_selector",
        label_visibility="collapsed"
    )
    
    selected_workspace_id = workspace_options[selected_label]
    
    # Check if changed
    if selected_workspace_id != st.session_state.active_workspace_id:
        st.session_state.active_workspace_id = selected_workspace_id
        # Clear cache on workspace change
        st.cache_data.clear()
        st.cache_resource.clear()
        st.toast(f"✅ Workspace alterado", icon="✅")
        st.rerun()
    
    # Show workspace info
    current_ws = next((ws for ws in workspaces if ws.id == selected_workspace_id), None)
    if current_ws:
        if current_ws.type == "personal":
            st.sidebar.caption("💡 Workspace pessoal - apenas você tem acesso")
        else:
            member_count = len(db.get_workspace_members(current_ws.id))
            st.sidebar.caption(f"👥 {member_count} membro(s) neste workspace")
    
    return selected_workspace_id


def ensure_workspace_selected() -> Optional[int]:
    """
    Helper to ensure a workspace is selected.
    Shows warning if not selected.
    
    Returns:
        workspace_id or None
    """
    workspace_id = st.session_state.get("active_workspace_id")
    
    if not workspace_id:
        st.warning("⚠️ Por favor, selecione um workspace na barra lateral.")
        st.stop()
    
    return workspace_id

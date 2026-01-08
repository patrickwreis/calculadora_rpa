# -*- coding: utf-8 -*-
"""
Workspace Management Page
Create, edit, and manage shared workspaces
"""
import streamlit as st
from src.database.db_manager import get_database_manager
from src.ui.workspace_selector import ensure_workspace_selected
from src.security import SessionManager
from src.ui.auth import require_auth

st.set_page_config(
    page_title="Espaços de Trabalho",
    page_icon="📂",
    layout="wide"
)

# Auth: tenta restaurar; se falhar, redireciona para login principal
SessionManager.ensure_auth(redirect_page="streamlit_app.py")

# Auth gate (renders login form if needed)
if not require_auth(form_key="workspaces_login"):
    st.stop()

st.title("📂 Espaços de Trabalho")
st.markdown("Gerencie seus espaços de trabalho pessoais e compartilhados")

# Workspace selector in sidebar
from src.ui.workspace_selector import render_workspace_selector
with st.sidebar:
    st.markdown("---")
    render_workspace_selector()
    st.markdown("---")

db = get_database_manager()
user_id = st.session_state.auth_user_id

# Garante que o ID do usuário está presente
if user_id is None:
    st.error("Sessão inválida. Faça login novamente.")
    st.stop()

# Get user workspaces
workspaces = db.get_user_workspaces(user_id)

if not workspaces:
    st.error("Nenhum espaço de trabalho encontrado")
    st.stop()

# Separate personal and shared
personal_workspaces = [ws for ws in workspaces if ws.type == "personal"]
shared_workspaces = [ws for ws in workspaces if ws.type == "shared"]

# Create tabs
tab1, tab2, tab3 = st.tabs(["📋 Meus Espaços", "➕ Novo Espaço", "👥 Gerenciar Membros"])

# ==================== TAB 1: View Workspaces ====================
with tab1:
    st.subheader("🏠 Espaço Pessoal")
    
    if personal_workspaces:
        for ws in personal_workspaces:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{ws.name}**")
                    if ws.description:
                        st.write(ws.description)
                
                with col2:
                    st.metric("Tipo", "Pessoal")
                
                with col3:
                    st.metric("Status", "✅ Ativo")
    else:
        st.info("Você não tem um espaço pessoal")
    
    st.divider()
    st.subheader("📁 Espaços Compartilhados")
    
    if shared_workspaces:
        for ws in shared_workspaces:
            if ws.id is None:
                st.warning("Espaço com ID inválido. Recarregue a página.")
                continue

            role = db.get_user_role_in_workspace(ws.id, user_id)
            members = db.get_workspace_members(ws.id)
            
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{ws.name}**")
                    if ws.description:
                        st.caption(ws.description)
                
                with col2:
                    role_display = role or "membro"
                    role_emoji = "👑" if role_display == "owner" else "📁"
                    st.metric("Seu Papel", f"{role_emoji} {role_display.capitalize()}")
                
                with col3:
                    st.metric("Membros", len(members))
                
                # Edit button (only for owner/admin)
                if role in ["owner", "admin"]:
                    if st.button("✏️ Editar", key=f"edit_ws_{ws.id}", use_container_width=True):
                        st.session_state[f"edit_workspace_{ws.id}"] = True
                
                # Show edit form if opened
                if st.session_state.get(f"edit_workspace_{ws.id}", False):
                    st.markdown("#### Editar Espaço")
                    
                    new_name = st.text_input(
                        "Nome",
                        value=ws.name,
                        key=f"edit_name_{ws.id}"
                    )
                    
                    new_description = st.text_area(
                        "Descrição",
                        value=ws.description or "",
                        key=f"edit_desc_{ws.id}"
                    )

                    st.markdown("##### Adicionar membro (rápido)")
                    add_col1, add_col2 = st.columns([2, 1])
                    with add_col1:
                        quick_email = st.text_input(
                            "Email do membro",
                            placeholder="email@empresa.com",
                            key=f"quick_member_email_{ws.id}"
                        )
                    with add_col2:
                        quick_role = st.selectbox(
                            "Papel",
                            options=["editor", "viewer", "admin"],
                            index=0,
                            format_func=lambda x: {
                                "editor": "📝 Editor",
                                "viewer": "👁️ Viewer",
                                "admin": "⚙️ Admin",
                            }[x],
                            key=f"quick_member_role_{ws.id}"
                        )

                    if st.button("➕ Adicionar membro", key=f"quick_member_btn_{ws.id}", use_container_width=True):
                        import re
                        email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
                        email = (quick_email or "").strip().lower()
                        if not email or not re.match(email_regex, email):
                            st.warning("⚠️ Email inválido.")
                        else:
                            user_obj = db.get_user_by_email(email)
                            owner_id = getattr(ws, "owner_id", None)
                            if not user_obj:
                                st.warning("🔎 Usuário não encontrado. Peça para ele se cadastrar primeiro.")
                            elif ws.id is None:
                                st.error("❌ ID do espaço inválido. Recarregue a página.")
                            elif user_obj.id is None:
                                st.error("❌ Usuário com ID inválido.")
                            elif owner_id is not None and user_obj.id == owner_id:
                                st.info("ℹ️ O proprietário já está neste espaço.")
                            else:
                                existing_ids = [u.id for u, _ in db.get_workspace_members(ws.id)]
                                if user_obj.id in existing_ids:
                                    st.info("ℹ️ Este usuário já é membro deste espaço.")
                                else:
                                    ok = db.add_workspace_member(ws.id, user_obj.id, quick_role)
                                    if ok:
                                        st.success(f"👥 {email} adicionado como {quick_role}.")
                                        st.rerun()
                                    else:
                                        st.error("❌ Não foi possível adicionar o membro.")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("💾 Salvar", key=f"save_ws_{ws.id}", use_container_width=True, type="primary"):
                            if db.update_workspace(ws.id, new_name, new_description):
                                st.success("✅ Espaço atualizado com sucesso!")
                                st.session_state[f"edit_workspace_{ws.id}"] = False
                                st.rerun()
                            else:
                                st.error("❌ Erro ao atualizar espaço")
                    
                    with col2:
                        if st.button("❌ Cancelar", key=f"cancel_ws_{ws.id}", use_container_width=True):
                            st.session_state[f"edit_workspace_{ws.id}"] = False
                            st.rerun()
    else:
        st.info("Você não é membro de nenhum espaço compartilhado. Crie um novo!")

# ==================== TAB 2: Create Workspace ====================
with tab2:
    st.subheader("➕ Criar Novo Espaço Compartilhado")
    
    with st.form("create_workspace_form"):
        ws_name = st.text_input(
            "Nome do Espaço",
            placeholder="Ex: Projeto ABC, Consultoria XYZ",
            help="Nome único para o espaço de trabalho"
        )
        
        ws_description = st.text_area(
            "Descrição (opcional)",
            placeholder="Descreva o propósito deste espaço",
            height=100
        )
        
        st.divider()
        st.markdown("#### Membro Inicial (opcional)")


        col1, col2 = st.columns(2)
        with col1:
            initial_member_email = st.text_input(
                "Email do membro",
                placeholder="email@empresa.com",
                key="initial_member_email",
                help="Opcional. Apenas usuários já cadastrados serão adicionados."
            )
        with col2:
            initial_member_role = st.selectbox(
                "Papel do membro",
                options=["editor", "viewer", "admin"],
                index=0,
                format_func=lambda x: {
                    "editor": "📝 Editor - pode criar/editar cálculos",
                    "viewer": "👁️ Visualizador - apenas leitura",
                    "admin": "⚙️ Admin - gerencia espaço e membros",
                }[x],
                key="initial_member_role"
            )
        
        submitted = st.form_submit_button("✅ Criar Espaço", type="primary", use_container_width=True)
        
        if submitted:
            if not ws_name or len(ws_name.strip()) == 0:
                st.error("❌ Nome do espaço é obrigatório")
            else:
                success, workspace_id, error = db.create_workspace(
                    name=ws_name,
                    owner_id=user_id,
                    workspace_type="shared",
                    description=ws_description if ws_description else None
                )
                
                if success:
                    st.success(f"✅ Espaço '{ws_name}' criado com sucesso!")
                    st.balloons()
                    st.session_state.created_workspace_id = workspace_id
                    # Se houver email informado, tentar adicionar como membro
                    if initial_member_email and initial_member_email.strip():
                        import re
                        email = initial_member_email.strip().lower()
                        email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
                        if not re.match(email_regex, email):
                            st.warning("⚠️ Email inválido para membro inicial.")
                        elif workspace_id is None:
                            st.warning("⚠️ ID do espaço não retornado; não foi possível adicionar membro inicial.")
                        else:
                            member_user = db.get_user_by_email(email)
                            if not member_user:
                                st.warning("🔎 Usuário não encontrado. Ele precisa se cadastrar primeiro.")
                            elif member_user.id == user_id:
                                st.info("ℹ️ Você já é o proprietário deste espaço.")
                            elif member_user.id is None:
                                st.warning("⚠️ Usuário sem ID válido.")
                            else:
                                ok = db.add_workspace_member(workspace_id, member_user.id, initial_member_role)
                                if ok:
                                    st.success(f"👥 {email} adicionado como {initial_member_role}.")
                                else:
                                    st.info("ℹ️ Usuário já é membro deste espaço.")

                    st.info("💡 Você pode gerenciar membros a qualquer momento na aba 'Gerenciar Membros'.")
                else:
                    st.error(f"❌ Erro ao criar espaço: {error}")

# ==================== TAB 3: Manage Members ====================
with tab3:
    st.subheader("👥 Gerenciar Membros")
    
    # Select workspace to manage
    shared_ws_options = {ws.name: ws.id for ws in shared_workspaces}
    
    if not shared_ws_options:
        st.info("Você não tem espaços compartilhados. Crie um na aba 'Novo Espaço'")
    else:
        # Use created workspace if exists, otherwise first one
        default_ws_id = st.session_state.get("created_workspace_id")
        if default_ws_id and default_ws_id in shared_ws_options.values():
            default_idx = list(shared_ws_options.values()).index(default_ws_id)
        else:
            default_idx = 0
        
        selected_ws_name = st.selectbox(
            "Selecione o espaço",
            options=list(shared_ws_options.keys()),
            index=default_idx
        )
        
        selected_ws_id = shared_ws_options[selected_ws_name]
        selected_ws = db.get_workspace_by_id(selected_ws_id)
        if not selected_ws:
            st.error("❌ Espaço não encontrado. Recarregue a página.")
            st.stop()

        user_role = db.get_user_role_in_workspace(selected_ws_id, user_id)
        owner_id = getattr(selected_ws, "owner_id", None)
        
        # Check if user can manage members
        if user_role not in ["owner", "admin"]:
            st.warning(f"⚠️ Você é um {user_role}. Apenas proprietários e administradores podem gerenciar membros.")
        else:
            st.divider()
            
            # Show current members
            st.markdown("#### Membros Atuais")
            members = db.get_workspace_members(selected_ws_id)
            
            if members:
                member_data = []
                for user, role in members:
                    is_owner = owner_id is not None and user.id == owner_id
                    member_data.append({
                        "ID": user.id,
                        "Email": user.email,
                        "Papel": "👑 Proprietário" if is_owner else f"📁 {role.capitalize()}",
                        "Status": "✅ Ativo"
                    })
                
                st.dataframe(
                    member_data,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhum membro ainda neste espaço")
            
            st.divider()
            
            # Add new member
            st.markdown("#### Adicionar Novo Membro")
            
            with st.form("add_member_form", border=False):
                member_email = st.text_input(
                    "Email do Membro",
                    placeholder="email@exemplo.com",
                    help="Email do usuário que já possui cadastro"
                )
                
                member_role = st.selectbox(
                    "Papel",
                    options=["editor", "viewer", "admin"],
                    format_func=lambda x: {
                        "editor": "📝 Editor - Pode criar/editar cálculos",
                        "viewer": "👁️ Visualizador - Apenas leitura",
                        "admin": "⚙️ Admin - Gerenciar espaço e membros"
                    }[x]
                )
                
                submitted = st.form_submit_button("➕ Adicionar Membro", type="primary", use_container_width=True)
                
                if submitted:
                    if not member_email:
                        st.error("❌ Email é obrigatório")
                    else:
                        # Get user by email
                        member_user = db.get_user_by_email(member_email)
                        
                        if not member_user:
                            st.error(f"❌ Usuário com email '{member_email}' não encontrado")
                            st.info("💡 O usuário precisa fazer cadastro primeiro")
                        else:
                            # Check if already member
                            existing_members = [u.id for u, _ in members]
                            if member_user.id is None:
                                st.error("❌ Usuário sem ID válido.")
                            elif member_user.id in existing_members or (owner_id is not None and member_user.id == owner_id):
                                st.error("⚠️ Este usuário já é membro deste espaço")
                            else:
                                success = db.add_workspace_member(
                                    selected_ws_id,
                                    member_user.id,
                                    member_role
                                )
                                
                                if success:
                                    st.success(f"✅ {member_email} adicionado como {member_role}!")
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao adicionar membro")
            
            # Remove members
            if members:
                st.divider()
                st.markdown("#### Remover Membro")
                
                member_to_remove = st.selectbox(
                    "Selecione membro para remover",
                    options=[(u.id, u.email) for u, _ in members],
                    format_func=lambda x: x[1]
                )
                
                if member_to_remove:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Remover Membro", key="remove_member", use_container_width=True, type="secondary"):
                            member_id = member_to_remove[0]
                            success = db.remove_workspace_member(selected_ws_id, member_id)
                            
                            if success:
                                st.success("✅ Membro removido!")
                                st.rerun()
                            else:
                                st.error("❌ Erro ao remover membro")

st.divider()
st.markdown("""
### 💡 Dicas
- **Espaço Pessoal**: Apenas você tem acesso (🏠)
- **Espaço Compartilhado**: Você escolhe quem tem acesso (📁)
- **Papéis**:
  - 👑 **Proprietário**: Controle total
  - ⚙️ **Admin**: Gerenciar espaço e membros
  - 📝 **Editor**: Criar e editar cálculos
  - 👁️ **Visualizador**: Apenas ver cálculos
""")

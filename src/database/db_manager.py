# -*- coding: utf-8 -*-
"""Database management"""
from sqlalchemy import create_engine, text
from sqlmodel import Session, select
from typing import List, Optional, Tuple, Any
from datetime import datetime
from config import DATABASE_URL
import functools
import time
import logging
import streamlit as st

# Import models at module level to avoid redefinition warnings
from src.models import Calculation, User, Workspace, WorkspaceMember, classify_process

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass


class CacheManager:
    """Simple cache manager for database queries"""
    
    def __init__(self, ttl: int = 300):
        """
        Initialize cache manager
        
        Args:
            ttl: Time to live for cached items in seconds (default 5 minutes)
        """
        self.ttl = ttl
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache if still valid"""
        if key in self._cache:
            if time.time() - self._timestamps[key] < self.ttl:
                return self._cache[key]
            else:
                # Cache expired, remove it
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cached items"""
        self._cache.clear()
        self._timestamps.clear()
    
    def clear_key(self, key: str) -> None:
        """Clear specific cache key"""
        if key in self._cache:
            del self._cache[key]
            del self._timestamps[key]


class DatabaseManager:
    """Manage database operations"""
    
    _cache_manager = CacheManager(ttl=300)  # 5 minute cache
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, echo=False)
        self._create_tables()
        self._migrate_tables()
    
    def _create_tables(self):
        """Create database tables"""
        # Use the correct metadata with all registered models
        from sqlmodel import SQLModel
        SQLModel.metadata.create_all(self.engine)
        # Note: _migrate_tables() is disabled as all tables are created properly by SQLAlchemy/SQLModel
        # If you need to add columns in the future, use alembic migrations instead
    
    def _migrate_tables(self):
        """Deprecated: Use alembic migrations for schema changes instead.
        
        This method was used for SQLite migrations and is no longer needed
        since we're using SQLAlchemy/SQLModel with PostgreSQL which creates
        all tables automatically.
        """
        pass
    
    def save_calculation(self, calculation_data: dict) -> Tuple[bool, Optional["Calculation"], Optional[str]]:
        """
        Save a calculation to the database with automatic classification
        
        Args:
            calculation_data: Dictionary with calculation data
            
        Returns:
            Tuple of (success: bool, calculation: Calculation or None, error_message: str or None)
        """
        try:
            # Auto-classify before saving
            if 'roi_percentage_first_year' in calculation_data and 'payback_period_months' in calculation_data:
                roi = calculation_data['roi_percentage_first_year']
                payback = calculation_data['payback_period_months']
                calculation_data['classification'] = classify_process(roi, payback)
            
            calculation = Calculation(**calculation_data)
            with Session(self.engine) as session:
                try:
                    session.add(calculation)
                    session.commit()
                    session.refresh(calculation)
                    logger.info(f"Calculation saved: {calculation.id} - {calculation.process_name} - Classification: {calculation.classification}")
                except Exception as e:
                    session.rollback()
                    error_msg = f"Database commit failed: {str(e)}"
                    logger.error(error_msg)
                    return False, None, error_msg
            
            # Invalidate cache when saving
            # Invalidate all user-specific caches since we don't know which user this affects
            self._cache_manager.clear()
            
            return True, calculation, None
        except ValueError as e:
            error_msg = f"Invalid calculation data: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error saving calculation: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def get_all_calculations(self, user_id: Optional[int] = 1, use_cache: bool = True) -> Tuple[bool, List["Calculation"], Optional[str]]:
        """
        Get all calculations filtered by user_id (None = todos)
        
        Args:
            user_id: User ID to filter by (default 1)
            use_cache: Whether to use cached results (default True)
            
        Returns:
            Tuple of (success: bool, calculations: list, error_message: str or None)
        """
        try:
            cache_key = f"all_calculations_user_{user_id if user_id is not None else 'all'}"
            
            # Try cache first
            if use_cache:
                cached = self._cache_manager.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache hit for all_calculations (user_id={user_id})")
                    return True, cached, None
            
            with Session(self.engine) as session:
                try:
                    if user_id is None:
                        statement = select(Calculation)
                    else:
                        statement = select(Calculation).where(Calculation.user_id == user_id)
                    calculations = session.exec(statement).all()
                    result = list(calculations)
                    logger.info(f"Retrieved {len(result)} calculations for user {user_id} from database")
                except Exception as e:
                    error_msg = f"Database query failed: {str(e)}"
                    logger.error(error_msg)
                    return False, [], error_msg
            
            # Cache the result
            if use_cache:
                self._cache_manager.set(cache_key, result)
            
            return True, result, None
        except Exception as e:
            error_msg = f"Unexpected error getting calculations: {str(e)}"
            logger.error(error_msg)
            return False, [], error_msg
    
    def get_calculation(self, calc_id: int, use_cache: bool = True) -> Tuple[bool, Optional["Calculation"], Optional[str]]:
        """
        Get a specific calculation by ID
        
        Args:
            calc_id: The calculation ID
            use_cache: Whether to use cached results (default True)
            
        Returns:
            Tuple of (success: bool, calculation: Calculation or None, error_message: str or None)
        """
        try:
            cache_key = f"calculation_{calc_id}"
            
            # Try cache first
            if use_cache:
                cached = self._cache_manager.get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache hit for calculation {calc_id}")
                    return True, cached, None
            
            with Session(self.engine) as session:
                try:
                    statement = select(Calculation).where(Calculation.id == calc_id)
                    calculation = session.exec(statement).first()
                except Exception as e:
                    error_msg = f"Database query failed: {str(e)}"
                    logger.error(error_msg)
                    return False, None, error_msg
            
            if not calculation:
                logger.warning(f"Calculation {calc_id} not found")
                return True, None, None  # Not an error, just not found
            
            # Cache the result
            if use_cache:
                self._cache_manager.set(cache_key, calculation)
            
            return True, calculation, None
        except Exception as e:
            error_msg = f"Unexpected error getting calculation: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def update_calculation(self, calc_id: int, calculation_data: dict) -> Tuple[bool, Optional["Calculation"], Optional[str]]:
        """
        Update a calculation with automatic re-classification
        
        Args:
            calc_id: The calculation ID to update
            calculation_data: Dictionary with fields to update
            
        Returns:
            Tuple of (success: bool, calculation: Calculation or None, error_message: str or None)
        """
        try:
            with Session(self.engine) as session:
                try:
                    statement = select(Calculation).where(Calculation.id == calc_id)
                    calculation = session.exec(statement).first()
                    
                    if not calculation:
                        logger.warning(f"Calculation {calc_id} not found for update")
                        return True, None, None  # Not an error, just not found
                    
                    for key, value in calculation_data.items():
                        if hasattr(calculation, key):
                            setattr(calculation, key, value)
                    
                    # Re-classify if ROI or payback changed
                    if 'roi_percentage_first_year' in calculation_data or 'payback_period_months' in calculation_data:
                        calculation.classification = classify_process(
                            calculation.roi_percentage_first_year,
                            calculation.payback_period_months
                        )
                    
                    session.add(calculation)
                    session.commit()
                    session.refresh(calculation)
                    logger.info(f"Calculation updated: {calc_id} - Classification: {calculation.classification}")
                    
                    # Invalidate cache
                    # Invalidate all caches since we don't know which users are affected
                    self._cache_manager.clear()
                    
                    return True, calculation, None
                except Exception as e:
                    session.rollback()
                    error_msg = f"Database transaction failed: {str(e)}"
                    logger.error(error_msg)
                    return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error updating calculation: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def delete_calculation(self, calc_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a calculation
        
        Args:
            calc_id: The calculation ID to delete
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            with Session(self.engine) as session:
                try:
                    statement = select(Calculation).where(Calculation.id == calc_id)
                    calculation = session.exec(statement).first()
                    
                    if not calculation:
                        logger.warning(f"Calculation {calc_id} not found for deletion")
                        return True, None  # Not an error, just not found
                    
                    session.delete(calculation)
                    session.commit()
                    logger.info(f"Calculation deleted: {calc_id}")
                    
                    # Invalidate cache
                    # Invalidate all caches since we don't know which users are affected
                    self._cache_manager.clear()
                    
                    return True, None
                except Exception as e:
                    session.rollback()
                    error_msg = f"Database transaction failed: {str(e)}"
                    logger.error(error_msg)
                    return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error deleting calculation: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    # ========== USER MANAGEMENT ==========
    def get_user_by_username(self, username: str) -> Optional["User"]:
        """Fetch user by username."""
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).first()

    def get_user_by_email(self, email: str) -> Optional["User"]:
        """Fetch user by email."""
        with Session(self.engine) as session:
            statement = select(User).where(User.email == email)
            return session.exec(statement).first()

    def list_active_users(self) -> List["User"]:
        """Return all active users."""
        with Session(self.engine) as session:
            statement = select(User).where(User.is_active == True)
            return list(session.exec(statement).all())

    def list_users(self, include_inactive: bool = True) -> List["User"]:
        """Return users; include inactive when requested."""
        with Session(self.engine) as session:
            stmt = select(User)
            if not include_inactive:
                stmt = stmt.where(User.is_active == True)
            return list(session.exec(stmt).all())

    def set_user_active(self, user_id: int, is_active: bool) -> bool:
        """Activate/deactivate user."""
        with Session(self.engine) as session:
            user = session.get(User, user_id)
            if not user:
                return False
            user.is_active = is_active
            session.add(user)
            session.commit()
            return True

    def create_user(self, username: str, password_hash: str, email: str = "", is_admin: bool = False, is_active: bool = True) -> Optional["User"]:
        """
        Create a new user and automatically create their personal workspace.
        
        Args:
            username: Username
            password_hash: Hashed password
            email: Email address
            is_admin: Admin flag
            is_active: Active flag
            
        Returns:
            User object or None if username already taken
        """
        with Session(self.engine) as session:
            existing = session.exec(select(User).where(User.username == username)).first()
            if existing:
                return existing
            
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                is_admin=is_admin,
                is_active=is_active,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            # Auto-create personal workspace for new user
            user_id = user.id
        
        # Create personal workspace (outside session to avoid nested transaction)
        success, workspace_id, error = self.create_workspace(
            name=f"Workspace de {username}",
            owner_id=user_id,
            workspace_type="personal",
            description="Workspace pessoal"
        )
        
        if success:
            logger.info(f"Personal workspace created for user {username} (workspace_id={workspace_id})")
        else:
            logger.error(f"Failed to create personal workspace for user {username}: {error}")
        
        return user
    
    @staticmethod
    def clear_cache() -> None:
        """Clear all cached data"""
        DatabaseManager._cache_manager.clear()
        logger.info("Cache cleared")
    
    # ========== LEGACY METHODS FOR BACKWARD COMPATIBILITY ==========
    
    def save_calculation_legacy(self, calculation_data: dict) -> Optional["Calculation"]:
        """Legacy wrapper for save_calculation"""
        success, calc, _ = self.save_calculation(calculation_data)
        return calc if success else None
    
    def get_all_calculations_legacy(self, use_cache: bool = True) -> List["Calculation"]:
        """Legacy wrapper for get_all_calculations"""
        success, calcs, _ = self.get_all_calculations(use_cache)
        return calcs if success else []
    
    def get_calculation_legacy(self, calc_id: int, use_cache: bool = True) -> Optional["Calculation"]:
        """Legacy wrapper for get_calculation"""
        success, calc, _ = self.get_calculation(calc_id, use_cache)
        return calc if success else None
    
    def update_calculation_legacy(self, calc_id: int, calculation_data: dict) -> Optional["Calculation"]:
        """Legacy wrapper for update_calculation"""
        success, calc, _ = self.update_calculation(calc_id, calculation_data)
        return calc if success else None
    
    def delete_calculation_legacy(self, calc_id: int) -> bool:
        """Legacy wrapper for delete_calculation"""
        success, _ = self.delete_calculation(calc_id)
        return success

    def update_user_password(self, username: str, hashed_password: str) -> bool:
        """Update user password by username."""
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()
            if not user:
                return False
            user.password_hash = hashed_password
            session.add(user)
            session.commit()
            return True
    
    def update_session_token(self, user_id: Optional[int], token: Optional[str], expiry: Optional['datetime']) -> bool:
        """Update user session token."""
        if user_id is None:
            return False
        with Session(self.engine) as session:
            user = session.get(User, user_id)
            if not user:
                return False
            user.session_token = token
            user.session_token_expiry = expiry
            session.add(user)
            session.commit()
            return True
    
    def get_user_by_session_token(self, token: str) -> Optional['User']:
        """Get user by session token and return detached user object."""
        from sqlalchemy import inspect
        
        with Session(self.engine) as session:
            statement = select(User).where(User.session_token == token)
            user = session.exec(statement).first()
            if not user:
                return None
            
            # Force load all attributes before exiting the session
            _ = user.id
            _ = user.username
            _ = user.password_hash
            _ = user.email
            _ = user.is_admin
            _ = user.is_active
            _ = user.session_token
            _ = user.session_token_expiry
            
            # Make a detached copy by accessing all attributes
            return user

    # ==================== Workspace Methods ====================
    
    def create_workspace(self, name: str, owner_id: int, workspace_type: str = "shared", 
                        description: Optional[str] = None) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Create a new workspace.
        
        Args:
            name: Workspace name
            owner_id: User ID of the owner
            workspace_type: "personal" or "shared"
            description: Optional description
            
        Returns:
            Tuple of (success, workspace_id, error_message)
        """
        try:
            import re
            
            # Generate slug from name
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
            slug = f"{slug}-{owner_id}-{int(time.time())}"
            
            with Session(self.engine) as session:
                workspace = Workspace(
                    name=name,
                    slug=slug,
                    description=description,
                    type=workspace_type,
                    owner_id=owner_id,
                    is_active=True
                )
                session.add(workspace)
                session.commit()
                session.refresh(workspace)
                
                logger.info(f"Workspace created: {workspace.name} (id={workspace.id}, type={workspace_type})")
                return True, workspace.id, None
                
        except Exception as e:
            error_msg = f"Failed to create workspace: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def get_user_workspaces(self, user_id: int) -> List[Any]:
        """
        Get all workspaces accessible by a user (owned + member of).
        
        Args:
            user_id: User ID
            
        Returns:
            List of Workspace objects
        """
        try:
            with Session(self.engine) as session:
                # Get workspaces where user is owner
                owned_stmt = select(Workspace).where(
                    Workspace.owner_id == user_id,
                    Workspace.is_active == True
                )
                owned = session.exec(owned_stmt).all()
                
                # Get workspaces where user is a member
                member_stmt = select(Workspace).join(WorkspaceMember).where(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.is_active == True,
                    Workspace.is_active == True
                )
                member_of = session.exec(member_stmt).all()
                
                # Combine and deduplicate
                all_workspaces = list(owned) + [ws for ws in member_of if ws not in owned]
                
                logger.debug(f"User {user_id} has access to {len(all_workspaces)} workspaces")
                return all_workspaces
                
        except Exception as e:
            logger.error(f"Failed to get user workspaces: {str(e)}")
            return []
    
    def get_workspace_by_id(self, workspace_id: int) -> Optional[Any]:
        """Get workspace by ID."""
        try:
            with Session(self.engine) as session:
                workspace = session.get(Workspace, workspace_id)
                return workspace
                
        except Exception as e:
            logger.error(f"Failed to get workspace: {str(e)}")
            return None
    
    def update_workspace(self, workspace_id: int, name: Optional[str] = None, 
                        description: Optional[str] = None) -> bool:
        """Update workspace details."""
        try:
            with Session(self.engine) as session:
                workspace = session.get(Workspace, workspace_id)
                if not workspace:
                    return False
                
                if name:
                    workspace.name = name
                if description is not None:
                    workspace.description = description
                    
                workspace.updated_at = datetime.utcnow()
                session.add(workspace)
                session.commit()
                
                logger.info(f"Workspace {workspace_id} updated")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update workspace: {str(e)}")
            return False
    
    def delete_workspace(self, workspace_id: int) -> bool:
        """Soft delete a workspace (set is_active=False)."""
        try:
            with Session(self.engine) as session:
                workspace = session.get(Workspace, workspace_id)
                if not workspace:
                    return False
                
                # Don't allow deleting personal workspaces
                if workspace.type == "personal":
                    logger.warning(f"Cannot delete personal workspace {workspace_id}")
                    return False
                
                workspace.is_active = False
                workspace.updated_at = datetime.utcnow()
                session.add(workspace)
                session.commit()
                
                logger.info(f"Workspace {workspace_id} deleted (soft)")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete workspace: {str(e)}")
            return False
    
    def add_workspace_member(self, workspace_id: int, user_id: int, role: str = "editor") -> bool:
        """
        Add a user as member to a workspace.
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID to add
            role: Role - "admin", "editor", or "viewer"
            
        Returns:
            Success boolean
        """
        try:
            with Session(self.engine) as session:
                # Check if workspace is shared
                workspace = session.get(Workspace, workspace_id)
                if not workspace or workspace.type != "shared":
                    logger.warning(f"Cannot add member to non-shared workspace {workspace_id}")
                    return False
                
                # Check if already a member
                existing = session.exec(
                    select(WorkspaceMember).where(
                        WorkspaceMember.workspace_id == workspace_id,
                        WorkspaceMember.user_id == user_id
                    )
                ).first()
                
                if existing:
                    if not existing.is_active:
                        # Reactivate
                        existing.is_active = True
                        existing.role = role
                        session.add(existing)
                        session.commit()
                        logger.info(f"Workspace member reactivated: user {user_id} in workspace {workspace_id}")
                        return True
                    else:
                        logger.warning(f"User {user_id} already member of workspace {workspace_id}")
                        return False
                
                # Add new member
                member = WorkspaceMember(
                    workspace_id=workspace_id,
                    user_id=user_id,
                    role=role,
                    is_active=True
                )
                session.add(member)
                session.commit()
                
                logger.info(f"Workspace member added: user {user_id} to workspace {workspace_id} as {role}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add workspace member: {str(e)}")
            return False
    
    def remove_workspace_member(self, workspace_id: int, user_id: int) -> bool:
        """Remove a user from workspace (soft delete)."""
        try:
            with Session(self.engine) as session:
                member = session.exec(
                    select(WorkspaceMember).where(
                        WorkspaceMember.workspace_id == workspace_id,
                        WorkspaceMember.user_id == user_id
                    )
                ).first()
                
                if not member:
                    return False
                
                member.is_active = False
                session.add(member)
                session.commit()
                
                logger.info(f"Workspace member removed: user {user_id} from workspace {workspace_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to remove workspace member: {str(e)}")
            return False
    
    def get_workspace_members(self, workspace_id: int) -> List[Any]:
        """Get all active members of a workspace."""
        try:
            with Session(self.engine) as session:
                stmt = select(User, WorkspaceMember.role).join(
                    WorkspaceMember,
                    User.id == WorkspaceMember.user_id
                ).where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.is_active == True
                )
                results = session.exec(stmt).all()
                
                return results
                
        except Exception as e:
            logger.error(f"Failed to get workspace members: {str(e)}")
            return []
    
    def get_user_role_in_workspace(self, workspace_id: int, user_id: int) -> Optional[str]:
        """
        Get user's role in a workspace.
        
        Returns: "owner", "admin", "editor", "viewer", or None if not member
        """
        try:
            with Session(self.engine) as session:
                # Check if owner
                workspace = session.get(Workspace, workspace_id)
                if workspace and workspace.owner_id == user_id:
                    return "owner"
                
                # Check member role
                member = session.exec(
                    select(WorkspaceMember).where(
                        WorkspaceMember.workspace_id == workspace_id,
                        WorkspaceMember.user_id == user_id,
                        WorkspaceMember.is_active == True
                    )
                ).first()
                
                return member.role if member else None
                
        except Exception as e:
            logger.error(f"Failed to get user role: {str(e)}")
            return None
    
    def get_workspace_calculations(self, workspace_id: int) -> List["Calculation"]:
        """Get all calculations in a workspace."""
        try:
            cache_key = f"workspace_calculations_{workspace_id}"
            
            # Check cache
            cached = self._cache_manager.get(cache_key)
            if cached is not None:
                logger.info(f"Retrieved {len(cached)} calculations for workspace {workspace_id} from cache")
                return cached
            
            with Session(self.engine) as session:
                stmt = select(Calculation).where(
                    Calculation.workspace_id == workspace_id
                ).order_by(Calculation.created_at.desc())
                
                calculations = session.exec(stmt).all()
                
                # Cache the results
                self._cache_manager.set(cache_key, calculations)
                
                logger.info(f"Retrieved {len(calculations)} calculations for workspace {workspace_id} from database")
                return calculations
                
        except Exception as e:
            logger.error(f"Failed to get workspace calculations: {str(e)}")
            return []
    
    def get_user_by_email(self, email: str) -> Optional['User']:
        """Get user by email."""
        try:
            with Session(self.engine) as session:
                stmt = select(User).where(User.email == email)
                user = session.exec(stmt).first()
                return user
                
        except Exception as e:
            logger.error(f"Failed to get user by email: {str(e)}")
            return None



@st.cache_resource
def get_database_manager() -> "DatabaseManager":
    """Get or create cached DatabaseManager instance (cached per session)."""
    return DatabaseManager()

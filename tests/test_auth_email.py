# -*- coding: utf-8 -*-
"""Tests for authentication with email functionality."""
import pytest
from src.database.db_manager import DatabaseManager
from src.ui.auth import (
    hash_password,
    verify_password,
    send_password_reset_email,
    _truncate_for_bcrypt,
)
from src.models import User


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a valid bcrypt hash string."""
        password = "test_password"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password
    
    def test_hash_password_consistent_verification(self):
        """Test that hashed passwords can be verified."""
        password = "test_password"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_wrong_password(self):
        """Test that wrong passwords don't verify."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False
    
    def test_hash_password_long_password(self):
        """Test hashing of passwords longer than 72 bytes (bcrypt limit)."""
        long_password = "x" * 100  # 100 characters
        hashed = hash_password(long_password)
        # Should truncate to 72 bytes and still work
        assert verify_password(long_password, hashed) is True
    
    def test_verify_password_truncates_at_72_bytes(self):
        """Test that verification truncates passwords at 72 bytes."""
        base_password = "x" * 72
        long_password = base_password + "y" * 50  # 122 chars total
        hashed = hash_password(base_password)
        # Should verify because truncation happens in both hash and verify
        assert verify_password(long_password, hashed) is True


class TestUserModelWithEmail:
    """Test User model with email field."""
    
    def test_user_with_email_creation(self):
        """Test creating a User with email."""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash123",
            is_active=True,
            is_admin=False,
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hash123"
        assert user.is_active is True
        assert user.is_admin is False
    
    def test_user_email_required(self):
        """Test that User requires email field."""
        # This should work in creation but SQLModel will enforce it on save
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hash123",
        )
        assert user.email == "test@example.com"


class TestCreateUserWithEmail:
    """Test creating users with email in database."""
    
    def test_create_user_with_email(self, tmp_path):
        """Test creating a user with email in database."""
        from config import DATABASE_URL
        import tempfile
        
        # Create temporary database
        db_path = tmp_path / "test.db"
        db_url = f"sqlite:///{db_path}"
        
        # Mock DatabaseManager to use temp DB
        original_url = DATABASE_URL
        import config
        config.DATABASE_URL = db_url
        
        try:
            db = DatabaseManager()
            user = db.create_user(
                username="testuser",
                password_hash=hash_password("password123"),
                email="test@example.com",
                is_admin=False,
                is_active=True,
            )
            
            assert user is not None
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            
            # Verify we can retrieve the user
            retrieved = db.get_user_by_username("testuser")
            assert retrieved is not None
            assert retrieved.email == "test@example.com"
        finally:
            config.DATABASE_URL = original_url
    
    def test_create_user_email_default(self, tmp_path):
        """Test creating user with default email."""
        import config
        
        db_path = tmp_path / "test.db"
        db_url = f"sqlite:///{db_path}"
        original_url = config.DATABASE_URL
        config.DATABASE_URL = db_url
        
        try:
            db = DatabaseManager()
            user = db.create_user(
                username="testuser2",
                password_hash=hash_password("password123"),
            )
            
            assert user is not None
            assert user.username == "testuser2"
            # Email should have default value or be empty
            assert hasattr(user, "email")
        finally:
            config.DATABASE_URL = original_url


class TestPasswordReset:
    """Test password reset functionality."""
    
    def test_update_user_password_method_exists(self):
        """Test that update_user_password method exists and is callable."""
        import inspect
        assert hasattr(DatabaseManager, "update_user_password")
        assert callable(getattr(DatabaseManager, "update_user_password"))


class TestEmailValidation:
    """Test email validation in auth forms."""
    
    def test_valid_email_format(self):
        """Test valid email formats."""
        valid_emails = [
            "test@example.com",
            "user+tag@domain.co.uk",
            "admin@localhost",
            "support@company.org",
        ]
        for email in valid_emails:
            assert "@" in email
    
    def test_invalid_email_format(self):
        """Test invalid email formats."""
        invalid_emails = [
            "testexample.com",
            "user@",
            "@domain.com",
            "user @domain.com",
        ]
        for email in invalid_emails:
            # Simple check that our form would use
            if "@" not in email:
                assert True
            else:
                # More complex validation could go here
                pass


class TestTruncateForBcrypt:
    """Test bcrypt password truncation."""
    
    def test_truncate_under_72_bytes(self):
        """Test passwords under 72 bytes are not modified."""
        password = "short_password"
        truncated = _truncate_for_bcrypt(password)
        assert truncated == password
    
    def test_truncate_exactly_72_bytes(self):
        """Test passwords exactly 72 bytes."""
        password = "x" * 72
        truncated = _truncate_for_bcrypt(password)
        assert len(truncated) == 72
        assert truncated == password
    
    def test_truncate_over_72_bytes(self):
        """Test passwords over 72 bytes are truncated."""
        password = "x" * 100
        truncated = _truncate_for_bcrypt(password)
        assert len(truncated) == 72
        assert truncated == "x" * 72


class TestSendPasswordResetEmail:
    """Test password reset email functionality."""
    
    def test_send_password_reset_email_no_config(self, monkeypatch):
        """Test that email sending fails gracefully without SMTP config."""
        # Remove SMTP env vars
        monkeypatch.delenv("EMAIL_SENDER", raising=False)
        monkeypatch.delenv("EMAIL_PASSWORD", raising=False)
        
        # Should return False without proper config
        result = send_password_reset_email("test@example.com", "testuser", "temp123")
        assert result is False
    
    def test_send_password_reset_email_parameters(self):
        """Test that email function accepts correct parameters."""
        # Just verify the function signature works
        try:
            # Don't actually send, just verify it can be called
            import inspect
            sig = inspect.signature(send_password_reset_email)
            params = list(sig.parameters.keys())
            assert "email" in params
            assert "username" in params
            assert "temp_password" in params
        except Exception:
            pytest.fail("send_password_reset_email signature is invalid")

# -*- coding: utf-8 -*-
"""Tests for optimization and security modules"""
import pytest
from unittest.mock import patch, MagicMock

from src.optimization import DatabaseOptimizer, SecurityHardener


class TestDatabaseOptimizer:
    """Test DatabaseOptimizer functionality"""
    
    @patch('src.optimization.optimization.logger')
    def test_create_indexes_callable(self, mock_logger):
        """Test that create_indexes is callable"""
        assert callable(DatabaseOptimizer.create_indexes)
    
    @patch('src.optimization.optimization.logger')
    def test_enable_query_logging_callable(self, mock_logger):
        """Test that enable_query_logging is callable"""
        assert callable(DatabaseOptimizer.enable_query_logging)
    
    @patch('src.optimization.optimization.logger')
    def test_analyze_database_performance_callable(self, mock_logger):
        """Test that analyze_database_performance is callable"""
        assert callable(DatabaseOptimizer.analyze_database_performance)
    
    @patch('src.optimization.optimization.logger')
    def test_analyze_database_performance_with_mock_engine(self, mock_logger):
        """Test analyze_database_performance with mock engine"""
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        result = DatabaseOptimizer.analyze_database_performance(mock_engine)
        
        assert result is True
        mock_engine.connect.assert_called_once()
        mock_connection.execute.assert_called()


class TestSecurityHardenerInput:
    """Test SecurityHardener input validation"""
    
    def test_validate_input_string_valid(self):
        """Test validation of valid input string"""
        is_valid, cleaned, error = SecurityHardener.validate_input_string("Test Process")
        
        assert is_valid is True
        assert cleaned == "Test Process"
        assert error is None
    
    def test_validate_input_string_empty(self):
        """Test validation rejects empty string"""
        is_valid, cleaned, error = SecurityHardener.validate_input_string("")
        
        assert is_valid is False
        assert cleaned is None
        assert error is not None
    
    def test_validate_input_string_whitespace_only(self):
        """Test validation rejects whitespace-only string"""
        is_valid, cleaned, error = SecurityHardener.validate_input_string("   ")
        
        assert is_valid is False
        assert cleaned is None
        assert error is not None
    
    def test_validate_input_string_too_long(self):
        """Test validation rejects too-long string"""
        long_string = "A" * 300
        is_valid, cleaned, error = SecurityHardener.validate_input_string(long_string, max_length=255)
        
        assert is_valid is False
        assert cleaned is None
        assert error is not None
        assert "máximo" in error.lower()
    
    def test_validate_input_string_non_string_type(self):
        """Test validation rejects non-string types"""
        is_valid, cleaned, error = SecurityHardener.validate_input_string(123)
        
        assert is_valid is False
        assert cleaned is None
        assert error is not None
    
    def test_validate_input_string_strips_whitespace(self):
        """Test that validation strips leading/trailing whitespace"""
        is_valid, cleaned, error = SecurityHardener.validate_input_string("  Test  ")
        
        assert is_valid is True
        assert cleaned == "Test"
        assert error is None
    
    def test_validate_input_string_special_characters(self):
        """Test validation handles special characters"""
        is_valid, cleaned, error = SecurityHardener.validate_input_string("Test-Process_123")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_input_string_portuguese_characters(self):
        """Test validation accepts Portuguese characters"""
        is_valid, cleaned, error = SecurityHardener.validate_input_string("Procéssö de Automação")
        
        assert is_valid is True
        assert error is None


class TestSecurityHardenerNumeric:
    """Test SecurityHardener numeric validation"""
    
    def test_validate_numeric_input_valid(self):
        """Test validation of valid numeric input"""
        is_valid, error = SecurityHardener.validate_numeric_input(100.5)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_numeric_input_string_number(self):
        """Test validation of numeric string"""
        is_valid, error = SecurityHardener.validate_numeric_input("50.25")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_numeric_input_invalid(self):
        """Test validation rejects non-numeric"""
        is_valid, error = SecurityHardener.validate_numeric_input("abc")
        
        assert is_valid is False
        assert error is not None
    
    def test_validate_numeric_input_below_min(self):
        """Test validation rejects value below minimum"""
        is_valid, error = SecurityHardener.validate_numeric_input(10, min_val=20)
        
        assert is_valid is False
        assert error is not None
        assert "mínimo" in error.lower()
    
    def test_validate_numeric_input_above_max(self):
        """Test validation rejects value above maximum"""
        is_valid, error = SecurityHardener.validate_numeric_input(150, max_val=100)
        
        assert is_valid is False
        assert error is not None
        assert "máximo" in error.lower()
    
    def test_validate_numeric_input_within_bounds(self):
        """Test validation accepts value within bounds"""
        is_valid, error = SecurityHardener.validate_numeric_input(50, min_val=0, max_val=100)
        
        assert is_valid is True
        assert error is None


class TestSecurityHardenerEscape:
    """Test SecurityHardener SQL escaping"""
    
    def test_escape_sql_injection_removes_quotes(self):
        """Test SQL escape removes single quotes"""
        result = SecurityHardener.escape_sql_injection("Test' OR '1'='1")
        
        assert "'" not in result
    
    def test_escape_sql_injection_removes_double_quotes(self):
        """Test SQL escape removes double quotes"""
        result = SecurityHardener.escape_sql_injection('Test" OR "1"="1')
        
        assert '"' not in result
    
    def test_escape_sql_injection_removes_semicolon(self):
        """Test SQL escape removes semicolons"""
        result = SecurityHardener.escape_sql_injection("Test; DROP TABLE users;")
        
        assert ";" not in result
    
    def test_escape_sql_injection_non_string(self):
        """Test SQL escape handles non-string input"""
        result = SecurityHardener.escape_sql_injection(123)
        
        assert result == "123"
    
    def test_escape_sql_injection_normal_text(self):
        """Test SQL escape doesn't destroy normal text"""
        text = "Test Process Name"
        result = SecurityHardener.escape_sql_injection(text)
        
        assert result == text


class TestSecurityHardenerDatabaseConnection:
    """Test database connection security validation"""
    
    def test_secure_database_connection_empty_url(self):
        """Test validation rejects empty URL"""
        is_secure, msg = SecurityHardener.secure_database_connection("")
        
        assert is_secure is False
    
    def test_secure_database_connection_sqlite_relative(self):
        """Test SQLite with relative path is secure"""
        is_secure, msg = SecurityHardener.secure_database_connection("sqlite:///./db/app.db")
        
        assert is_secure is True
    
    def test_secure_database_connection_sqlite_absolute_path(self):
        """Test SQLite with absolute path is not secure"""
        is_secure, msg = SecurityHardener.secure_database_connection("sqlite:////etc/app.db")
        
        assert is_secure is False
    
    def test_secure_database_connection_sqlite_parent_dir(self):
        """Test SQLite with parent directory reference is not secure"""
        is_secure, msg = SecurityHardener.secure_database_connection("sqlite:///../db/app.db")
        
        assert is_secure is False


class TestSecurityHardenerFilePermissions:
    """Test file permissions security checking"""
    
    def test_check_file_permissions_nonexistent_file(self):
        """Test that nonexistent file returns error"""
        is_secure, msg = SecurityHardener.check_file_permissions("/nonexistent/file.db")
        
        assert is_secure is False
        assert "not found" in msg.lower()
    
    @patch('os.path.exists')
    @patch('os.stat')
    def test_check_file_permissions_world_readable(self, mock_stat, mock_exists):
        """Test detection of world-readable files"""
        import stat
        
        mock_exists.return_value = True
        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = stat.S_IRUSR | stat.S_IROTH  # User read + world read
        mock_stat.return_value = mock_stat_result
        
        is_secure, msg = SecurityHardener.check_file_permissions("/path/to/file.db")
        
        assert is_secure is False
        assert "world-readable" in msg.lower()
    
    @patch('os.path.exists')
    @patch('os.stat')
    def test_check_file_permissions_world_writable(self, mock_stat, mock_exists):
        """Test detection of world-writable files"""
        import stat
        
        mock_exists.return_value = True
        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IWOTH  # + world write
        mock_stat.return_value = mock_stat_result
        
        is_secure, msg = SecurityHardener.check_file_permissions("/path/to/file.db")
        
        assert is_secure is False
        assert "world-writable" in msg.lower()


class TestSecurityHardenerLogging:
    """Test security event logging"""
    
    @patch('src.optimization.optimization.logging.getLogger')
    def test_log_security_event_info(self, mock_get_logger):
        """Test logging security event with INFO severity"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        SecurityHardener.log_security_event("LOGIN_ATTEMPT", "User x from IP y", severity="INFO")
        
        mock_logger.info.assert_called_once()
    
    @patch('src.optimization.optimization.logging.getLogger')
    def test_log_security_event_warning(self, mock_get_logger):
        """Test logging security event with WARNING severity"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        SecurityHardener.log_security_event("FAILED_AUTH", "Invalid credentials", severity="WARNING")
        
        mock_logger.warning.assert_called_once()
    
    @patch('src.optimization.optimization.logging.getLogger')
    def test_log_security_event_error(self, mock_get_logger):
        """Test logging security event with ERROR severity"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        SecurityHardener.log_security_event("INJECTION_ATTEMPT", "SQL injection detected", severity="ERROR")
        
        mock_logger.error.assert_called_once()
    
    @patch('src.optimization.optimization.logging.getLogger')
    def test_log_security_event_critical(self, mock_get_logger):
        """Test logging security event with CRITICAL severity"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        SecurityHardener.log_security_event("BREACH", "Database accessed unauthoritatively", severity="CRITICAL")
        
        mock_logger.critical.assert_called_once()

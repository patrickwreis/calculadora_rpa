# -*- coding: utf-8 -*-
"""Database optimization and performance enhancements"""
import logging
from sqlalchemy import Index, create_engine, event
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """Database optimization utilities"""
    
    @staticmethod
    def create_indexes(engine):
        """Create database indexes for frequently queried columns"""
        try:
            # Get metadata and create indexes
            from src.models.calculation import Calculation
            
            # Create indexes on frequently queried columns
            indexes = [
                Index('idx_department', Calculation.department),
                Index('idx_complexity', Calculation.complexity),
                Index('idx_created_at', Calculation.created_at),
                Index('idx_status', Calculation.status),
                Index('idx_process_name', Calculation.process_name),
                # Composite indexes for common queries
                Index('idx_dept_created', Calculation.department, Calculation.created_at),
            ]
            
            # Execute CREATE INDEX IF NOT EXISTS for each index
            with engine.begin() as conn:
                for idx in indexes:
                    try:
                        # Create index using raw SQL for better compatibility
                        idx_name = idx.name
                        if idx.name == 'idx_department':
                            conn.execute("CREATE INDEX IF NOT EXISTS idx_department ON calculation(department)")
                        elif idx.name == 'idx_complexity':
                            conn.execute("CREATE INDEX IF NOT EXISTS idx_complexity ON calculation(complexity)")
                        elif idx.name == 'idx_created_at':
                            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON calculation(created_at)")
                        elif idx.name == 'idx_status':
                            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON calculation(status)")
                        elif idx.name == 'idx_process_name':
                            conn.execute("CREATE INDEX IF NOT EXISTS idx_process_name ON calculation(process_name)")
                        elif idx.name == 'idx_dept_created':
                            conn.execute("CREATE INDEX IF NOT EXISTS idx_dept_created ON calculation(department, created_at)")
                    except Exception as e:
                        logger.warning(f"Index {idx.name} might already exist: {str(e)}")
            
            logger.info("Database indexes created/verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
            return False
    
    @staticmethod
    def enable_query_logging(engine, log_level=logging.DEBUG):
        """Enable SQL query logging for debugging"""
        try:
            from sqlalchemy import event
            from sqlalchemy.engine import Engine
            
            @event.listens_for(Engine, "before_cursor_execute")
            def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                if log_level == logging.DEBUG:
                    logger.debug(f"Query: {statement}")
                    if parameters:
                        logger.debug(f"Parameters: {parameters}")
            
            @event.listens_for(Engine, "after_cursor_execute")
            def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                if log_level == logging.DEBUG:
                    logger.debug(f"Execution time: {cursor.rowcount} rows affected")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enabling query logging: {str(e)}")
            return False
    
    @staticmethod
    def analyze_database_performance(engine):
        """Analyze database performance metrics"""
        try:
            with engine.connect() as conn:
                # SQLite PRAGMA commands for optimization
                conn.execute("PRAGMA query_only = OFF")
                conn.execute("PRAGMA synchronous = NORMAL")  # Balance safety and performance
                conn.execute("PRAGMA journal_mode = WAL")     # Write-Ahead Logging for concurrency
                conn.execute("PRAGMA cache_size = -64000")    # 64MB cache
                conn.execute("PRAGMA temp_store = MEMORY")    # Use memory for temp tables
                
                logger.info("Database performance optimizations applied")
                return True
                
        except Exception as e:
            logger.warning(f"Error applying performance optimizations: {str(e)}")
            return False


class SecurityHardener:
    """Security hardening utilities"""
    
    @staticmethod
    def validate_input_string(input_str: str, max_length: int = 255, allowed_chars: str = None) -> tuple:
        """
        Validate and sanitize string input
        
        Args:
            input_str: Input string to validate
            max_length: Maximum allowed length
            allowed_chars: Regex pattern for allowed characters (None = allow all printable)
            
        Returns:
            Tuple[is_valid, cleaned_string, error_message]
        """
        import re
        
        if not isinstance(input_str, str):
            return False, None, "Input deve ser uma string"
        
        if len(input_str) > max_length:
            return False, None, f"Input excede comprimento máximo de {max_length}"
        
        # Remove leading/trailing whitespace
        cleaned = input_str.strip()
        
        if not cleaned:
            return False, None, "Input não pode estar vazio"
        
        # Default: allow alphanumeric, spaces, and common punctuation
        if allowed_chars is None:
            allowed_chars = r'^[\w\s\-.,áéíóúãõâêôç]*$'
        
        if not re.match(allowed_chars, cleaned):
            return False, None, "Input contém caracteres não permitidos"
        
        return True, cleaned, None
    
    @staticmethod
    def escape_sql_injection(value: str) -> str:
        """
        Escape potential SQL injection attempts
        Note: This is for additional safety. SQLAlchemy ORM handles this via parameterized queries.
        
        Args:
            value: String value to escape
            
        Returns:
            Escaped string
        """
        if not isinstance(value, str):
            return str(value)
        
        # SQLAlchemy with parameterized queries handles SQL injection
        # This is an additional layer of defense
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        escaped = value
        
        for char in dangerous_chars:
            escaped = escaped.replace(char, "")
        
        return escaped
    
    @staticmethod
    def secure_database_connection(database_url: str) -> tuple:
        """
        Validate database connection URL is secure
        
        Args:
            database_url: Database connection URL
            
        Returns:
            Tuple[is_secure, message]
        """
        if not database_url:
            return False, "Database URL is required"
        
        # For SQLite, ensure it's local or in a safe directory
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
            # Should be in project directory, not world-writable
            if ".." in db_path or db_path.startswith("/"):
                return False, "Database path must be relative and within project"
            return True, "SQLite database is secure"
        
        # For remote databases, ensure SSL/TLS
        if database_url.startswith(("mysql://", "postgresql://")):
            if "+pymysql" not in database_url and "+psycopg2" not in database_url:
                return False, "Database driver not specified"
            if "ssl" not in database_url.lower():
                return False, "Remote database must use SSL/TLS"
            return True, "Remote database connection is secure"
        
        return True, "Database URL format recognized"
    
    @staticmethod
    def check_file_permissions(file_path: str) -> tuple:
        """
        Check file permissions security
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple[is_secure, message]
        """
        import os
        import stat
        
        try:
            if not os.path.exists(file_path):
                return False, f"File not found: {file_path}"
            
            # Get file stats
            file_stat = os.stat(file_path)
            file_mode = file_stat.st_mode
            
            # Check if world-readable (for sensitive files like DB)
            if file_mode & stat.S_IROTH:
                return False, "File is world-readable - consider restricting permissions"
            
            # Check if world-writable
            if file_mode & stat.S_IWOTH:
                return False, "File is world-writable - this is a security risk"
            
            return True, "File permissions are secure"
            
        except Exception as e:
            return False, f"Error checking permissions: {str(e)}"
    
    @staticmethod
    def validate_numeric_input(value, min_val=None, max_val=None) -> tuple:
        """
        Validate numeric input against bounds
        
        Args:
            value: Numeric value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Tuple[is_valid, error_message]
        """
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return False, "Input deve ser um número"
        
        if min_val is not None and num_value < min_val:
            return False, f"Valor mínimo permitido: {min_val}"
        
        if max_val is not None and num_value > max_val:
            return False, f"Valor máximo permitido: {max_val}"
        
        return True, None
    
    @staticmethod
    def log_security_event(event_type: str, details: str, severity: str = "INFO"):
        """
        Log security-related events
        
        Args:
            event_type: Type of security event
            details: Event details
            severity: Log severity level
        """
        security_logger = logging.getLogger("security")
        
        message = f"[{event_type}] {details}"
        
        if severity == "CRITICAL":
            security_logger.critical(message)
        elif severity == "ERROR":
            security_logger.error(message)
        elif severity == "WARNING":
            security_logger.warning(message)
        else:
            security_logger.info(message)

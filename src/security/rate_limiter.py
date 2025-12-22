# -*- coding: utf-8 -*-
"""Rate limiting para proteção contra brute force attacks."""
import time
from typing import Dict
from datetime import datetime, timedelta
import threading


class RateLimiter:
    """Simple in-memory rate limiter para proteção contra brute force.
    
    Para produção, considere usar Redis para distribução entre múltiplas instâncias.
    """
    
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        """
        Args:
            max_attempts: Máximo de tentativas permitidas
            window_seconds: Janela de tempo em segundos
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts: Dict[str, list] = {}
        self._lock = threading.Lock()
    
    def is_rate_limited(self, key: str) -> bool:
        """Verifica se a chave está rate limitada.
        
        Args:
            key: Identificador único (ex: email, IP address)
            
        Returns:
            True se rate limitado, False caso contrário
        """
        with self._lock:
            now = time.time()
            
            # Limpar tentativas antigas
            if key in self.attempts:
                cutoff = now - self.window_seconds
                self.attempts[key] = [
                    timestamp for timestamp in self.attempts[key]
                    if timestamp > cutoff
                ]
            
            # Verificar limite
            if key not in self.attempts:
                self.attempts[key] = []
            
            if len(self.attempts[key]) >= self.max_attempts:
                return True
            
            return False
    
    def record_attempt(self, key: str) -> None:
        """Registra uma tentativa.
        
        Args:
            key: Identificador único
        """
        with self._lock:
            now = time.time()
            if key not in self.attempts:
                self.attempts[key] = []
            self.attempts[key].append(now)
    
    def reset(self, key: str) -> None:
        """Limpa histórico de tentativas (usado após login bem-sucedido).
        
        Args:
            key: Identificador único
        """
        with self._lock:
            if key in self.attempts:
                del self.attempts[key]
    
    def get_remaining_attempts(self, key: str) -> int:
        """Retorna tentativas restantes.
        
        Args:
            key: Identificador único
            
        Returns:
            Número de tentativas restantes
        """
        with self._lock:
            now = time.time()
            
            if key in self.attempts:
                cutoff = now - self.window_seconds
                self.attempts[key] = [
                    timestamp for timestamp in self.attempts[key]
                    if timestamp > cutoff
                ]
                return max(0, self.max_attempts - len(self.attempts[key]))
            
            return self.max_attempts
    
    def get_reset_time(self, key: str) -> int:
        """Retorna segundos até reset do rate limit.
        
        Args:
            key: Identificador único
            
        Returns:
            Segundos até poder tentar novamente
        """
        with self._lock:
            if key not in self.attempts or not self.attempts[key]:
                return 0
            
            oldest_attempt = self.attempts[key][0]
            reset_time = oldest_attempt + self.window_seconds - time.time()
            return max(0, int(reset_time))


# Global rate limiter instances
_login_limiter = RateLimiter(max_attempts=5, window_seconds=300)  # 5 tentativas em 5 min
_password_reset_limiter = RateLimiter(max_attempts=3, window_seconds=600)  # 3 tentativas em 10 min


def get_login_limiter() -> RateLimiter:
    """Retorna o rate limiter para login."""
    return _login_limiter


def get_password_reset_limiter() -> RateLimiter:
    """Retorna o rate limiter para recuperação de senha."""
    return _password_reset_limiter

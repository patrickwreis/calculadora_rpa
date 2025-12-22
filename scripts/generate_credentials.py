#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para gerar credenciais seguras para .env"""
import secrets
import string


def generate_secure_password(length: int = 32) -> str:
    """Gera uma senha criptograficamente segura."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


def generate_config():
    """Gera configuração segura para .env"""
    username = "admin_" + secrets.token_hex(4)
    password = generate_secure_password()
    
    print("\n" + "=" * 60)
    print("🔐 GERADOR DE CREDENCIAIS SEGURAS - ROI RPA CALCULATOR")
    print("=" * 60)
    print("\nAdicione as seguintes linhas ao seu arquivo .env:\n")
    print("# ===== AUTHENTICATION (Gerado em:", __import__('datetime').datetime.now().isoformat(), ")")
    print(f"AUTH_USERNAME={username}")
    print(f"AUTH_PASSWORD={password}")
    print("AUTH_EMAIL=seu_email_admin@seudominio.com")
    print("\n" + "=" * 60)
    print("⚠️  IMPORTANTE:")
    print("  1. Guarde essas credenciais em local seguro")
    print("  2. Nunca commite o arquivo .env para Git")
    print("  3. Use credenciais diferentes para cada ambiente")
    print("  4. Troque a senha após o primeiro login")
    print("=" * 60 + "\n")
    
    # Salvar opcionalmente em arquivo
    save = input("Deseja salvar estas credenciais em .env.local? (s/n): ").strip().lower()
    if save == 's':
        with open('.env.local', 'w') as f:
            f.write(f"AUTH_USERNAME={username}\n")
            f.write(f"AUTH_PASSWORD={password}\n")
            f.write("AUTH_EMAIL=seu_email_admin@seudominio.com\n")
        print("✅ Credenciais salvas em .env.local (ignore este arquivo no git!)")


if __name__ == "__main__":
    generate_config()

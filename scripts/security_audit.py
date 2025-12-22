#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auditoria de Segurança - Busca por credenciais hardcoded no projeto.

Este script verifica o codebase procurando por:
- Senhas hardcoded
- API keys e tokens
- Mensagens de aviso ignoradas
- Configurações inseguras
"""
import os
import re
from pathlib import Path

# Padrões perigosos a procurar
DANGEROUS_PATTERNS = [
    (r"admin\s*=\s*['\"]admin['\"]", "Senha hardcoded: admin=admin"),
    (r"password\s*=\s*['\"][^'\"]{1,20}['\"]", "Senha em texto plano"),
    (r"api_?key\s*=\s*['\"]sk-", "API Key hardcoded"),
    (r"token\s*=\s*['\"][\w\-]{20,}", "Token hardcoded"),
    (r"secret\s*=\s*['\"]", "Secret key hardcoded"),
    (r"AUTH_PASSWORD\s*=\s*['\"](?!YOUR_)", "Senha no código"),
]

# Diretórios a ignorar
IGNORE_DIRS = {
    '.git', '.venv', '__pycache__', '.pytest_cache', 
    'node_modules', 'dist', 'build', '.streamlit'
}

def scan_file(filepath: Path) -> list:
    """Escaneia um arquivo em busca de padrões perigosos."""
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                for pattern, description in DANGEROUS_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        findings.append({
                            'file': str(filepath),
                            'line': line_num,
                            'pattern': description,
                            'content': line.strip()[:100]
                        })
    except (UnicodeDecodeError, PermissionError):
        pass
    return findings

def audit_project(project_root: str = ".") -> None:
    """Executa auditoria completa de segurança."""
    project_path = Path(project_root)
    all_findings = []
    
    print("\n" + "=" * 70)
    print("🔍 AUDITORIA DE SEGURANÇA - ROI RPA CALCULATOR")
    print("=" * 70)
    print("Procurando por credenciais hardcoded e segredos...\n")
    
    # Escanear arquivos Python
    for py_file in project_path.rglob("*.py"):
        # Ignorar diretórios
        if any(part in py_file.parts for part in IGNORE_DIRS):
            continue
        
        findings = scan_file(py_file)
        if findings:
            all_findings.extend(findings)
    
    # Escanear arquivos de configuração
    config_patterns = ["*.env", "*.json", "*.yaml", "*.yml", "*.conf", "*.config"]
    for pattern in config_patterns:
        for config_file in project_path.rglob(pattern):
            if any(part in config_file.parts for part in IGNORE_DIRS):
                continue
            if config_file.name == ".env":  # Verificar mas não commitar
                continue
            
            findings = scan_file(config_file)
            if findings:
                all_findings.extend(findings)
    
    # Exibir resultados
    if all_findings:
        print("⚠️  PROBLEMAS ENCONTRADOS:\n")
        for finding in all_findings:
            print(f"  📄 {finding['file']}:{finding['line']}")
            print(f"     ⚠️  {finding['pattern']}")
            print(f"     → {finding['content'][:80]}")
            print()
    else:
        print("✅ NENHUM SEGREDO HARDCODED DETECTADO")
    
    # Checklist de verificação manual
    print("\n" + "=" * 70)
    print("📋 CHECKLIST DE VERIFICAÇÃO MANUAL")
    print("=" * 70)
    
    checklist = [
        "[ ] Arquivo .env não está versionado (verificar .gitignore)",
        "[ ] Não há senhas padrão como 'admin/admin' no código",
        "[ ] Variáveis AUTH_* vêm do .env, não de defaults",
        "[ ] Rate limiting está ativo na autenticação",
        "[ ] Senhas são hasheadas com bcrypt",
        "[ ] Sessions usam tokens JWT com expiração",
        "[ ] Logs não expõem informações sensíveis",
        "[ ] HTTPS obrigatório em produção",
        "[ ] Cookies com flags Secure, HttpOnly, SameSite",
        "[ ] Database URL não contém senha hardcoded",
    ]
    
    for item in checklist:
        print(f"\n{item}")
    
    print("\n" + "=" * 70)
    print("Para gerar credenciais seguras:")
    print("  python scripts/generate_credentials.py")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    audit_project()

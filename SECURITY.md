# 🔐 Guia de Segurança - ROI RPA Calculator

## 1. Configuração Inicial de Credenciais

### ⚠️ NUNCA use credenciais padrão (admin/admin)

Ao configurar o sistema pela primeira vez:

```bash
# Gere credenciais seguras
python scripts/generate_credentials.py

# Copie a saída para seu arquivo .env
cp .env.example .env
# Edite .env com as credenciais geradas
nano .env
```

### Estrutura do .env

```env
AUTH_REQUIRED=true
AUTH_USERNAME=seu_admin_username
AUTH_PASSWORD=sua_senha_segura
AUTH_EMAIL=admin@seudominio.com
```

## 2. Proteção contra Brute Force

O sistema implementa **rate limiting automático**:

- **Login**: Máximo 5 tentativas a cada 5 minutos por usuário
- **Recuperação de Senha**: Máximo 3 tentativas a cada 10 minutos por email

Usuários bloqueados verão:
```
❌ Muitas tentativas de login. Tente novamente em XXX segundos.
```

## 3. Segurança de Cookies

### Produção (HTTPS obrigatório)

Adicione ao .env:

```env
STREAMLIT_CLIENT_SSL_CERTIFICATE_FILE=/caminho/para/cert.pem
STREAMLIT_CLIENT_SSL_KEY_FILE=/caminho/para/key.pem
```

Configure no arquivo `~/.streamlit/config.toml`:

```toml
[client]
showWarningOnDirectExecution = false

[server]
port = 443
sslKeyFile = "/caminho/para/key.pem"
sslCertFile = "/caminho/para/cert.pem"
headless = true
```

## 4. Checklist de Segurança para Produção

- [ ] Senhas admin alteradas do padrão
- [ ] HTTPS configurado (certificado SSL/TLS)
- [ ] Rate limiting verificado
- [ ] Arquivo .env adicionado a .gitignore
- [ ] Backups automáticos configurados
- [ ] Logs de acesso monitorizados
- [ ] Senha AUTH_PASSWORD nunca commitada
- [ ] Firewall configurado (apenas IPs necessários)

## 5. Boas Práticas de Senha

### Requisitos Mínimos
- ✅ Mínimo 8 caracteres
- ✅ Conter letras maiúsculas E minúsculas
- ✅ Conter números
- ✅ Conter símbolos especiais (!@#$%^&*)

### Gerar Senha Segura
```python
import secrets
senha = secrets.token_urlsafe(32)  # 32 caracteres
print(senha)
```

## 6. Migração de SQLite para PostgreSQL (Recomendado)

Para produção, migre de SQLite para PostgreSQL:

```bash
# 1. Instale PostgreSQL
# 2. Crie banco de dados
createdb roi_calculator

# 3. Configure a connection string
DATABASE_URL=postgresql://user:password@localhost:5432/roi_calculator

# 4. Execute migrations
alembic upgrade head
```

## 7. Monitoramento de Segurança

### Logs Críticos a Monitorar

```
- Tentativas de login falhadas (múltiplas)
- Rate limiting acionado
- Erros de autenticação
- Alterações de senha
```

### Alertas Recomendados

Implemente alertas para:
- 10+ tentativas de login falhadas em 1 hora
- Taxa de erro > 5% em 15 minutos
- Tentativas de SQL injection detectadas

## 8. Verificação de Conformidade

Antes de deployar, execute:

```bash
# Verificar se .env está no .gitignore
grep "^.env" .gitignore

# Verificar se há hardcoded passwords
grep -r "admin.*admin" --include="*.py"

# Verificar se credenciais estão nos commits
git log --all --name-only --oneline | grep ".env"
```

## 9. Resposta a Incidentes

Se suspeitar de comprometimento:

1. **Imediatamente**: Mude a senha do admin
2. **Dentro de 1 hora**: Audite logs de acesso
3. **Dentro de 4 horas**: Verifique se dados foram exfiltrados
4. **Dentro de 24 horas**: Faça backup e reexamine banco de dados

## 10. Recursos Adicionais

- [OWASP Top 10](https://owasp.org/Top10/)
- [Python bcrypt best practices](https://github.com/pyca/bcrypt)
- [Streamlit security docs](https://docs.streamlit.io/library/advanced-features/secrets-management)

---

**Última atualização**: 22/12/2025  
**Versão**: 1.0.0

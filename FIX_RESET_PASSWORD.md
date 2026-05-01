# 🔧 Correção Rápida - Reset de Senha

## 🎯 Problema

Token de reset inválido porque as colunas não existem no banco do Railway.

## ✅ Solução em 3 Passos

### Passo 1: Verificar Estado do Banco

Acesse no navegador:
```
https://seu-app.railway.app/debug/db-schema
```

**Se retornar**:
```json
{
  "has_reset_columns": false,
  "migration_needed": true
}
```

Significa que a migração NÃO foi executada. Continue para o Passo 2.

**Se retornar**:
```json
{
  "has_reset_columns": true,
  "migration_needed": false
}
```

Significa que a migração JÁ foi executada. O problema é outro (veja Passo 3).

### Passo 2: Executar Migração

#### Opção A: Force Novo Deploy (RECOMENDADO)

```bash
# Commit os novos arquivos
git add .
git commit -m "feat: add db migration and debug endpoint"
git push
```

O Railway fará deploy automaticamente e executará a migração no startup.

#### Opção B: Via Railway CLI

```bash
# Instalar CLI (se não tiver)
npm i -g @railway/cli

# Login
railway login

# Conectar ao projeto
railway link

# Executar migração
railway run python migrate_railway.py
```

#### Opção C: Redeploy Manual

1. Acesse: https://railway.app/
2. Selecione seu projeto
3. Clique em "Deployments"
4. Clique em "Redeploy" no último deploy

### Passo 3: Verificar Novamente

Após executar a migração, acesse novamente:
```
https://seu-app.railway.app/debug/db-schema
```

Deve retornar:
```json
{
  "has_reset_columns": true,
  "migration_needed": false,
  "users_columns": {
    "id": "INTEGER",
    "name": "VARCHAR(255)",
    "username": "VARCHAR(100)",
    "password": "VARCHAR(255)",
    "role": "VARCHAR(20)",
    "active": "INTEGER",
    "created_at": "DATETIME",
    "email": "TEXT",
    "reset_token": "TEXT",
    "reset_token_expiry": "TEXT"
  }
}
```

### Passo 4: Testar Reset de Senha

1. Acesse: `https://seu-app.railway.app/forgot-password`
2. Digite o email: `brrasantos@gmail.com`
3. Clique em "Enviar"
4. Verifique o email (pode estar no spam)
5. Clique no link
6. **Deve funcionar agora!** ✅

## 🐛 Se Ainda Não Funcionar

### Problema: Usuário não tem email cadastrado

1. Acesse: `https://seu-app.railway.app/admin/users`
2. Login: `admin` / `admin123`
3. Edite o usuário
4. **Adicione o email**: `brrasantos@gmail.com`
5. Salve
6. Tente resetar a senha novamente

### Problema: Token expira muito rápido

O token expira em **1 hora**. Se você demorar mais que isso, precisará:
1. Solicitar novo reset
2. Usar o novo link rapidamente

### Problema: Email não chega

Veja o arquivo [`GMAIL_TROUBLESHOOTING.md`](GMAIL_TROUBLESHOOTING.md:1) para soluções.

## 📝 Checklist Completo

- [ ] Commit e push dos arquivos novos
- [ ] Deploy no Railway concluído
- [ ] Acesse `/debug/db-schema` e verifique `has_reset_columns: true`
- [ ] Usuário tem email em `/admin/users`
- [ ] Solicite reset de senha
- [ ] Email chega (verifique spam)
- [ ] Link de reset funciona
- [ ] Senha é alterada com sucesso

## 🎉 Após Funcionar

Você pode remover o endpoint de debug por segurança:

1. Comente ou delete as linhas 217-237 do [`main.py`](pitch_app/main.py:217)
2. Commit e push
3. O endpoint `/debug/db-schema` não estará mais disponível

## 💡 Resumo

1. **Verifique**: `/debug/db-schema`
2. **Migre**: Commit + push (ou Railway CLI)
3. **Teste**: Reset de senha
4. **Sucesso**: ✅

**Tempo estimado**: 5-10 minutos
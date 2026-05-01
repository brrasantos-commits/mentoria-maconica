# 🔧 Guia de Migração do Banco de Dados no Railway

## 🎯 Problema

O token de reset de senha está sendo marcado como inválido porque as colunas `reset_token` e `reset_token_expiry` não existem no banco de dados do Railway.

**Log do erro**:
```
WARNING - Invalid reset token used: 559bb2a01a174320a16de586524940d4
```

## ✅ Solução

Execute o script de migração no Railway para adicionar as colunas necessárias.

## 📋 Passo a Passo

### Opção 1: Via Railway CLI (Recomendado)

1. **Instale o Railway CLI** (se ainda não tiver):
   ```bash
   npm i -g @railway/cli
   ```

2. **Faça login no Railway**:
   ```bash
   railway login
   ```

3. **Conecte ao projeto**:
   ```bash
   railway link
   ```
   Selecione seu projeto da lista.

4. **Execute o script de migração**:
   ```bash
   railway run python migrate_railway.py
   ```

5. **Verifique a saída**:
   ```
   🔄 Iniciando migrações do banco de dados...
   📦 Inicializando banco de dados...
   ✅ Banco inicializado
   🔧 Executando migrações...
   ✅ Migrações concluídas com sucesso!
   
   ✨ Banco de dados atualizado!
   ```

### Opção 2: Force Novo Deploy (Mais Simples)

O script `migrate_db()` já é executado no startup da aplicação (linha 107 do `main.py`).

**Mas pode não ter funcionado se:**
- O deploy foi feito antes das migrações serem adicionadas
- Houve erro durante o startup

**Solução**: Force um novo deploy:

1. **Faça um commit e push**:
   ```bash
   git add migrate_railway.py RAILWAY_MIGRATION_GUIDE.md
   git commit -m "feat: add migration script for reset password"
   git push
   ```

2. **Aguarde o deploy** e verifique os logs no Railway:
   ```
   2026-05-01 XX:XX:XX - pitch_app.main - INFO - Starting application...
   2026-05-01 XX:XX:XX - pitch_app.main - INFO - Application started successfully
   ```

3. **Teste o reset de senha** novamente.

### Opção 3: Via Railway Dashboard

1. **Acesse**: https://railway.app/

2. **Selecione seu projeto** > **Service**

3. **Clique em "Deployments"**

4. **Clique em "Redeploy"** no último deploy

5. **Aguarde** e verifique os logs

## 🔍 Verificar se Funcionou

Após executar a migração, teste o reset de senha:

1. Acesse: `https://seu-app.railway.app/forgot-password`
2. Digite um email cadastrado (ex: `brrasantos@gmail.com`)
3. Clique em "Enviar"
4. Verifique o email (pode estar no spam)
5. Clique no link de reset
6. **Deve funcionar agora!** ✅

Se ainda der erro, verifique os logs do Railway para ver se a migração foi executada.

## 📊 O Que a Migração Faz

O script `migrate_db()` adiciona as seguintes colunas à tabela `users`:

```sql
ALTER TABLE users ADD COLUMN email TEXT
ALTER TABLE users ADD COLUMN reset_token TEXT
ALTER TABLE users ADD COLUMN reset_token_expiry TEXT
```

E cria os seguintes índices para performance:

```sql
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
CREATE INDEX IF NOT EXISTS idx_users_reset_token ON users(reset_token)
```

## ⚠️ Importante

- **A migração é segura**: Usa `IF NOT EXISTS` para não duplicar colunas
- **Não perde dados**: Apenas adiciona colunas novas
- **Pode executar múltiplas vezes**: É idempotente (não causa problemas)

## 🐛 Troubleshooting

### Erro: "Invalid reset token used"

**Causa**: Colunas `reset_token` e `reset_token_expiry` não existem no banco.

**Solução**: Execute a migração usando uma das opções acima.

### Erro: "no such column: users.reset_token"

**Causa**: Migração não foi executada.

**Solução**: 
1. Force um novo deploy (Opção 2)
2. Ou execute manualmente via Railway CLI (Opção 1)

### Migração executada mas ainda não funciona

**Verifique**:
1. Os logs do Railway mostram "Application started successfully"?
2. O email está cadastrado no banco? (Vá em `/admin/users` e verifique)
3. O email tem o campo preenchido?

**Se o usuário não tem email**:
1. Acesse: `https://seu-app.railway.app/admin/users`
2. Edite o usuário
3. Adicione o email
4. Salve
5. Tente resetar a senha novamente

## 📝 Checklist

- [ ] Commit e push do código atualizado
- [ ] Deploy no Railway concluído
- [ ] Logs mostram "Application started successfully"
- [ ] Usuário tem email cadastrado em `/admin/users`
- [ ] Teste de reset de senha funciona
- [ ] Email chega (verifique spam)
- [ ] Link de reset funciona

## 🎉 Próximos Passos

Após a migração funcionar:

1. **Cadastre emails** para todos os usuários em `/admin/users`
2. **Teste** o fluxo completo de reset de senha
3. **Configure SendGrid Domain Authentication** para emails não irem para spam
4. **Aumente o volume** do Railway para 5-10GB (para uploads de vídeo)

## 💡 Dica

Se você deletar o volume do Railway e criar um novo, precisará executar a migração novamente, pois o banco de dados será recriado do zero.
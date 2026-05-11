# 🚂 Guia de Deploy no Railway - Sales Pitch AI V4

## ✅ Status: PRONTO PARA DEPLOY

Todas as melhorias foram aplicadas e o código está pronto para produção no Railway.

## 📋 Pré-requisitos

1. Conta no Railway (https://railway.app)
2. Repositório GitHub conectado
3. Chave da API OpenAI

## 🚀 Passo a Passo para Deploy

### 1. Preparar o Repositório

```bash
# Certifique-se de que todos os arquivos estão commitados
git add .
git commit -m "feat: aplicar melhorias de segurança, performance e arquitetura v4"
git push origin main
```

### 2. Criar Projeto no Railway

1. Acesse https://railway.app
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha o repositório `brrasantos-commits/sales-pitch-ai`
5. Railway detectará automaticamente o Dockerfile

### 3. Configurar Variáveis de Ambiente

No painel do Railway, vá em **Variables** e adicione:

#### ⚠️ OBRIGATÓRIAS

```env
OPENAI_API_KEY=sk-sua-chave-aqui
SESSION_SECRET_KEY=gere-uma-chave-segura-aqui
```

**Gerar SESSION_SECRET_KEY segura:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 📝 OPCIONAIS (com valores padrão)

```env
OPENAI_MODEL=gpt-4o-mini
OPENAI_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe
MAX_VIDEO_SIZE_MB=70
MAX_TEXT_CHARS_PER_MATERIAL=4000
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
```

#### 📧 EMAIL (para reset de senha)

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app-gmail
SMTP_FROM=noreply@seudominio.com
```

### 4. Configurar Volume Persistente (Importante!)

O Railway precisa de um volume para persistir o banco de dados:

1. No painel do projeto, clique em **Settings**
2. Vá para **Volumes**
3. Clique em **Add Volume**
4. Configure:
   - **Mount Path**: `/app/data`
   - **Size**: 1GB (ou mais, conforme necessário)

### 5. Deploy

1. Railway iniciará o deploy automaticamente
2. Aguarde o build completar (2-5 minutos)
3. Acesse a URL gerada pelo Railway

## 🔍 Verificar Deploy

### Health Check

Acesse: `https://seu-app.railway.app/health`

Resposta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "version": "4.0"
}
```

### Login

Acesse: `https://seu-app.railway.app/login`

**Usuários padrão:**
- Admin: `admin` / `admin123`
- Vendedor: `vendedor` / `123456`

⚠️ **IMPORTANTE**: Altere essas senhas imediatamente após o primeiro login!

## 📊 Monitoramento

### Logs

No painel do Railway:
1. Clique no seu serviço
2. Vá para **Deployments**
3. Clique no deployment ativo
4. Veja os logs em tempo real

### Métricas

Railway fornece automaticamente:
- CPU usage
- Memory usage
- Network traffic
- Request count

## 🔧 Troubleshooting

### Erro: "SESSION_SECRET_KEY must be set"

**Solução**: Adicione a variável de ambiente no Railway:
```
SESSION_SECRET_KEY=<sua-chave-gerada>
```

### Erro: "OPENAI_API_KEY not found"

**Solução**: Adicione sua chave da OpenAI nas variáveis de ambiente.

### Banco de dados não persiste

**Solução**: Verifique se o volume está montado em `/app/data`

### Aplicação não inicia

**Solução**: Verifique os logs no Railway para identificar o erro específico.

### Rate Limiting muito restritivo

**Solução**: Ajuste os limites no código se necessário:
- Login: 5 tentativas/minuto (linha 235 do main.py)
- Reset senha: 3 tentativas/hora (linha 271 do main.py)

## 🔐 Segurança em Produção

### 1. Alterar Senhas Padrão

Após o primeiro deploy, altere as senhas dos usuários padrão:

```sql
-- Conecte ao banco via Railway CLI ou interface
UPDATE users SET password = '<nova-senha-hasheada>' WHERE username = 'admin';
UPDATE users SET password = '<nova-senha-hasheada>' WHERE username = 'vendedor';
```

Ou use a interface de admin para criar novos usuários e desativar os padrão.

### 2. Configurar Domínio Customizado

1. No Railway, vá em **Settings** > **Domains**
2. Adicione seu domínio customizado
3. Configure os registros DNS conforme instruído

### 3. Habilitar HTTPS

Railway fornece HTTPS automaticamente para todos os domínios.

### 4. Backup do Banco de Dados

Configure backups regulares do volume `/app/data`:

```bash
# Usando Railway CLI
railway run python -c "import shutil; shutil.copy('/app/data/pitch_app.db', '/app/data/backup.db')"
```

## 📈 Escalabilidade

### Aumentar Recursos

No Railway:
1. Vá em **Settings** > **Resources**
2. Ajuste CPU e Memory conforme necessário
3. Railway cobra por uso

### Múltiplas Instâncias

Para alta disponibilidade:
1. Configure um banco de dados externo (PostgreSQL)
2. Atualize `db.py` para usar PostgreSQL
3. Habilite múltiplas réplicas no Railway

## 🔄 Atualizações

### Deploy Automático

Railway faz deploy automático a cada push no GitHub:

```bash
git add .
git commit -m "feat: nova funcionalidade"
git push origin main
# Railway detecta e faz deploy automaticamente
```

### Rollback

Se algo der errado:
1. No Railway, vá em **Deployments**
2. Encontre o deployment anterior estável
3. Clique em **Redeploy**

## 📝 Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Volume persistente criado e montado
- [ ] Health check respondendo
- [ ] Login funcionando
- [ ] Upload de vídeo funcionando
- [ ] Análise de pitch funcionando
- [ ] Senhas padrão alteradas
- [ ] Logs sendo gerados corretamente
- [ ] Email de reset funcionando (se configurado)

## 🆘 Suporte

### Logs Detalhados

Para ver logs mais detalhados, adicione:
```env
LOG_LEVEL=DEBUG
```

### Railway CLI

Instale para acesso direto:
```bash
npm install -g @railway/cli
railway login
railway link
railway logs
```

## 🎉 Deploy Completo!

Sua aplicação está rodando em produção com:
- ✅ Segurança aprimorada (bcrypt, rate limiting)
- ✅ Performance otimizada (cache, connection pooling)
- ✅ Arquitetura modular (serviços separados)
- ✅ Logging estruturado
- ✅ Monitoramento (health check)
- ✅ Tratamento de erros robusto

**URL da aplicação**: `https://seu-app.railway.app`

---

**Versão**: 4.0  
**Última atualização**: 2024  
**Status**: ✅ Produção Ready
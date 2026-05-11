# Sales Pitch AI V4 - Versão Melhorada

Versão 4.0 do app com melhorias significativas em **segurança**, **performance**, **arquitetura** e **manutenibilidade**.

## 🆕 Novidades da V4

### Segurança
- ✅ Senhas hasheadas com bcrypt
- ✅ Secret key obrigatória
- ✅ Rate limiting em endpoints críticos
- ✅ Validação de entrada com Pydantic
- ✅ Logs de auditoria

### Performance
- ✅ Connection pooling otimizado
- ✅ Cache LRU para consultas frequentes
- ✅ Índices de banco de dados
- ✅ Validação otimizada de uploads

### Arquitetura
- ✅ Camada de serviços separada
- ✅ Dependency injection
- ✅ Logging estruturado
- ✅ Exception handling global

## 📋 Pré-requisitos

- Docker e Docker Compose
- Chave da API OpenAI

## 🚀 Como rodar

### 1. Configuração Inicial

```bash
# Clone o repositório
git clone <seu-repo>
cd sales-pitch-ai-v4

# Copie o arquivo de exemplo
cp .env.example .env
```

### 2. Configure as Variáveis de Ambiente

Edite o arquivo `.env` e preencha:

```env
# OBRIGATÓRIO
OPENAI_API_KEY=sk-sua-chave-aqui
SESSION_SECRET_KEY=gere-uma-chave-aleatoria-segura-aqui

# OPCIONAL (valores padrão)
OPENAI_MODEL=gpt-4o-mini
MAX_VIDEO_SIZE_MB=70
```

**⚠️ IMPORTANTE**: Gere uma secret key segura:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Inicie a Aplicação

```bash
# Limpe containers antigos (se existirem)
docker compose down --rmi all -v --remove-orphans

# Build e inicie
docker compose build --no-cache
docker compose up
```

### 4. Acesse a Aplicação

Abra seu navegador em: `http://localhost:8002`

## 👥 Usuários Padrão

### Admin
- **Usuário**: `admin`
- **Senha**: `admin123`
- **Acesso**: Painel administrativo

### Vendedor
- **Usuário**: `vendedor`
- **Senha**: `123456`
- **Acesso**: Interface de estudo e pitch

**⚠️ IMPORTANTE**: Altere essas senhas em produção!

## 📁 Estrutura do Projeto

```
sales-pitch-ai-v4/
├── pitch_app/
│   ├── services/           # Camada de serviços
│   │   ├── auth_service.py         # Autenticação
│   │   ├── material_service.py     # Materiais
│   │   ├── session_service.py      # Sessão
│   │   ├── validation_models.py    # Validação
│   │   ├── evaluation_service.py   # Avaliação
│   │   ├── openai_service.py       # OpenAI
│   │   └── ...
│   ├── templates/          # Templates HTML
│   ├── static/            # Arquivos estáticos
│   ├── main.py            # Aplicação principal
│   ├── db.py              # Configuração do banco
│   └── models.py          # Modelos de dados
├── data/                  # Dados persistentes (criado automaticamente)
│   ├── pitch_app.db      # Banco de dados SQLite
│   ├── materials/        # Materiais de estudo
│   └── uploads/          # Uploads de vídeos
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente Completas

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe

# Segurança
SESSION_SECRET_KEY=sua-chave-secreta

# Limites
MAX_VIDEO_SIZE_MB=70
MAX_TEXT_CHARS_PER_MATERIAL=4000

# Áudio
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1

# Diretórios
APP_DATA_DIR=/app/data

# Email (para reset de senha)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
SMTP_FROM=noreply@example.com
```

## 🛡️ Segurança

### Rate Limiting

A aplicação implementa rate limiting para proteger contra ataques:

- **Login**: 5 tentativas por minuto
- **Reset de senha**: 3 tentativas por hora

### Senhas

- Todas as senhas são hasheadas com bcrypt (custo 12)
- Tokens de reset expiram em 1 hora
- Validação de força de senha implementada

### Logs de Auditoria

Todos os eventos de autenticação são logados:
- Tentativas de login (sucesso/falha)
- Criação de usuários
- Reset de senhas
- Alterações de senha

## 📊 Performance

### Otimizações Implementadas

1. **Connection Pooling**
   - Pool size: 10 conexões
   - Max overflow: 20 conexões
   - Pre-ping habilitado

2. **Cache**
   - LRU cache para opções de filtro
   - Invalidação automática em mudanças

3. **Índices de Banco**
   - materials(active, industry, solution, sort_order)
   - users(username, email, reset_token)

4. **Validação Otimizada**
   - Verificação de tamanho via headers
   - Streaming de uploads

## 🔍 Monitoramento

### Health Check

Endpoint disponível em: `GET /health`

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "version": "4.0"
}
```

### Logs

Logs estruturados com níveis:
- INFO: Operações normais
- WARNING: Situações suspeitas
- ERROR: Erros que precisam atenção

Visualize os logs:
```bash
docker compose logs -f web
```

## 🧪 Desenvolvimento

### Executar Localmente (sem Docker)

```bash
# Instale as dependências
pip install -r requirements.txt

# Configure o .env
cp .env.example .env

# Execute
python -m uvicorn pitch_app.main:app --reload --host 0.0.0.0 --port 8000
```

### Estrutura de Serviços

A aplicação segue uma arquitetura em camadas:

1. **Rotas** (`main.py`, `admin_routes.py`)
   - Recebem requests HTTP
   - Validam entrada
   - Chamam serviços

2. **Serviços** (`services/`)
   - Lógica de negócio
   - Interação com banco
   - Processamento de dados

3. **Modelos** (`models.py`, `validation_models.py`)
   - Estrutura de dados
   - Validação de entrada

## 📝 Migrações de Banco

As migrações são executadas automaticamente no startup:

- Adiciona colunas faltantes
- Cria índices
- Atualiza estrutura

Para forçar recriação do banco:
```bash
docker compose down -v
docker compose up
```

## 🐛 Troubleshooting

### Erro: "SESSION_SECRET_KEY must be set"

**Solução**: Configure a variável no `.env`:
```bash
SESSION_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
```

### Erro: "OPENAI_API_KEY not found"

**Solução**: Adicione sua chave no `.env`:
```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

### Porta 8002 já em uso

**Solução**: Altere a porta no `docker-compose.yml`:
```yaml
ports:
  - "8003:8000"  # Use outra porta
```

### Banco de dados corrompido

**Solução**: Recrie o banco:
```bash
docker compose down -v
docker compose up
```

## 📚 Documentação Adicional

- `IMPROVEMENTS_APPLIED.md` - Detalhes de todas as melhorias
- `SYNTAX_CHECK.txt` - Validações de sintaxe
- `.env.example` - Exemplo de configuração

## 🤝 Contribuindo

1. Crie uma branch para sua feature
2. Implemente as mudanças
3. Adicione testes
4. Faça commit com mensagens descritivas
5. Abra um Pull Request

## 📄 Licença

[Sua licença aqui]

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs: `docker compose logs -f`
2. Consulte o troubleshooting acima
3. Abra uma issue no repositório

---

**Versão**: 4.0  
**Última atualização**: 2024  
**Status**: ✅ Produção Ready (após aplicar mudanças do IMPROVEMENTS_APPLIED.md)
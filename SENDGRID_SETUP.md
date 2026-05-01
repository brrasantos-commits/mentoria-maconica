# 📧 Configurar SendGrid para Reset de Senha

## Por que SendGrid?

O Railway bloqueia conexões SMTP de saída (`Network is unreachable`), mas permite APIs HTTP. SendGrid usa API HTTP e funciona perfeitamente no Railway.

## 🚀 Passo a Passo

### 1. Criar Conta SendGrid (Gratuita)

1. Acesse: https://signup.sendgrid.com/
2. Preencha o formulário
3. Verifique seu email
4. Complete o onboarding

**Plano Gratuito:**
- ✅ 100 emails/dia
- ✅ Suficiente para desenvolvimento e pequena produção
- ✅ Sem cartão de crédito necessário

### 2. Gerar API Key

1. **Login no SendGrid**: https://app.sendgrid.com/
2. **Settings** > **API Keys**
3. **Create API Key**
4. **Nome**: `Sales Pitch AI - Railway`
5. **Permissões**: `Full Access` (ou apenas `Mail Send`)
6. **Create & View**
7. **COPIE A CHAVE** (só aparece uma vez!)

Exemplo de chave:
```
SG.xxxxxxxxxxxxxxxxxxx.yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

### 3. Verificar Sender Identity

Para enviar emails, você precisa verificar um remetente:

#### Opção A: Single Sender Verification (Mais Fácil)

1. **Settings** > **Sender Authentication**
2. **Verify a Single Sender**
3. Preencha:
   - **From Name**: `Sales Pitch AI`
   - **From Email**: `seu-email@gmail.com` (use seu email real)
   - **Reply To**: mesmo email
   - **Company**: `Sales Pitch AI`
4. **Create**
5. **Verifique seu email** e clique no link

#### Opção B: Domain Authentication (Produção)

Se você tem um domínio próprio:
1. **Settings** > **Sender Authentication**
2. **Authenticate Your Domain**
3. Siga as instruções para adicionar registros DNS

### 4. Configurar no Railway

No painel do Railway, vá em **Variables** e adicione:

```env
SENDGRID_API_KEY=SG.sua-chave-aqui
SENDGRID_FROM_EMAIL=seu-email-verificado@gmail.com
SENDGRID_FROM_NAME=Sales Pitch AI
```

**⚠️ IMPORTANTE:**
- Use o **mesmo email** que você verificou no passo 3
- A chave começa com `SG.`
- Não compartilhe a chave

### 5. Deploy

```bash
git add .
git commit -m "feat: adicionar suporte SendGrid para emails"
git push origin main
```

Railway fará redeploy automaticamente.

### 6. Testar

1. Acesse sua aplicação
2. Vá para `/forgot-password`
3. Digite o email de um usuário cadastrado
4. Verifique os logs do Railway:

**Sucesso:**
```
INFO - Reset email sent via SendGrid to usuario@email.com (status: 202)
```

**Erro:**
```
ERROR - Failed to send email via SendGrid: [detalhes]
```

## 🔍 Troubleshooting

### Erro: "The from email does not match a verified Sender Identity"

**Solução:** O email em `SENDGRID_FROM_EMAIL` deve ser o mesmo que você verificou no SendGrid.

### Erro: "Unauthorized"

**Solução:** 
- Verifique se a API Key está correta
- Gere uma nova chave se necessário
- Certifique-se que copiou a chave completa

### Erro: "API key does not have permission"

**Solução:** Gere nova chave com permissão `Mail Send` ou `Full Access`

### Email não chega

**Verifique:**
1. Spam/Lixeira
2. Email está cadastrado no banco de dados
3. Logs do Railway mostram sucesso (status 202)
4. SendGrid Activity (https://app.sendgrid.com/email_activity)

## 📊 Monitorar Envios

No SendGrid Dashboard:
- **Activity** - Ver emails enviados
- **Statistics** - Métricas de entrega
- **Suppressions** - Emails bloqueados

## 💰 Limites e Upgrade

### Plano Gratuito
- 100 emails/dia
- Perfeito para desenvolvimento

### Se precisar mais
- **Essentials**: $19.95/mês - 50k emails/mês
- **Pro**: $89.95/mês - 100k emails/mês

## 🎨 Personalizar Email

O template HTML está em `pitch_app/services/email_service.py` na função `_send_via_sendgrid()`.

Você pode personalizar:
- Cores
- Logo
- Texto
- Layout

## ✅ Checklist Final

- [ ] Conta SendGrid criada
- [ ] API Key gerada e copiada
- [ ] Sender Identity verificado
- [ ] Variáveis configuradas no Railway
- [ ] Deploy realizado
- [ ] Email de teste enviado com sucesso

## 🆘 Suporte

- **SendGrid Docs**: https://docs.sendgrid.com/
- **SendGrid Support**: https://support.sendgrid.com/
- **Status**: https://status.sendgrid.com/

---

**Pronto! Agora o reset de senha funciona perfeitamente no Railway! 🎉**
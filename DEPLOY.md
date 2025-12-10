# 🚀 Guia de Deploy - Locamil

Este guia fornece instruções para fazer deploy da aplicação Locamil em diferentes plataformas.

## 📋 Pré-requisitos

Antes de fazer o deploy, certifique-se de:

1. ✅ Ter configurado todas as variáveis de ambiente necessárias
2. ✅ Ter testado a aplicação localmente
3. ✅ Ter gerado uma `SECRET_KEY` forte e única
4. ✅ Ter configurado `FLASK_DEBUG=False` para produção

## 🌐 Opções de Deploy

### 1. PythonAnywhere (Recomendado para Iniciantes)

PythonAnywhere é uma plataforma simples e gratuita para hospedar aplicações Flask.

#### Passos:

1. **Criar conta no PythonAnywhere**
   - Acesse [pythonanywhere.com](https://www.pythonanywhere.com)
   - Crie uma conta gratuita

2. **Fazer upload do código**
   ```bash
   # No seu terminal local
   git clone https://github.com/seu-usuario/locamil.git
   cd locamil
   ```

3. **Configurar no PythonAnywhere**
   - Vá para "Web" → "Add a new web app"
   - Escolha "Flask" e Python 3.10
   - Configure o caminho para `app.py`

4. **Instalar dependências**
   ```bash
   # No console do PythonAnywhere
   pip install -r requirements.txt
   ```

5. **Configurar variáveis de ambiente**
   - Crie arquivo `.env` no servidor
   - Configure `SECRET_KEY`, `DATABASE_URI`, etc.

6. **Reload da aplicação**
   - Clique em "Reload" no painel Web

### 2. Heroku

Heroku é uma plataforma popular para deploy de aplicações web.

#### Passos:

1. **Instalar Heroku CLI**
   ```bash
   # Windows (com Chocolatey)
   choco install heroku-cli
   
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Linux
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Criar arquivos necessários**

   **Procfile** (criar na raiz do projeto):
   ```
   web: gunicorn app:app
   ```

   **runtime.txt** (criar na raiz do projeto):
   ```
   python-3.10.12
   ```

   **Atualizar requirements.txt**:
   ```bash
   pip install gunicorn
   pip freeze > requirements.txt
   ```

3. **Deploy**
   ```bash
   # Login no Heroku
   heroku login
   
   # Criar app
   heroku create nome-do-seu-app
   
   # Configurar variáveis de ambiente
   heroku config:set SECRET_KEY=sua-chave-secreta-aqui
   heroku config:set FLASK_DEBUG=False
   
   # Deploy
   git push heroku main
   
   # Abrir aplicação
   heroku open
   ```

### 3. Railway

Railway é uma plataforma moderna e fácil de usar.

#### Passos:

1. **Criar conta no Railway**
   - Acesse [railway.app](https://railway.app)
   - Conecte sua conta GitHub

2. **Criar novo projeto**
   - Clique em "New Project"
   - Selecione "Deploy from GitHub repo"
   - Escolha o repositório Locamil

3. **Configurar variáveis de ambiente**
   - Vá para "Variables"
   - Adicione:
     - `SECRET_KEY`
     - `DATABASE_URI`
     - `FLASK_DEBUG=False`

4. **Deploy automático**
   - Railway fará deploy automaticamente
   - Acesse a URL fornecida

### 4. Render

Render oferece deploy gratuito com SSL automático.

#### Passos:

1. **Criar conta no Render**
   - Acesse [render.com](https://render.com)
   - Conecte sua conta GitHub

2. **Criar Web Service**
   - Clique em "New +"
   - Selecione "Web Service"
   - Conecte o repositório Locamil

3. **Configurar**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

4. **Variáveis de ambiente**
   - Adicione `SECRET_KEY`, `DATABASE_URI`, etc.

5. **Deploy**
   - Render fará deploy automaticamente

### 5. DigitalOcean App Platform

Para aplicações mais robustas.

#### Passos:

1. **Criar conta no DigitalOcean**
   - Acesse [digitalocean.com](https://www.digitalocean.com)

2. **Criar App**
   - Vá para "Apps" → "Create App"
   - Conecte GitHub e selecione o repositório

3. **Configurar**
   - Escolha plano (começa em $5/mês)
   - Configure variáveis de ambiente
   - Configure banco de dados (PostgreSQL recomendado)

4. **Deploy**
   - DigitalOcean fará deploy automaticamente

## 🗄️ Banco de Dados em Produção

### SQLite (Desenvolvimento/Pequeno Porte)

```env
DATABASE_URI=sqlite:///locadora.db
```

**Limitações**: Não recomendado para produção com múltiplos usuários simultâneos.

### PostgreSQL (Recomendado para Produção)

```env
DATABASE_URI=postgresql://usuario:senha@host:5432/locamil
```

**Vantagens**: Robusto, escalável, suporta múltiplos usuários.

#### Configurar PostgreSQL:

1. **Heroku**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

2. **Railway/Render**: Adicione PostgreSQL pelo painel

3. **DigitalOcean**: Crie um Managed Database

### MySQL

```env
DATABASE_URI=mysql://usuario:senha@host:3306/locamil
```

## 🔒 Checklist de Segurança

Antes de fazer deploy em produção:

- [ ] `FLASK_DEBUG=False` configurado
- [ ] `SECRET_KEY` forte e única gerada
- [ ] Arquivo `.env` NÃO commitado no Git
- [ ] Banco de dados de produção configurado
- [ ] HTTPS/SSL configurado (a maioria das plataformas faz automaticamente)
- [ ] Backup do banco de dados configurado
- [ ] Logs de erro configurados
- [ ] Limite de taxa (rate limiting) implementado (opcional)

## 📊 Monitoramento

### Logs

Acesse logs da aplicação:

- **Heroku**: `heroku logs --tail`
- **Railway**: Painel "Deployments" → "Logs"
- **Render**: Painel "Logs"

### Métricas

Configure monitoramento com:
- Sentry (erros)
- New Relic (performance)
- Google Analytics (uso)

## 🔄 Atualizações

Para atualizar a aplicação em produção:

```bash
# Fazer alterações localmente
git add .
git commit -m "feat: nova funcionalidade"
git push origin main

# Deploy automático (Railway, Render, etc.)
# OU
# Deploy manual (Heroku)
git push heroku main
```

## 🆘 Troubleshooting

### Erro: "Application Error"

1. Verifique logs: `heroku logs --tail`
2. Verifique variáveis de ambiente
3. Verifique se todas as dependências estão em `requirements.txt`

### Erro: "Database connection failed"

1. Verifique `DATABASE_URI`
2. Verifique credenciais do banco
3. Verifique se o banco está acessível

### Erro: "Internal Server Error"

1. Verifique `FLASK_DEBUG=False`
2. Verifique logs de erro
3. Teste localmente com `FLASK_DEBUG=True`

## 📚 Recursos Adicionais

- [Documentação Flask Deployment](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [Guia Heroku Python](https://devcenter.heroku.com/articles/getting-started-with-python)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)

---

💡 **Dica**: Comece com uma plataforma gratuita (Railway, Render) para testar, depois migre para uma solução paga se necessário.

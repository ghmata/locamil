# 📁 Estrutura do Projeto - Locamil

```
Locamil/
│
├── .github/                          # Configurações do GitHub
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md            # Template para reportar bugs
│   │   └── feature_request.md       # Template para solicitar features
│   └── pull_request_template.md     # Template para pull requests
│
├── instance/                         # Pasta do Flask (criada automaticamente)
│   └── locadora.db                  # Banco de dados SQLite (não commitado)
│
├── templates/                        # Templates HTML (Jinja2)
│   ├── base.html                    # Template base
│   ├── dashboard.html               # Dashboard principal
│   ├── exportar.html                # Página de exportação
│   ├── historico.html               # Histórico de locações
│   └── nova_locacao.html            # Formulário de nova locação
│
├── __pycache__/                      # Cache Python (não commitado)
│
├── .env                              # Variáveis de ambiente (NÃO COMMITADO)
├── .env.example                      # Template de variáveis de ambiente
├── .gitattributes                    # Configuração de atributos do Git
├── .gitignore                        # Arquivos ignorados pelo Git
│
├── app.py                            # Aplicação Flask principal
├── models.py                         # Modelos do banco de dados (SQLAlchemy)
│
├── requirements.txt                  # Dependências Python
│
├── CONTRIBUTING.md                   # Guia de contribuição
├── DEPLOY.md                         # Guia de deploy
├── GITHUB_SETUP.md                   # Instruções de setup do GitHub
├── LICENSE                           # Licença MIT
└── README.md                         # Documentação principal

Arquivos Legados (podem ser removidos):
├── alugueis.json                     # Arquivo de dados antigo (vazio)
└── rent_app.py                       # Aplicação Streamlit antiga (não usada)
```

## 📝 Descrição dos Arquivos Principais

### Código-fonte

- **`app.py`**: Aplicação Flask principal com todas as rotas e lógica de negócio
- **`models.py`**: Definição dos modelos de banco de dados (Carro, Cliente, Locação)

### Configuração

- **`.env.example`**: Template com todas as variáveis de ambiente necessárias
- **`.gitignore`**: Lista de arquivos que não devem ser commitados
- **`.gitattributes`**: Configuração de normalização de line endings

### Documentação

- **`README.md`**: Documentação principal do projeto
- **`CONTRIBUTING.md`**: Como contribuir para o projeto
- **`DEPLOY.md`**: Guia completo de deploy em várias plataformas
- **`GITHUB_SETUP.md`**: Instruções para configurar o repositório no GitHub
- **`LICENSE`**: Licença MIT do projeto

### Templates GitHub

- **`.github/ISSUE_TEMPLATE/bug_report.md`**: Template para reportar bugs
- **`.github/ISSUE_TEMPLATE/feature_request.md`**: Template para solicitar features
- **`.github/pull_request_template.md`**: Template para pull requests

### Templates HTML

- **`templates/base.html`**: Layout base com Bootstrap 5
- **`templates/dashboard.html`**: Dashboard com status da frota
- **`templates/nova_locacao.html`**: Formulário de nova locação
- **`templates/historico.html`**: Histórico de locações
- **`templates/exportar.html`**: Página de exportação de dados

## 🗑️ Arquivos que Podem Ser Removidos

Se você não precisa dos arquivos legados:

```bash
# Remover arquivo de dados antigo (vazio)
rm alugueis.json

# Remover aplicação Streamlit antiga
rm rent_app.py
```

## 📦 Arquivos Gerados Automaticamente

Estes arquivos são criados automaticamente e **NÃO** devem ser commitados:

- `instance/locadora.db` - Banco de dados SQLite
- `__pycache__/` - Cache do Python
- `.env` - Variáveis de ambiente locais
- `*.pyc` - Bytecode Python compilado

Todos esses já estão no `.gitignore`.

## 🔐 Arquivos Sensíveis

**NUNCA** commite estes arquivos:

- `.env` - Contém chaves secretas e senhas
- `instance/locadora.db` - Pode conter dados sensíveis de clientes
- Qualquer arquivo com credenciais ou tokens

## 📊 Tamanho do Projeto

- **Arquivos Python**: ~25 KB
- **Templates HTML**: ~30 KB
- **Documentação**: ~20 KB
- **Total (sem dependências)**: ~75 KB

## 🚀 Próximos Passos

1. Revise a estrutura
2. Remova arquivos legados se não precisar
3. Configure `.env` com suas variáveis
4. Faça commit e push para o GitHub

---

Estrutura gerada em: 2025-12-10

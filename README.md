# 🚗 Sistema de Gestão de Locadora de Veículos - Locamil

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Aplicação web completa para gestão de uma pequena locadora de veículos, desenvolvida com Flask, SQLAlchemy e Bootstrap 5.

## 📸 Preview

> 🎨 _Screenshots em breve_

## 📋 Características

- **Dashboard Interativo**: Visão geral do status de todos os carros em tempo real
- **Gestão de Frota**: Sistema já vem com a frota cadastrada (1 HB20 + 4 Celtas)
- **Nova Locação**: Formulário simples e intuitivo com cálculo automático de valores
- **Validação de Conflitos**: Impede aluguel de carros já ocupados no período
- **Histórico Completo**: Lista todas as locações passadas e futuras
- **Design Mobile First**: Interface otimizada para uso em celulares

## 🚀 Como Executar

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/locamil.git
cd locamil
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure suas variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e configure:
- `SECRET_KEY`: Gere uma chave secreta única (veja instruções no arquivo)
- `DATABASE_URI`: URI do banco de dados (padrão: SQLite)
- `FLASK_DEBUG`: `True` para desenvolvimento, `False` para produção

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Executar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em: **http://localhost:5000**

### 5. Deploy em Produção

Para fazer deploy da aplicação em produção, consulte o [Guia de Deploy](DEPLOY.md) completo com instruções para várias plataformas (Heroku, Railway, Render, PythonAnywhere, etc.).

### 3. Primeiro Acesso

Na primeira execução, o sistema automaticamente:
- Cria o banco de dados SQLite (`locadora.db`)
- Cadastra a frota inicial:
  - 1x HB20 (Placa: HB-001) - Diária: R$ 120,00
  - 4x Celta (Placas: CEL-100, CEL-200, CEL-300, CEL-400) - Diária: R$ 90,00

## 📱 Funcionalidades

### Dashboard
- Cards com status de cada carro (Disponível/Alugado)
- Tabela de próximas devoluções (próximos 7 dias)
- Tabela de próximas retiradas (próximos 7 dias)

### Nova Locação
- Seleção de cliente (nome e WhatsApp opcional)
- Seleção de carro da frota
- Datas de retirada e devolução
- **Cálculo automático** do valor total (Dias × Diária)
- Validação de conflitos de datas

### Histórico
- Lista completa de todas as locações
- Filtros por status (Ativa, Finalizada, Cancelada)
- Ações para finalizar ou cancelar locações ativas
- Estatísticas de totais

### Exportação de Dados
- **SQL**: Exporta todos os dados em formato SQL (INSERT statements) para backup e migração
- **CSV**: Exporta locações em CSV para análise em Excel, Google Sheets ou Python/Pandas
- **JSON**: Exporta todos os dados em JSON estruturado para integração e análise programática

## 🗄️ Estrutura do Banco de Dados

- **Carros**: Modelo, placa, cor, valor da diária
- **Clientes**: Nome, WhatsApp
- **Locações**: Carro, cliente, datas, valor total, status

## 🛠️ Tecnologias Utilizadas

- **Flask 3.0.0**: Framework web
- **SQLAlchemy 3.1.1**: ORM para banco de dados
- **SQLite**: Banco de dados embutido
- **Bootstrap 5**: Framework CSS para interface
- **Bootstrap Icons**: Ícones

## 📝 Notas Importantes

- O banco de dados é criado automaticamente na primeira execução
- Os dados são persistidos no arquivo `locadora.db`
- A validação de conflitos impede aluguel de carros já ocupados
- O sistema é otimizado para uso mobile (botões grandes, layout responsivo)
- **Exportação de dados**: Acesse a página "Exportar" no menu para baixar dados em SQL, CSV ou JSON para análise posterior

## 🔒 Segurança

### Variáveis de Ambiente

Este projeto usa variáveis de ambiente para configurações sensíveis. **NUNCA** commite o arquivo `.env` no Git.

### Gerando uma SECRET_KEY Segura

Para gerar uma chave secreta forte, execute em Python:

```python
import secrets
print(secrets.token_hex(32))
```

Copie o resultado e cole no arquivo `.env`:

```
SECRET_KEY=sua-chave-gerada-aqui
```

### Produção

Em produção:
1. ✅ Defina `FLASK_DEBUG=False` no arquivo `.env`
2. ✅ Use uma `SECRET_KEY` única e forte (nunca use a chave padrão)
3. ✅ Configure um banco de dados apropriado (PostgreSQL, MySQL, etc.)
4. ✅ Use um servidor WSGI (Gunicorn, uWSGI) ao invés do servidor de desenvolvimento do Flask
5. ✅ Configure HTTPS/SSL


## 📞 Suporte

Para dúvidas ou problemas, verifique:
1. Se todas as dependências foram instaladas corretamente
2. Se a porta 5000 está disponível
3. Se há permissões para criar o arquivo `locadora.db`
4. Se o arquivo `.env` está configurado corretamente

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia o [guia de contribuição](CONTRIBUTING.md) para mais detalhes.

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 🗺️ Roadmap

- [ ] Sistema de autenticação de usuários
- [ ] Relatórios e dashboards avançados
- [ ] Integração com API de pagamento
- [ ] Notificações por e-mail/SMS
- [ ] App mobile (React Native)
- [ ] Sistema de manutenção de veículos
- [ ] Gestão de multas e sinistros

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

Desenvolvido com ❤️ para facilitar a gestão de locadoras de veículos.


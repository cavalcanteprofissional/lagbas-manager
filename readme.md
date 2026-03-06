# LabGas Manager

**Versão: 1.4.1**

Dashboard para gestão de cilindro de gás e elementos analisados em laboratório de química, utilizando **Flask** com **Jinja2** para o frontend e **Supabase** como banco de dados.

## Novidades v1.4.1

- **Mensagens de erro amigáveis**: Erros de chave duplicada agora exibem mensagens claras
- **Correção no histórico**: Registro de atividades agora funciona corretamente
- **Formatação de datas**: Datas padronizadas para DD/MM/YYYY
- **Correção de exclusão**: Exclusão de cilindro/elemento com amostras vinculadas com mensagem clara

## Arquitetura do Sistema

```
┌─────────────────┐     ┌─────────────────┐
│   Flask+Jinja2  │────▶│    Supabase    │
│  (Frontend Web) │     │  (PostgreSQL)  │
│   + Blueprints  │     │                │
└─────────────────┘     └─────────────────┘
```

## Tecnologias

- **Frontend**: Flask 3.0 + Jinja2 + Bootstrap 5
- **Banco de Dados**: Supabase (PostgreSQL)
- **Autenticação**: Supabase Auth
- **Gerenciamento de Dependências**: pip + venv
- **Deploy**: Railway.app

## Estrutura de Diretórios

```
labgas-manager/
├── .gitignore
├── AGENTS.md                  # Documentação técnica
├── readme.md                  # Este arquivo
├── database.md               # Schema completo do banco de dados
├── todo.md                  # Tarefas e histórico
├── backend/                   # Flask API (opcional)
└── frontend/                  # Flask + Jinja2 (Web)
    ├── app.py                 # Aplicação Flask principal (~130 linhas)
    ├── blueprints/            # Blueprints Flask
    │   ├── auth.py           # Login, register, logout
    │   ├── cilindro.py       # CRUD Cilindros
    │   ├── elemento.py       # CRUD Elementos
    │   ├── amostra.py        # CRUD Amostras
    │   ├── admin.py          # Funções admin
    │   ├── historico.py      # Histórico de atividades
    │   └── helpers.py        # Funções auxiliares
    ├── utils/                # Utilitários
    │   ├── supabase_utils.py # Cliente Supabase
    │   ├── validators.py     # Validações
    │   └── constants.py      # Constantes
    └── templates/            # Templates HTML
```

## Como Rodar Local

### Frontend (Flask + Jinja2)

```bash
# 1. Criar ambiente virtual (primeira vez)
cd frontend
python -m venv venv

# 2. Instalar dependências
./venv/Scripts/pip install -r requirements.txt

# 3. Rodar o servidor
./venv/Scripts/python app.py
```

O frontend estará disponível em: `http://localhost:5000`

## Variáveis de Ambiente

### frontend/.env

```env
SECRET_KEY=sua_chave_secreta
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon
SUPABASE_SERVICE_KEY=sua_service_role_key
```

**Nota**: A service_role key é necessária para operações de admin (bypass RLS).

## Deploy no Railway

### Configuração

1. Criar projeto no Railway com o repositório GitHub
2. Adicionar variáveis de ambiente no Railway:
   - `SECRET_KEY`: chave secreta para sessões
   - `SUPABASE_URL`: URL do projeto Supabase
   - `SUPABASE_KEY`: chave anônima do Supabase

### Build Command: (vazio)
### Start Command: `gunicorn app:app`

## Fluxo de Autenticação

1. Usuário acessa o frontend Flask
2. Faz login com email/senha
3. Flask valida no Supabase Auth
4. Sessão gerenciada por Flask-Login
5. Dados filtrados por user_id

## Regras de Negócio

### Cilindro
- Código único por usuário
- Código deve seguir formato CIL-XXX (ex: CIL-001, CIL-002)
- Valores padrão: 1kg = 956L, R$290
- Status: ativo, esgotado

### Elemento
- Lista pré-carregada automática (20 elementos padrão)
- Consumo em L/min
- Nomes únicos por usuário

### Amostra
- Data default como data atual
- Tempo de chama editável (HH:MM:SS)
- Vincular a cilindro e elemento existentes
- Quantidade de amostras (inteiro)

## Estado Atual

### Funcionalidades Implementadas
- Mensagens de erro amigáveis para duplicatas
- Sistema de registro de histórico funcionando corretamente
- Dates formatadas em DD/MM/YYYY
- Sistema de admin com todas as funcionalidades operacionais
- Sistema de registro de histórico de atividades
- Painel admin lista todos os usuários cadastrados
- Perfil de usuário mostra role corretamente
- Nome e email armazenados na tabela perfil
- Sistema de segurança com JWT validation
- Paginação em todas as listas (10/25/50/100 itens por página)
- Otimização de consultas (separação dados próprios vs compartilhados)
- Sistema de cache (5 minutos)
- Filtros em listas de cilindro, elemento e amostra
- Página de histórico com filtros por tipo e ação
- Coluna "Usuário" no histórico de atividades
- Cards visuais no dashboard
- Toast notifications
- Edição de perfil (nome) funcionando corretamente
- Criação automática de perfil no registro
- Validação de código de cilindro (CIL-XXX)
- Normalização de nomes de elementos
- Data default como hoje no registro de amostras
- Ordenação alfabética nos seletores de Cilindro/Elemento
- Remoção de elementos duplicados nos seletores de amostra
- **Refatoração para Blueprints** - Código organizado por domínio
- Multi-select com checkbox para exclusão em massa

### Versão
- v1.4.1 - Correções de UX e mensagens amigáveis
- v1.4.0 - Refatoração para Blueprints, código modular

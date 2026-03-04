# LabGas Manager

**Versão: 1.3.0**

Dashboard para gestão de cilindro de gás e elementos analisados em laboratório de química, utilizando **Flask** com **Jinja2** para o frontend e **Supabase** como banco de dados.

## Novidades v1.3.0

- **Histórico de Atividades**: Sistema completo de registro de todas as operações CRUD na tabela `historico_log`
- **Filtros Aprimorados**: Removido seletor de compartilhamento nas abas Elementos e Cilindros
- **Melhorias UX**: Data default como hoje no registro de amostras
- **Ordenação**: Seletores de Cilindro/Elemento em ordem alfabética
- **Correções**: Bugs no filtro do Histórico, duplicação de elementos, exclusão de cilindro/elemento

## Novidades v1.2.2

- **Validação de Cilindro**: Código deve seguir formato CIL-XXX (ex: CIL-001, CIL-002)
- **Normalização de Elementos**: Nomes salvos com primeira letra maiúscula

## Novidades v1.2.1

- **Admin**: Painel agora lista todos os usuários cadastrados

## Arquitetura do Sistema

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Flask+Jinja2  │     │    Flask API    │     │    Supabase     │
│  (Frontend Web) │────▶│  (CRUDs + Auth) │────▶│  (PostgreSQL)   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Tecnologias

- **Frontend**: Flask 3.0 + Jinja2 + Bootstrap 5
- **Backend API**: Flask 3.0 + Flask-RESTX
- **Banco de Dados**: Supabase (PostgreSQL)
- **Autenticação**: Supabase Auth
- **Gerenciamento de Dependências**: pip + venv
- **Deploy**: Railway.app

## Estrutura de Diretórios

```
labgas-manager/
├── .gitignore
├── agents.md                  # Documentação técnica
├── readme.md                  # Este arquivo
├── database.md               # Schema completo do banco de dados
├── bd_admin.md               # Script SQL admin
├── backend/                   # Flask API (opcional)
│   ├── app.py                 # Aplicação Flask API
│   ├── .env                   # Variáveis do backend
│   ├── requirements.txt       # Dependências Python
│   ├── venv/                  # Virtual environment
│   ├── Procfile               # Deploy Railway
│   ├── config.py              # Configurações
│   ├── routes/
│   │   ├── auth.py            # Autenticação
│   │   ├── cilindro.py        # CRUD Cilindros
│   │   ├── elemento.py        # CRUD Elementos
│   │   └── amostra.py         # CRUD Amostras
│   └── utils/
│       ├── supabase.py        # Cliente Supabase
│       └── decorators.py      # Autenticação JWT
└── frontend/                  # Flask + Jinja2 (Web)
    ├── app.py                 # Aplicação Flask principal
    ├── .env                   # Variáveis do frontend
    ├── requirements.txt        # Dependências Python
    ├── venv/                  # Virtual environment
    ├── Procfile               # Deploy Railway
    └── templates/             # Templates HTML
        ├── base.html          # Layout base
        ├── login.html         # Login
        ├── register.html      # Registro
        ├── dashboard.html     # Dashboard
        ├── cilindro.html      # CRUD Cilindros
        ├── elemento.html      # CRUD Elementos
        ├── amostra.html       # CRUD Amostras
        ├── historico.html     # Histórico de atividades
        ├── perfil.html        # Perfil usuário
        └── admin.html         # Painel admin
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

### Backend (API - opcional) - Porta 5001

```bash
cd backend
python -m venv venv
./venv/Scripts/pip install -r requirements.txt
./venv/Scripts/python app.py
```

## Variáveis de Ambiente

### frontend/.env

```env
SECRET_KEY=sua_chave_secreta
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon
SUPABASE_SERVICE_KEY=sua_service_role_key
```

**Nota**: A service_role key é necessária para operações de admin (bypass RLS).

### backend/.env

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=sua_chave_secreta
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon
SUPABASE_JWT_SECRET=seu_jwt_secret
```

## Modelo de Dados (Supabase)

### Tabela: cilindro

```sql
CREATE TABLE cilindro (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL,
    data_compra DATE NOT NULL,
    data_inicio_consumo DATE,
    data_fim DATE,
    gas_kg DECIMAL(5,2) DEFAULT 1.0,
    litros_equivalentes DECIMAL(10,2) DEFAULT 956.0,
    custo DECIMAL(10,2) DEFAULT 290.00,
    status VARCHAR(20) DEFAULT 'ativo',
    compartilhado BOOLEAN DEFAULT false,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: elemento

```sql
CREATE TABLE elemento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    consumo_lpm DECIMAL(5,2) NOT NULL,
    compartilhado BOOLEAN DEFAULT false,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: amostra

```sql
CREATE TABLE amostra (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    tempo_chama VARCHAR(8) NOT NULL,
    cilindro_id INTEGER REFERENCES cilindro(id),
    elemento_id INTEGER REFERENCES elemento(id),
    quantidade_amostras INTEGER DEFAULT 1,
    compartilhado BOOLEAN DEFAULT false,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela: historico_log

```sql
CREATE TABLE historico_log (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    acao VARCHAR(20) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Nota**: O código usa nomes de tabelas no singular (`cilindro`, `elemento`, `amostra`).

## Deploy no Railway

### Configuração
O projeto utiliza Dockerfile para deploy no Railway.

1. Criar projeto no Railway com o repositório GitHub
2. O Railway detecta automaticamente o Dockerfile
3. Adicionar variáveis de ambiente no Railway:
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
- Status: ativo, em_uso, esgotado

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
- Sistema de admin com todas as funcionalidades operacionais
- Sistema de registro de histórico de atividades
- Painel admin lista todos os usuários cadastrados
- Perfil de usuário mostra role corretamente
- Nome e email armazenados na tabela perfil
- Sistema de segurança com JWT validation
- Paginação em todas as listas (10 itens por página)
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

### Versão
- v1.3.0 - Sistema de histórico, filtros aprimorados, correções de bugs

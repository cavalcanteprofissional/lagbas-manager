# LabGas Manager

Dashboard para gestão de cilindro de gás e elementos analisados em laboratório de química, utilizando **Flask** com **Jinja2** para o frontend e **Supabase** como banco de dados.

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
│   │   ├── amostra.py         # CRUD Amostras
│   └── utils/
│       ├── supabase.py        # Cliente Supabase
│       └── decorators.py      # Autenticação JWT
└── frontend/                  # Flask + Jinja2 (Web)
    ├── app.py                 # Aplicação Flask principal
    ├── .env                   # Variáveis do frontend
    ├── requirements.txt        # Dependências Python
    ├── venv/                  # Virtual environment
    ├── Procfile               # Deploy Railway
    └── templates/              # Templates HTML
        ├── base.html           # Layout base
        ├── login.html          # Login
        ├── register.html       # Registro
        ├── dashboard.html      # Dashboard
        ├── cilindro.html       # CRUD Cilindros
        ├── elemento.html       # CRUD Elementos
        ├── amostra.html        # CRUD Amostras
        └── perfil.html        # Perfil usuário
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
```

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
    codigo VARCHAR(50) UNIQUE NOT NULL,
    data_compra DATE NOT NULL,
    data_inicio_consumo DATE,
    data_fim DATE,
    gas_kg DECIMAL(5,2) DEFAULT 1.0,
    litros_equivalentes DECIMAL(10,2) DEFAULT 956.0,
    custo DECIMAL(10,2) DEFAULT 290.00,
    status VARCHAR(20) DEFAULT 'ativo',
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Tabela: elemento

```sql
CREATE TABLE elemento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    consumo_lpm DECIMAL(5,2) NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Tabela: amostra

```sql
CREATE TABLE amostra (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    tempo_chama VARCHAR(8) NOT NULL,
    cilindro_id INTEGER REFERENCES cilindro(id) ON DELETE SET NULL,
    elemento_id INTEGER REFERENCES elemento(id) ON DELETE SET NULL,
    quantidade_amostras INTEGER DEFAULT 1,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Nota**: O código usa nomes de tabelas no singular (`cilindro`, `elemento`, `amostra`).

## Deploy no Railway

### Frontend (Flask Web)

Crie um serviço Railway com:
- Build Command: (vazio)
- Start Command: `gunicorn app:app`

## Fluxo de Autenticação

1. Usuário acessa o frontend Flask
2. Faz login com email/senha
3. Flask valida no Supabase Auth
4. Sessão gerenciada por Flask-Login
5. Dados filtrados por user_id

## Regras de Negócio

### Cilindro
- Código único por usuário
- Valores padrão: 1kg = 956L, R$290
- Status: ativo, em_uso, esgotado

### Elemento
- Lista pré-carregada automática (20 elementos padrão)
- Consumo em L/min
- Nomes únicos por usuário

### Amostra
- Data/tempo de chama editável
- Vincular a cilindro e elemento existentes

### Tempo Chama
- Registrar duração em h/min/s
- Calcular consumo automaticamente
- Vincular a elemento e cilindro

## Deploy Railway

### Configuração
1. Criar projeto no Railway com o repositório GitHub
2. Configurar Root Directory como `frontend` ou usar `railway.json`
3. Adicionar variáveis de ambiente:
   - `SECRET_KEY`: chave secreta para sessões
   - `SUPABASE_URL`: URL do projeto Supabase
   - `SUPABASE_KEY`: chave anônima do Supabase

### Build Command: (vazio)
### Start Command: `gunicorn app:app`

## Estado Atual
- Deploy em andamento ( Railway)

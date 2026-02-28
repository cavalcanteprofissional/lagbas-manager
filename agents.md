# LabGas Manager - Arquitetura Migrada

## Visão Geral

Dashboard para gestão de cilindro de gás e elementos analisados em laboratório de química, utilizando **Flask** para APIs REST (CRUDs) e **Streamlit** para dashboards/visualizações, com **Supabase** como banco de dados PostgreSQL.

## Arquitetura do Sistema

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │     │    Flask API    │     │    Supabase     │
│  (Dashboards)  │────▶│  (CRUDs + Auth) │────▶│  (PostgreSQL)   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Tecnologias

- **Backend API**: Flask + Flask-RESTX
- **Frontend Dashboard**: Streamlit
- **Banco de Dados**: Supabase (PostgreSQL)
- **Autenticação**: Supabase Auth (via API Flask)
- **Gerenciamento de Dependências**: Poetry (frontend), pip (backend)
- **Deploy**: Railway.app

## Estrutura de Diretórios

```
labgas-manager/
├── pyproject.toml              # Poetry config (Streamlit)
├── poetry.lock
├── .env                        # Variáveis ambiente
├── .gitignore
├── agents.md
├── backend/                    # Flask API
│   ├── app.py                 # Aplicação Flask
│   ├── requirements.txt       # Dependências Python
│   ├── config.py              # Configurações
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py           # Autenticação
│   │   ├── cilindro.py       # CRUD Cilindros
│   │   ├── elemento.py       # CRUD Elementos
│   │   ├── amostra.py        # CRUD Amostras
│   │   └── tempo_chama.py    # CRUD Tempo Chama
│   └── utils/
│       ├── supabase.py       # Cliente Supabase
│       └── decorators.py      # Autenticação JWT
├── frontend/                  # Streamlit Dashboard
│   ├── app.py               # Página principal
│   ├── requirements.txt
│   ├── pages/
│   │   ├── 1_📦_Cilindros.py
│   │   ├── 2_🧪_Elementos.py
│   │   ├── 3_📊_Amostras.py
│   │   ├── 4_🔥_Tempo_Chama.py
│   │   └── 5_👥_Usuarios.py
│   ├── services/
│   │   └── api_client.py    # Cliente API
│   └── assets/
│       └── style.css
└── README.md
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
    hora TIME NOT NULL,
    cilindro_id INTEGER REFERENCES cilindro(id) ON DELETE SET NULL,
    elemento_id INTEGER REFERENCES elemento(id) ON DELETE SET NULL,
    tempo_chama_segundos INTEGER,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Tabela: tempo_chama

```sql
CREATE TABLE tempo_chama (
    id SERIAL PRIMARY KEY,
    elemento_id INTEGER REFERENCES elemento(id) ON DELETE SET NULL,
    cilindro_id INTEGER REFERENCES cilindro(id) ON DELETE SET NULL,
    horas INTEGER NOT NULL,
    minutos INTEGER NOT NULL,
    segundos INTEGER NOT NULL,
    total_segundos INTEGER GENERATED ALWAYS AS (horas * 3600 + minutos * 60 + segundos) STORED,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Elementos Padrão (Dados Iniciais)

```sql
INSERT INTO elemento (nome, consumo_lpm) VALUES
('Antimônio', 1.5), ('Alumínio', 4.5), ('Arsênio', 1.5),
('Bário', 4.5), ('Cádmio', 1.5), ('Chumbo', 2.0),
('Cobalto', 1.5), ('Cobre', 1.5), ('Cromo', 4.5),
('Estanho FAAS', 4.5), ('Estanho HG', 1.5), ('Ferro', 2.0),
('Manganês', 1.5), ('Mercúrio', 0), ('Molibdênio', 4.5),
('Níquel', 1.5), ('Prata', 1.5), ('Selênio', 2.0),
('Zinco', 1.5), ('Tálio', 1.5);
```

## Endpoints da API REST

### Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /api/auth/login | Login com email/senha |
| POST | /api/auth/register | Registro de novo usuário |
| POST | /api/auth/logout | Logout |
| GET | /api/auth/me | Dados do usuário atual |

### Cilindros

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /api/cilindros | Listar todos (filtrado por user_id) |
| POST | /api/cilindros | Criar novo |
| GET | /api/cilindros/{id} | Detalhes |
| PUT | /api/cilindros/{id} | Atualizar |
| DELETE | /api/cilindros/{id} | Deletar |

### Elementos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /api/elementos | Listar todos |
| POST | /api/elementos | Criar novo |
| GET | /api/elementos/{id} | Detalhes |
| PUT | /api/elementos/{id} | Atualizar |
| DELETE | /api/elementos/{id} | Deletar |

### Amostras

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /api/amostras | Listar todas |
| POST | /api/amostras | Criar nova |
| GET | /api/amostras/{id} | Detalhes |
| PUT | /api/amostras/{id} | Atualizar |
| DELETE | /api/amostras/{id} | Deletar |

### Tempo Chama

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /api/tempo-chama | Listar todos |
| POST | /api/tempo-chama | Criar novo |
| GET | /api/tempo-chama/{id} | Detalhes |
| DELETE | /api/tempo-chama/{id} | Deletar |

## Configuração de Ambiente

### Variáveis de Ambiente (Backend)

```env
# Flask
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=sua_chave_secreta_aqui

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon
SUPABASE_JWT_SECRET=seu_jwt_secret
```

### Variáveis de Ambiente (Frontend)

```env
# Streamlit
API_BASE_URL=http://localhost:5000
# Em produção: API_BASE_URL=https://seu-backend.railway.app
```

## Implementação

### 1. Backend Flask

Criar estrutura base com:
- `backend/app.py` - Aplicação principal
- `backend/config.py` - Configurações
- `backend/routes/` - Rotas da API
- Integração com Supabase Auth
- Validação JWT para rotas protegidas

### 2. Frontend Streamlit

Atualizar para:
- Usar API Client para comunicar com Flask
- Consumir endpoints REST
- Manter dashboards e visualizações
- Sessão armazenada no session_state

### 3. Deploy Railway

- Backend: `web: gunicorn app:app`
- Frontend: `web: streamlit run app.py`

## Comandos de Desenvolvimento

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Frontend
cd frontend
poetry install
poetry run streamlit run app.py

# Deploy Railway
railway login
railway init
railway deploy
```

## Fluxo de Autenticação

1. Usuário faz login no Streamlit
2. Streamlit envia credenciais para `/api/auth/login`
3. Flask valida no Supabase Auth
4. Supabase retorna sessão
5. Flask gera JWT interno e retorna ao Streamlit
6. Streamlit armazena token no session_state
7. Requisições futuras incluem token no header `Authorization: Bearer <token>`

## Regras de Negócio

### Cilindro
- Código único por usuário
- Valores padrão: 1kg = 956L, R$290
- Status: ativo, em_uso, esgotado, inativo

### Elemento
- Lista pré-carregada automática
- Consumo em L/min
- Nomes únicos por usuário

### Amostra
- Data/hora automática (editável)
- Vincular a cilindro e elemento existentes

### Tempo Chama
- Registrar duração em h/min/s
- Calcular consumo automaticamente
- Vincular a elemento e cilindro

## Validações

- Não permitir duplicatas
- Validar campos obrigatórios
- Confirmar antes de deletar
- Verificar permissões por role
- Proteger rotas com JWT

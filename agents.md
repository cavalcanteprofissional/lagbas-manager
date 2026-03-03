# LabGas Manager - Documentação Técnica

## Visão Geral

Dashboard para gestão de cilindro de gás e elementos analisados em laboratório de química, utilizando **Flask** com **Jinja2** para o frontend web e **Supabase** como banco de dados PostgreSQL.

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
- **Autenticação**: Supabase Auth (via Flask-Login)
- **Gerenciamento de Dependências**: pip + venv
- **Deploy**: Railway.app

## Estrutura de Diretórios

```
labgas-manager/
├── .gitignore
├── agents.md                  # Este arquivo
├── readme.md                  # Documentação do projeto
├── bd.md                     # Script SQL do banco de dados
├── bd_admin.md               # Script SQL admin (tabela perfil, compartilhamento)
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
└── frontend/                   # Flask + Jinja2 (Web)
    ├── app.py                 # Aplicação Flask principal
    ├── .env                   # Variáveis do frontend
    ├── requirements.txt        # Dependências Python
    ├── venv/                  # Virtual environment
    ├── Procfile               # Deploy Railway
    └── templates/              # Templates HTML Jinja2
        ├── base.html          # Layout base
        ├── login.html         # Login
        ├── register.html      # Registro
        ├── dashboard.html     # Dashboard
        ├── cilindro.html      # CRUD Cilindros
        ├── elemento.html      # CRUD Elementos
        ├── amostra.html       # CRUD Amostras
        └── perfil.html        # Perfil usuário
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
    cilindro_id INTEGER REFERENCES cilindro(id),
    elemento_id INTEGER REFERENCES elemento(id),
    quantidade_amostras INTEGER DEFAULT 1,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Nota**: O código usa nomes de tabelas no singular (`cilindro`, `elemento`, `amostra`).

### Tabela: perfil

```sql
CREATE TABLE perfil (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    role VARCHAR(20) DEFAULT 'usuario',
    ativo BOOLEAN DEFAULT true,
    nome VARCHAR(100),
    email VARCHAR(255),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Campos compartilhado

```sql
ALTER TABLE cilindro ADD COLUMN compartilhado BOOLEAN DEFAULT false;
ALTER TABLE elemento ADD COLUMN compartilhado BOOLEAN DEFAULT false;
ALTER TABLE amostra ADD COLUMN compartilhado BOOLEAN DEFAULT false;
```

### Políticas RLS

Devido a problemas de recursão infinita, as políticas RLS para admin foram removidas. O sistema agora usa service_role key para operações de admin (bypass RLS).

### Configuração SQL Admin (execute no Supabase SQL Editor)

```sql
-- Criar tabela perfil
CREATE TABLE IF NOT EXISTS perfil (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'usuario' CHECK (role IN ('admin', 'usuario')),
    ativo BOOLEAN DEFAULT true,
    nome VARCHAR(100),
    email VARCHAR(255),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Adicionar campos compartilhado
ALTER TABLE cilindro ADD COLUMN IF NOT EXISTS compartilhado BOOLEAN DEFAULT false;
ALTER TABLE elemento ADD COLUMN IF NOT EXISTS compartilhado BOOLEAN DEFAULT false;
ALTER TABLE amostra ADD COLUMN IF NOT EXISTS compartilhado BOOLEAN DEFAULT false;

-- Habilitar RLS
ALTER TABLE perfil ENABLE ROW LEVEL SECURITY;

-- Políticas RLS (apenas para operações não-admin)
DROP POLICY IF EXISTS "Users can view own perfil" ON perfil;
CREATE POLICY "Users can view own perfil" ON perfil
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own perfil" ON perfil;
CREATE POLICY "Users can update own perfil" ON perfil
    FOR UPDATE USING (auth.uid() = id);

-- Tornar primeiro usuário admin (substitua pelo email desejado)
INSERT INTO perfil (id, role, ativo)
SELECT id, 'admin', true 
FROM auth.users 
WHERE email = 'seu-email@exemplo.com'
ON CONFLICT (id) DO UPDATE SET role = 'admin', ativo = true;

-- Criar perfis para usuários existentes
INSERT INTO perfil (id, role, ativo, nome, email)
SELECT 
    u.id,
    'usuario',
    true,
    COALESCE(u.raw_user_meta_data->>'nome', ''),
    u.email
FROM auth.users u
LEFT JOIN perfil p ON u.id = p.id
WHERE p.id IS NULL;
```

## Sistema de Administração

### Funcionalidades Admin

| Recurso | Descrição |
|---------|-----------|
| Painel Admin | Lista todos os usuários com estatísticas |
| Ativar/Desativar usuário | Bloqueia acesso de usuários |
| Promover/Demover admin | Altera role do usuário |
| Deletar usuário | Remove usuário e todos os dados |
| Ver dados de qualquer usuário | Visualiza cilindro, elemento, amostra |

### Compartilhamento de Dados

- Usuários podem compartilharcilindros, elementos e amostras
- Dados compartilhados ficam visíveis para todos os usuários ativos
- Admins veem todos os dados (próprios + compartilhados + outros usuários)

### Rotas Admin

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /admin | Painel de administração |
| POST | /admin/toggle-user | Ativar/Desativar usuário |
| POST | /admin/set-role | Definir role (admin/usuario) |
| POST | /admin/delete-user | Deletar usuário e dados |
| GET | /admin/user-data/<id> | Ver dados de um usuário |

## Endpoints da API REST (Backend)

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

## Configuração de Ambiente

### Variáveis de Ambiente (Frontend - frontend/.env)

```env
SECRET_KEY=sua_chave_secreta_aqui
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon
SUPABASE_SERVICE_KEY=sua_service_role_key
```

**Nota**: A service_role key é armazenada no .env para operações de admin.

### Variáveis de Ambiente (Backend - backend/.env)

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=sua_chave_secreta_aqui
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon
SUPABASE_JWT_SECRET=seu_jwt_secret
```

## Como Rodar Local

### Frontend (Flask + Jinja2) - Porta 5000

```bash
cd frontend
python -m venv venv
./venv/Scripts/pip install -r requirements.txt
./venv/Scripts/python app.py
```

### Backend (API - opcional) - Porta 5001

```bash
cd backend
python -m venv venv
./venv/Scripts/pip install -r requirements.txt
./venv/Scripts/python app.py
```

**Nota**: O frontend roda na porta 5000 e o backend na porta 5001 para evitar conflitos.

## Deploy Railway

### Configuração Atual (Dockerfile)
O projeto utiliza Dockerfile para deploy no Railway.

1. Criar projeto no Railway com o repositório GitHub
2. O Railway detecta automaticamente o Dockerfile
3. Adicionar variáveis de ambiente:
   - `SECRET_KEY`: chave secreta para sessões
   - `SUPABASE_URL`: URL do projeto Supabase
   - `SUPABASE_KEY`: chave anônima do Supabase

### Build Command: (vazio)
### Start Command: `gunicorn app:app`

**Nota**: O deploy pode apresentar desafios dependendo da configuração do Railway. Verifique os logs de build em caso de erros.

## Fluxo de Autenticação

1. Usuário acessa o frontend Flask
2. Faz login com email/senha
3. Flask valida no Supabase Auth
4. Sessão gerenciada por Flask-Login (cookies)
5. Dados filtrados por user_id em todas as consultas

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
- Quantidade de amostras (inteiro)

## Validações

- Não permitir duplicatas (código de cilindro, nome de elemento)
- Validar campos obrigatórios
- Cilindro e elemento não podem ser excluídos se possuírem amostras vinculadas (mensagem de erro amigável)
- Proteger rotas com @login_required

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

### Funcionalidades Implementadas
- Sistema de admin com todas as funcionalidades operacionais
- Perfil de usuário mostra role corretamente
- Nome e email armazenados na tabela perfil
- Sistema de segurança com JWT (removido service_role key do frontend)
- Paginação em todas as listas (10 itens por página)
- Otimização de consultas (separação dados próprios vs compartilhados)
- Sistema de cache (5 minutos)
- Filtros em listas de cilindro, elemento e amostra
- Página de histórico
- Cards visuais no dashboard
- Toast notifications (feedback melhor ao usuário)
- Edição de perfil (nome) funcionando corretamente
- Criação automática de perfil no registro

### Versão
- v1.2.0 - Segurança, performance e UX aprimorados

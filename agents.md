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
├── database.md                # Schema completo do banco de dados
├── bd_admin.md                # Script SQL admin (tabela perfil, compartilhamento)
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
        ├── historico.html     # Histórico de atividades
        └── perfil.html        # Perfil usuário
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

### Tabela: perfil

```sql
CREATE TABLE perfil (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'usuario' CHECK (role IN ('admin', 'usuario')),
    ativo BOOLEAN DEFAULT true,
    nome VARCHAR(100),
    email VARCHAR(255),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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

## Políticas RLS

O sistema usa políticas RLS (Row Level Security) para controle de acesso:

- **SELECT**: Todos podem visualizar (política "Anyone can view")
- **INSERT/UPDATE/DELETE**: Apenas o próprio usuário (política com verificação de `auth.uid() = user_id`)
- **Admin**: Usa service_role key para bypass completo de RLS

Consulte o arquivo `database.md` para o SQL completo das políticas RLS.

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

- Usuários podem compartilhar cilindro, elemento e amostra
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

## Histórico de Atividades

O sistema registra todas as operações CRUD na tabela `historico_log`:

- **Tipo**: cilindro, elemento, amostra
- **Ação**: criado, atualizado, excluido
- **Nome**: identificação do item
- **User**: usuário que executou a ação

O histórico pode ser filtrado por:
- Tipo (Cilindros, Elementos, Amostras)
- Ação (Criado, Atualizado, Excluído)
- Texto de busca

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
| GET | /api/cilindros | Listar todos |
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

**Nota**: A service_role key é necessária para operações de admin (bypass RLS).

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
- Código deve seguir formato CIL-XXX (ex: CIL-001, CIL-002)
- Valores padrão: 1kg = 956L, R$290
- Status: ativo, em_uso, esgotado

### Elemento
- Lista pré-carregada automática (20 elementos padrão)
- Consumo em L/min
- Nomes únicos por usuário
- Nomes normalizados com primeira letra maiúscula

### Amostra
- Data default como data atual (pode ser alterada)
- Tempo de chama editável (HH:MM:SS)
- Vincular a cilindro e elemento existentes
- Quantidade de amostras (inteiro)

## Validações

- Não permitir duplicatas (código de cilindro, nome de elemento)
- Validar campos obrigatórios
- Cilindro e elemento não podem ser excluídos se possuírem amostras vinculadas
- Proteger rotas com @login_required
- **Cilindro**: Código deve seguir formato CIL-XXX
- **Elemento**: Nomes normalizados com primeira letra maiúscula

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
- Toast notifications (feedback ao usuário)
- Edição de perfil (nome) funcionando corretamente
- Criação automática de perfil no registro
- Validação de código de cilindro (CIL-XXX)
- Normalização de nomes de elementos (primeira maiúscula)
- Data default como hoje no registro de amostras
- Ordenação alfabética nos seletores de Cilindro/Elemento
- Remoção de elementos duplicados nos seletores de amostra

### Versão
- v1.3.0 - Sistema de histórico, filtros aprimorados, correções de bugs

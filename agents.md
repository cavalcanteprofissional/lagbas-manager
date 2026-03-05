# LabGas Manager - Documentação Técnica

## Visão Geral

Dashboard para gestão de cilindro de gás e elementos analisados em laboratório de química, utilizando **Flask** com **Jinja2** para o frontend web e **Supabase** como banco de dados PostgreSQL.

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
- **Autenticação**: Supabase Auth (via Flask-Login)
- **Gerenciamento de Dependências**: pip + venv
- **Deploy**: Railway.app

## Estrutura de Diretórios

```
labgas-manager/
├── .gitignore
├── AGENTS.md                    # Este arquivo
├── readme.md                    # Documentação do projeto
├── database.md                  # Schema completo do banco de dados
├── todo.md                      # Tarefas e histórico de alterações
├── backend/                     # Flask API (opcional)
│   ├── app.py
│   ├── .env
│   ├── requirements.txt
│   ├── venv/
│   ├── Procfile
│   ├── config.py
│   ├── routes/
│   └── utils/
└── frontend/                    # Flask + Jinja2 (Web)
    ├── app.py                   # Aplicação Flask principal (~130 linhas)
    ├── .env
    ├── requirements.txt
    ├── venv/
    ├── Procfile
    ├── blueprints/              # Blueprints Flask
    │   ├── __init__.py
    │   ├── auth.py             # Login, register, logout
    │   ├── cilindro.py         # CRUD Cilindros
    │   ├── elemento.py         # CRUD Elementos
    │   ├── amostra.py          # CRUD Amostras
    │   ├── admin.py            # Funções admin
    │   ├── historico.py        # Histórico de atividades
    │   └── helpers.py          # Funções auxiliares
    ├── utils/                   # Utilitários
    │   ├── __init__.py
    │   ├── supabase_utils.py   # Cliente Supabase
    │   ├── validators.py       # Validações
    │   └── constants.py        # Constantes
    └── templates/                # Templates HTML Jinja2
        ├── base.html
        ├── login.html
        ├── register.html
        ├── dashboard.html
        ├── cilindro.html
        ├── elemento.html
        ├── amostra.html
        ├── historico.html
        ├── perfil.html
        ├── admin.html
        └── admin_user_data.html
```

## Blueprints

| Blueprint | Arquivo | Rotas |
|-----------|---------|--------|
| Auth | auth.py | /login, /register, /logout |
| Cilindro | cilindro.py | /cilindros (GET, POST) |
| Elemento | elemento.py | /elementos (GET, POST) |
| Amostra | amostra.py | /amostras (GET, POST) |
| Admin | admin.py | /admin, /admin/toggle-user, /admin/set-role, /admin/delete-user, /admin/user-data/<id> |
| Historico | historico.py | /historico |

## Utils

| Arquivo | Funções |
|---------|---------|
| supabase_utils.py | get_supabase_client(), get_admin_client(), buscar_perfis_usuarios() |
| validators.py | safe_int(), safe_float(), validar_codigo_cilindro(), formatar_tempo_chama(), remover_duplicatas_por_campo() |
| constants.py | ITEMS_PER_PAGE, LITROS_EQUIVALENTES_KG, GAS_KG_DEFAULT, CUSTO_DEFAULT, CILINDRO_STATUS, ELEMENTOS_PADRAO |
| helpers.py | get_user_id(), is_admin(), is_user_active(), get_user_role(), get_authenticated_client(), get_admin_client(), registrar_historico() |

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

## Configuração de Ambiente

### Variáveis de Ambiente (frontend/.env)

```env
SECRET_KEY=sua_chave_secreta_aqui
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon
SUPABASE_SERVICE_KEY=sua_service_role_key
```

**Nota**: A service_role key é necessária para operações de admin (bypass RLS).

## Como Rodar Local

### Frontend (Flask + Jinja2) - Porta 5000

```bash
cd frontend
python -m venv venv
./venv/Scripts/pip install -r requirements.txt
./venv/Scripts/python app.py
```

## Deploy Railway

1. Criar projeto no Railway com o repositório GitHub
2. Adicionar variáveis de ambiente:
   - `SECRET_KEY`: chave secreta para sessões
   - `SUPABASE_URL`: URL do projeto Supabase
   - `SUPABASE_KEY`: chave anônima do Supabase

### Start Command
`gunicorn app:app`

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
- **Refatoração para Blueprints** - Código organizado por domínio

### Versão
- v1.4.0 - Refatoração para Blueprints, código modular

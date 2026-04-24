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
| Admin | admin.py | /admin, /admin/toggle-user, /admin/set-role, /admin/delete-user, /admin/user-data/<id>, /admin/export |
| Historico | historico.py | /historico |

## Utils

| Arquivo | Funções |
|---------|---------|
| supabase_utils.py | get_supabase_client(), get_admin_client(), buscar_perfis_usuarios() |
| validators.py | safe_int(), safe_float(), validar_codigo_cilindro(), formatar_tempo_chama(), remover_duplicatas_por_campo() |
| constants.py | ITEMS_PER_PAGE, LITROS_EQUIVALENTES_KG, GAS_KG_DEFAULT, CUSTO_DEFAULT, CILINDRO_STATUS, ELEMENTOS_PADRAO |
| helpers.py | get_user_id(), is_admin(), is_user_active(), get_user_role(), get_authenticated_client(), get_admin_client(), registrar_historico(), pode_acessar_aba(), get_habilitar_abas() |
| erros_utils.py | formatar_erro_supabase() - Converte erros técnicos em mensagens amigáveis |

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
    habilitar_abas JSONB DEFAULT '{"cilindro": true, "elemento": true, "amostra": true, "historico": true}',
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
| GET | /admin/export | Exportar dados (JSON/CSV/Excel/Markdown) |

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

## Sistema de Expiração de Sessão

- Sessão expira após **10 minutos de inatividade**
- A cada request válido, o timestamp de última atividade é atualizado
- Quando a sessão expira, o usuário é redirecionado para login com mensagem: "Sessão expirada por inatividade. Faça login novamente."
- Rotas públicas (login, register, logout, static) são ignoradas na verificação

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
- **Mensagens de erro amigáveis**: Erros técnicos do Supabase são convertidos para mensagens amigáveis

## Estado Atual

### Funcionalidades Implementadas
- **Expiração de Sessão v1.8.0**:
  - Sessão expira após 10 minutos de inatividade
  - Timestamp de atividade atualizado a cada request
  - Rotas públicas ignoradas na verificação
- **Mensagens de Erro Amigáveis v1.7.0**:
  - Conversão de erros técnicos do Supabase para mensagens amigáveis
  - Tratamento específico para erros RLS (42501), duplicatas (23505), foreign key (23503)
- **Correção RLS v1.7.0**:
  - Uso de get_authenticated_client() para operações INSERT/UPDATE/DELETE
  - Token JWT enviado corretamente para políticas RLS
- **Exportação de Dados v1.6.0**:
  - Admin pode exportar todo o banco de dados
  - Formatos: JSON, CSV, Excel (.xlsx), Markdown (.md)
  - Botão no dashboard disponível apenas para admin
  - Dados incluem cilindro, elemento, amostra com informações do usuário
- **Controle de Acesso por Abas v1.6.0**:
  - Admin pode habilitar/desabilitar abas para cada usuário
  - Abas controladas: Cilindros, Elementos, Amostras, Histórico
  - Usuários admin sempre têm acesso a todas as abas
  - Campo `habilitar_abas` JSON na tabela perfil
  - UI no painel admin com botões toggle por aba
  - Exibição de permissões no perfil do usuário
- **Segurança v1.5.0**:
  - Proteção CSRF em todos os formulários
  - Rate Limiting (5 tentativas/min login, 3 tentativas/min register)
  - Validação de role e status contra valores permitidos
  - Verificação de propriedade antes de delete (proteção IDOR)
  - Session fixation protection (session.clear() após login)
  - Cliente autenticado para operações RLS
  - Mensagens de erro amigáveis para login e registro
- **Dashboard v1.5.0**:
  - Card "Quantidade de Amostras por Cilindro"
  - Card "Consumo por Elemento × Tempo de Chama"
  - Card "Elementos mais analisados por Amostras"
  - Card "Eficiência de Cilindros por Elemento"
  - Padrão de cores: Cilindro=Verde, Elemento=Azul, Amostra=Rosa, Ativos=Roxo
- Mensagens de erro amigáveis para duplicatas (código 23505)
- Sistema de registro de histórico funcionando corretamente
- Datas formatadas em DD/MM/YYYY por todo o projeto
- Exclusão com mensagem clara quando há amostras vinculadas
- Sistema de admin com todas as funcionalidades operacionais
- Sistema de registro de histórico de atividades
- Painel admin lista todos os usuários cadastrados
- Perfil de usuário mostra role corretamente
- Nome e email armazenados na tabela perfil
- Sistema de segurança com JWT validation
- Paginação em todas as listas (10/25/50/100 itens por página)
- Otimização de consultas
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
- Multi-select com checkbox para exclusão em massa
- Status de cilindro: ativo, esgotado
- Dashboard com soma de quantidade_amostras (não apenas contagem de registros)
- Filtro de cilindro no card de Eficiência por Elemento

### Versão
- v1.9.0 - Dashboard com soma de quantidade_amostras e filtro de cilindro
- v1.8.0 - Sistema de expiração de sessão por inatividade
- v1.7.0 - Correções RLS, mensagens de erro amigáveis
- v1.6.0 - Exportação de dados e Controle de acesso por abas
- v1.5.0 - Correções de segurança (CSRF, IDOR, Rate Limiting, RLS)
- v1.4.1 - Correções de UX e mensagens amigáveis, formatação de datas
- v1.4.0 - Refatoração para Blueprints, código modular

## Sistema de Cores

### Cor Primária
- **Principal**: #0070b8
- **Descrição**: Cor base do projeto, derivada do ícone TSA

### Paleta de Cores (CSS Variables)

| Variável | Hex | Uso |
|----------|-----|-----|
| `--primary-darkest` | #002a47 | Sidebar background, textos muito escuros |
| `--primary-dark` | #003a5e | Sidebar hover, headers escuros |
| `--primary` | #0070b8 | Brand, botões primários |
| `--primary-light` | #4da3e8 | Gradientes, cards |
| `--primary-lighter` | #6cccff | Gráficos, acentos |
| `--primary-lightest` | #88d4ff | Highlights, bordas |
| `--accent` | #005f96 | Cilindro (variação) |
| `--accent-alt` | #4da3e8 | Elemento (variação) |

### Aplicações por Tipo

| Tipo | Gradient | Hex (início → fim) |
|------|----------|-----------------|
| Cilindro | linear-gradient | #005f96 → #4da3e8 |
| Elemento | linear-gradient | #003a5e → #4da3e8 |
| Amostra | linear-gradient | #0070b8 → #6cccff |
| Ativos | linear-gradient | #002a47 → #003a5e |
| Admin | linear-gradient | #002a47 → #004475 |
| Login/Register | linear-gradient | #0070b8 → #4da3e8 |

### Arquivos de Estilo
- **base.html**: CSS variables no :root + classes .stat-card
- **constants.py**: COR_TIPO com novas variações
- **login.html/register.html**: Gradiente unificado
- **dashboard.html**: Cards + gráficos
- **admin_user_data.html**: Headers dos cards

---

## v2.0.0 - Padrão de Cores #0070b8

### Visão Geral
Nova versão com padrão de cores unificado baseado na cor primária `#0070b8` (derivada do ícone TSA).

### Alterações de Cores

#### Sistema de Cores Global
- **Cor Primária**: `#0070b8`
- **8 variações de cores**: CSS Variables no :root
- **Todos os elementos ahora usam o padrão**: Botões, badges, gradientes, gráficos

#### Arquivos Modificados

| Arquivo | Alteração |
|---------|-----------|
| base.html | CSS Variables, botões Bootstrap, paginação, sidebar |
| constants.py | COR_TIPO + ELEMENTO_CORES (20 cores) |
| login.html | Gradient #0070b8 |
| register.html | Gradient #0070b8 |
| dashboard.html | 8 stat-cards + gráficos |
| admin.html | Botões admin |
| admin_user_data.html | Cards + paginação |
| perfil.html | 4 stat-cards |
| historico.html | Cores + paginação |
| amostra.html | Badges + alerta + modal |
| cilindro.html | Alerta de seleção |
| pressao.html | Alerta de seleção |
| elemento.html | Alerta de seleção |

#### Paleta de Cores (CSS Variables)

```css
:root {
    --primary-darkest: #002a47;
    --primary-dark: #003a5e;
    --primary: #0070b8;
    --primary-light: #4da3e8;
    --primary-lighter: #6cccff;
    --primary-lightest: #88d4ff;
    --accent: #005f96;
    --accent-alt: #4da3e8;
}
```

#### Aplicações por Tipo

| Tipo | Classe CSS | Gradient |
|------|------------|----------|
| Cilindro | stat-card | #005f96 → #4da3e8 |
| Pressão | stat-card.blue | #003a5e → #4da3e8 |
| Elementos | stat-card.pink | #0070b8 → #6cccff |
| Amostras | stat-card.purple | #002a47 → #003a5e |
| Ativos | stat-card.purple | #002a47 → #003a5e |
| Admin | stat-card | #002a47 → #004475 |
| Login/Register | background | #0070b8 → #4da3e8 |

### Novas Funcionalidades

#### estatisticas do Perfil
- 4 stat-cards: Cilindros, Pressões, Elementos, Amostras
- Grid 2x2 com cores diferenciadas

#### Dados do Usuário (Admin)
- Grid 2x2 com total de registros
- Card de Histórico com paginação e filtros

#### Histórico
- Paginação (20 itens por página)
- Filtros: Tipo, Ação
- Busca por nome
- Cores padronizadas nos badges

#### Cores de Elementos nos Gráficos
- Paleta de 20 cores para diferenciação de elementos
- Função JavaScript `getCoresPorElemento()` para atribuição dinâmica

### Correções de UI

- Alerta de seleção em massa padronizado
- Modal de edição com header gradiente
- Badges padronizados com cores do projeto
- Header do filtro "bg-light" → #f0f8ff
- Sidebar background: #0d1117 → #002a47

### Deploy Vercel

| Branch | URL Produção | Status |
|--------|---------------|--------|
| main | labgas-manager.vercel.app | Produção atual |
| v2-cores | (em configuração) | Beta/Novo |

---

## Deploy Guide (Vercel)

### Configuração do Projeto Vercel

1. **Conectar Repositório**
   - Acesse: https://vercel.com/new
   - Selecione "Import Project"
   - Escolha o repositório `labgas-manager`

2. **Configurações do Projeto**
   - Framework Preset: **Other**
   - Build Command: *(deixe vazio)*
   - Output Directory: *(deixe vazio)*
   - Install Command: *(deixe vazio)*

3. **Environment Variables**
   - `SECRET_KEY`: sua chave secreta
   - `SUPABASE_URL`: https://seu-projeto.supabase.co
   - `SUPABASE_KEY`: sua chave anon
   - `SUPABASE_SERVICE_KEY`: sua service role key

4. **Configurar domains Extras (opcional)**
   - Para produção: `labgas-manager.vercel.app`
   - Para v2: `v2.labgas-manager.vercel.app` (ou subdomain diferente)

### Versionamento

| Versão | Branch | Descrição |
|--------|--------|-----------|
| 1.x.x | main | Versão original |
| 2.x.x | v2-cores | Nova versão com padrão de cores |

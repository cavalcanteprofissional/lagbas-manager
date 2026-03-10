# LabGas Manager

**Versão: 1.8.0**

Dashboard para gestão de cilindro de gás e elementos analisados em laboratório de química, utilizando **Flask** com **Jinja2** para o frontend web e **Supabase** como banco de dados PostgreSQL.

---

## Recursos Principais

### Abas e Funcionalidades

| Aba | Funcionalidades |
|-----|-----------------|
| **Dashboard** | Cards com estatísticas, gráficos de amostras por cilindro, elementos mais analisados, eficiência de cylinders |
| **Cilindros** | CRUD completo, código CIL-XXX, status (ativo/esgotado), compartilhamento |
| **Elementos** | CRUD completo, consumo em L/min, 20 elementos padrão pré-carregados |
| **Amostras** | CRUD completo, vinculado a cilindro/elemento, tempo de chama, quantidade |
| **Histórico** | Log de todas as operações CRUD, filtros por tipo/ação |
| **Perfil** | Edição de nome, visualização de role e permissões |
| **Administração** | Painel admin, gerenciar usuários, controle de acesso por abas, exportar dados |

### Novidades v1.6.0

- **Exportação de Dados**: Admin pode exportar todo o banco de dados
  - Formatos: JSON, CSV, Excel (.xlsx), Markdown (.md)
  - Botão no dashboard disponível apenas para admin
- **Controle de Acesso por Abas**: Admin pode habilitar/desabilitar abas para cada usuário
  - Abas controladas: Cilindros, Elementos, Amostras, Histórico
  - Usuários admin sempre têm acesso a todas as abas

### Novidades v1.7.0

- **Correção RLS**: Uso de cliente autenticado para operações no banco
- **Mensagens de Erro Amigáveis**: Erros técnicos são convertidos para mensagens amigáveis

### Novidades v1.8.0

- **Expiração de Sessão**: Sessão expira após 10 minutos de inatividade
  - Usuário é redirecionado para login com mensagem explicativa

### Recursos de Segurança v1.5.0

- Proteção CSRF em todos os formulários
- Rate Limiting (5 tentativas/min login, 3 tentativas/min register)
- Validação de role e status contra valores permitidos
- Verificação de propriedade antes de delete (proteção IDOR)
- Session fixation protection
- Cliente autenticado para operações RLS

---

## Tecnologias

- **Frontend**: Flask 3.0 + Jinja2 + Bootstrap 5 + Bootstrap Icons
- **Banco de Dados**: Supabase (PostgreSQL)
- **Autenticação**: Supabase Auth (via Flask-Login)
- **Gerenciamento de Dependências**: pip + venv
- **Deploy**: Railway.app

---

## Arquitetura do Sistema

```
┌─────────────────┐     ┌─────────────────┐
│   Flask+Jinja2  │────▶│    Supabase    │
│  (Frontend Web) │     │  (PostgreSQL)  │
│   + Blueprints  │     │                │
└─────────────────┘     └─────────────────┘
```

---

## Estrutura de Diretórios

```
labgas-manager/
├── .gitignore
├── AGENTS.md                  # Documentação técnica
├── readme.md                  # Este arquivo
├── database.md               # Schema completo do banco de dados
├── frontend/                  # Flask + Jinja2 (Web)
│   ├── app.py                 # Aplicação Flask principal
│   ├── blueprints/            # Blueprints Flask
│   │   ├── auth.py           # Login, register, logout
│   │   ├── cilindro.py       # CRUD Cilindros
│   │   ├── elemento.py       # CRUD Elementos
│   │   ├── amostra.py        # CRUD Amostras
│   │   ├── admin.py          # Funções admin
│   │   ├── historico.py      # Histórico de atividades
│   │   └── helpers.py        # Funções auxiliares
│   ├── utils/                # Utilitários
│   │   ├── supabase_utils.py # Cliente Supabase
│   │   ├── validators.py     # Validações
│   │   └── constants.py      # Constantes
│   └── templates/            # Templates HTML Jinja2
```

---

## Como Rodar Local

### Pré-requisitos

- Python 3.10+
- pip

### Instalação

```bash
# 1. Clonar o repositório e entrar na pasta frontend
cd frontend

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente virtual (Windows)
venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements.txt
```

### Configuração

Crie o arquivo `frontend/.env` com as variáveis de ambiente:

```env
SECRET_KEY=sua_chave_secreta_aqui
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon
SUPABASE_SERVICE_KEY=sua_service_role_key
```

**Nota**: A `service_role_key` é necessária para operações de admin (bypass RLS).

### Executar

```bash
python app.py
```

O frontend estará disponível em: `http://localhost:5000`

---

## Regras de Negócio

### Cilindro
- Código único por usuário
- Código deve seguir formato CIL-XXX (ex: CIL-001, CIL-002)
- Valores padrão: 1kg = 956L, R$290
- Status: ativo, esgotado

### Elemento
- Lista pré-carregada automática (20 elementos padrão)
- Consumo em L/min
- Nomes únicos por usuário (primeira letra maiúscula)

### Amostra
- Data default como data atual
- Tempo de chama editável (HH:MM:SS)
- Vincular a cilindro e elemento existentes
- Quantidade de amostras (inteiro)

---

## Funcionalidades Implementadas

### Geral
- Sistema de autenticação (login/register/logout)
- Dashboard com cards de estatísticas
- Paginação em todas as listas (10/25/50/100 itens por página)
- Filtros em listas de cilindro, elemento e amostra
- Sistema de cache (5 minutos)
- Toast notifications
- Design responsivo com Bootstrap 5

### CRUD
- Criação, edição e exclusão de Cilindros
- Criação, edição e exclusão de Elementos
- Criação, edição e exclusão de Amostras
- Multi-select com checkbox para exclusão em massa

### Admin
- Painel de administração com lista de usuários
- Ativar/Desativar usuários
- Promover/Demover usuários (admin/usuario)
- Deletar usuário e todos os dados associados
- Visualizar dados de qualquer usuário
- Controle de acesso por abas
- Exportação de dados (JSON/CSV/Excel/Markdown)

### Histórico
- Registro de todas as operações CRUD
- Filtros por tipo (cilindro/elemento/amostra) e ação (criado/atualizado/excluido)
- Exibição do usuário que realizou a ação

### Validações
- Não permitir duplicatas (código de cilindro, nome de elemento)
- Cilindro e elemento não podem ser excluídos se possuírem amostras vinculadas
- Validação de código de cilindro (CIL-XXX)
- Normalização de nomes de elementos
- **Mensagens de erro amigáveis**: Erros técnicos são convertidos para mensagens amigáveis

---

## Deploy no Railway

1. Criar projeto no Railway com o repositório GitHub
2. Adicionar variáveis de ambiente:
   - `SECRET_KEY`: chave secreta para sessões
   - `SUPABASE_URL`: URL do projeto Supabase
   - `SUPABASE_KEY`: chave anônima do Supabase
3. Start Command: `gunicorn app:app`

---

## Changelog

| Versão | Descrição |
|--------|-----------|
| v1.8.0 | Sistema de expiração de sessão por inatividade (10 min) |
| v1.7.0 | Correções RLS, mensagens de erro amigáveis |
| v1.6.0 | Exportação de dados (JSON/CSV/Excel/Markdown) + Controle de acesso por abas |
| v1.5.0 | Correções de segurança (CSRF, IDOR, Rate Limiting, RLS) |
| v1.4.1 | Correções de UX e mensagens amigáveis, formatação de datas |
| v1.4.0 | Refatoração para Blueprints, código modular |

---

## Licença

MIT

# Tarefas de Segurança - LabGas Manager

## Fase 1 - CRÍTICO (Implementação Imediata) ✅ CONCLUÍDO

### 1.1 IDOR em Operações de Delete
- [x] Adicionar verificação de propriedade antes de excluir em cilindro.py
- [x] Adicionar verificação de propriedade antes de excluir em elemento.py  
- [x] Adicionar verificação de propriedade antes de excluir em amostra.py

### 1.2 Ausência de Proteção CSRF
- [x] Instalar flask-wtf
- [x] Configurar CSRFProtect em app.py
- [x] Adicionar token CSRF em todos os formulários (templates)

### 1.3 Secret Key Fallback
- [x] Remover fallback de secret_key em app.py
- [x] Adicionar validação obrigatória da variável de ambiente

---

## Fase 2 - HIGH (Curto Prazo) ✅ CONCLUÍDO

### 2.1 Rate Limiting
- [x] Adicionar flask-limiter ao requirements.txt
- [x] Configurar limite de tentativas em /login (5 por minuto)
- [x] Configurar limite em /register (3 por minuto)

---

## Fase 3 - MEDIUM (Médio Prazo) ✅ CONCLUÍDO

### 3.1 Validação de Role
- [x] Validar role contra valores permitidos em admin.py

### 3.2 Validação de Status
- [x] Validar status contra CILINDRO_STATUS em cilindro.py

### 3.3 Padrão Singleton de Clientes
- [x] Refatorar supabase_utils.py para usar Flask g object

---

## Fase 4 - LOW (Melhorias Contínuas) ✅ CONCLUÍDO

### 4.1 Logging
- [x] Revisar logs para remover dados sensíveis

### 4.2 Session Fixation
- [x] Implementar regeneração de session ID após login

---

## Fase 5 - Controle de Acesso às Abas ✅ CONCLUÍDO

### Descrição
Admin pode habilitar/desabilitar acesso às abas para usuários comuns.

### Abas Controladas
- Cilindros
- Pressão
- Elementos
- Amostras
- Histórico

### Comportamento Default
- Todas as abas **habilitadas** para novos usuários por padrão
- Admin tem acesso a todas as abas

### Tarefas
- [x] Adicionar campo `habilitar_abas` na tabela perfil (JSON)
- [x] Criar função `pode_acessar_aba()` em helpers.py
- [x] Verificar permissão nas rotas de cilindro, elemento, amostra, historico
- [x] Adicionar UI no admin para gerenciar permissões
- [x] Ocultar menus das abas se usuário não tem permissão

---

## Estrutura de Diretórios - Futuro Backend

### Decisão de Arquitetura

O projeto mantém dois diretórios para permitir evolução futura:

| Diretório | Conteúdo | Status |
|-----------|----------|--------|
| `frontend/` | Flask + Jinja2 (app completo) | **Em uso** - Produção |
| `backend/` | Estrutura para API REST futura | Reservado para desenvolvimento |

### Motivação
- Atualmente todo o código (UI + API) está em `frontend/`
- O diretório `backend/` está reservado para quando um backend maduro e profissional for necessário
- Mantém a separação conceitual de responsabilidades

---

## Fase 11 - Paleta de Cores por KPI no Dashboard ⏳

### Descrição
Cada KPI (Cilindros, Elementos, Amostras) terá uma cor diferente mantendo padrões de gradiente/degrade.

### Tarefas

#### 11.1 Paleta Verde para Cilindros
- [x] Adicionar variáveis CSS `--green-*` no `:root` (base.html)
  - `--green-darkest`: #004d40
  - `--green-dark`: #00695c
  - `--green`: #00897b
  - `--green-light`: #4db6ac
  - `--green-lighter`: #80cbc4
  - `--green-lightest`: #b2dfdb
- [x] Atualizar stat-card.green para usar nova paleta (base.html)
- [x] Atualizar gráfico "Quantidade de Amostras por Cilindro" com paleta verde (dashboard.html)
- [x] Atualizar header do card com gradiente verde (dashboard.html)

#### 11.2 Paleta para Elementos (pendente)
- [ ] Definir paleta de cores
- [ ] Aplicar no stat-card.blue
- [ ] Aplicar no gráfico relacionado

#### 11.3 Paleta para Amostras (pendente)
- [x] Adicionar variáveis CSS `--pink-*` no `:root` (base.html)
- [x] Atualizar stat-card.pink para usar nova paleta (base.html)
- [x] Atualizar gráfico "Elementos mais analisados por Amostras" com paleta rosa (dashboard.html)
- [x] Adicionar constante `ELEMENTO_CORES_AMOSTRAS` (constants.py)
- [x] Aplicar no header do card relacionado (dashboard.html)
- [x] Padronizar tags de cilindro (verde) em todas as abas (amostra.html, historico.html, admin_user_data.html)
- [x] Padronizar tags de amostra (rosa) em todas as abas (amostra.html, historico.html, admin_user_data.html)
- [x] Adicionar variáveis CSS `--purple` e `--purple-light` (base.html)
- [x] Tag "Consumo (L/min)" em roxo (elemento.html)
- [x] Tag "Qtd" em roxo claro (amostra.html)
- [x] Código do cilindro em tag verde em todas as abas (dashboard, cilindro, pressao, historico)
- [x] Elemento em tag azul (--primary-light) em todas as abas (dashboard, elemento, amostra, historico)

---

## Projeto Concluído ✅

> As tarefas de segurança acima estão em andamento. Abaixo está o histórico do projeto.

### 2026-03-05 - Refatoração para Blueprints

#### Estrutura Implementada

```
frontend/
├── app.py                      # Main app (~130 linhas)
├── blueprints/
│   ├── __init__.py
│   ├── auth.py                # Login, register, logout
│   ├── cilindro.py            # CRUD cilindro
│   ├── elemento.py           # CRUD elemento
│   ├── amostra.py             # CRUD amostra
│   ├── admin.py               # Funções admin
│   ├── historico.py           # Histórico
│   └── helpers.py             # Funções auxiliares
├── utils/
│   ├── __init__.py
│   ├── supabase_utils.py      # Cliente Supabase
│   ├── validators.py          # Validações
│   └── constants.py           # Constantes
└── templates/
```

#### Blueprints

| Blueprint | Rotas |
|-----------|-------|
| auth.py | /login, /register, /logout |
| cilindro.py | /cilindros |
| elemento.py | /elementos |
| amostra.py | /amostras |
| admin.py | /admin, /admin/toggle-user, /admin/set-role, /admin/delete-user, /admin/user-data/<id> |
| historico.py | /historico |
| helpers.py | get_user_id, is_admin, is_user_active, get_user_role, etc |

#### Utils

| Arquivo | Funções |
|---------|---------|
| supabase_utils.py | get_supabase_client, get_admin_client, buscar_perfis_usuarios |
| validators.py | safe_int, safe_float, validar_codigo_cilindro, formatar_tempo_chama |
| constants.py | ITEMS_PER_PAGE, LITROS_EQUIVALENTES_KG, CILINDRO_STATUS, ELEMENTOS_PADRAO |

---

## Histórico de Correções

### 2026-03-06
- Mensagens de erro amigáveis para duplicatas (código 23505)
- Registro no histórico corrigido (agora usa admin_client)
- Adiciona filtro Jinja2 formatar_data para DD/MM/YYYY
- Corrige mensagem ao excluir cilindro/elemento com amostras vinculadas
- Análise de segurança completa identificando 11 vulnerabilidades
- Removido status 'em_uso' do cilindro

### 2026-03-05
- Refatoração completa para Blueprints
- app.py reduzido de ~1250 linhas para ~130 linhas
- Separação por domínio (auth, cilindro, elemento, amostra, admin, historico)
- Funções auxiliares em helpers.py
- Constantes centralizadas em constants.py
- Correção import request no perfil
- Correção load_dotenv no helpers.py
- Correção url_for nos templates para usar notação blueprint.nome
- Logging adicionado para debug de is_admin()

### 2026-03-04
- Validação de entrada segura (safe_int/safe_float)
- Try-except em operações de delete
- Remoção de código duplicado
- Funções auxiliares extraídas
- Otimização N+1 do histórico
- Sistema de logging implementado
- Adicionado sistema de registro de histórico de atividades
- Removido seletor de filtro "compartilhado"
- Corrigido filtro de "Cilindros" na aba Histórico
- Adicionado campo data default (data de hoje)
- Ordenação alfabética nos seletores
- Adicionado coluna "Usuário" no Histórico
- Unificação arquivos BD → database.md
- Correção erro RLS
- Remoção de elementos duplicados

### 2026-03-03
- Corrigido filtro na aba "Amostras"
- Corrigido admin para visualizar todos os usuários
- Adicionado validação de código de cilindro (CIL-XXX)
- Adicionado normalização de nomes de elementos

### 2026-03-28
- Ordenação alfabética na legenda do card "Quantidade de Amostras por Cilindro" no dashboard

### 2026-03-31 - Migração Railway → Vercel

#### Motivação
- Railway expirou o plano gratuito

#### Deploy Vercel
- URL: https://lagbas-manager.vercel.app/
- Criado `frontend/vercel.json` para deploy na pasta frontend
- Ajuste em app.py: debug=False por padrão (variação via FLASK_DEBUG)

#### Correção 2026-03-31 (NOT_FOUND error)
- Moveu vercel.json de raiz para frontend/ (requerido pelo Vercel)

#### Configurações Necessárias no Vercel
- `SECRET_KEY`: chave secreta para sessões
- `SUPABASE_URL`: URL do projeto Supabase
- `SUPABASE_KEY`: chave anônima do Supabase
- `SUPABASE_SERVICE_KEY`: service role key (para operações admin)
- Opcional: `FLASK_DEBUG=true` para desenvolvimento

#### Estrutura de Arquivos
```
labgas-manager/
├── vercel.json           # Configuração Vercel (NOVO)
├── frontend/
│   ├── app.py            # Flask app
│   ├── blueprints/       # Blueprints
│   ├── templates/        # Templates Jinja2
│   └── requirements.txt
└── backend/             # (não usado no Vercel)
```

#### Procedimento de Deploy
1. Conectar repositório GitHub no Vercel
2. Configurar variáveis de ambiente no painel Vercel
3. Deploy automático ao push na branch principal

---

## Fase 6 - Log de Usuários no Histórico ✅ CONCLUÍDO

### Descrição
Implementar registro no histórico de eventos relacionados a usuários (cadastro, alteração de role, permissões de abas).

### Tarefas

#### 6.1 Log de Cadastro de Usuário
- [x] Adicionar `registrar_historico()` em `auth.py` após criar perfil
- [x] Tipo: `perfil`, Ação: `criado`, Nome: email do usuário
- [x] Arquivo: `frontend/blueprints/auth.py`

#### 6.2 Log de Alteração de Role
- [x] Adicionar registro em `admin.py:set_role()` após atualizar role
- [x] Tipo: `perfil`, Ação: `atualizado`, Nome: "Role alterada para admin/usuario"
- [x] Arquivo: `frontend/blueprints/admin.py`

#### 6.3 Log de Ativação/Desativação de Usuário
- [x] Adicionar registro em `admin.py:toggle_user()` após atualizar status
- [x] Tipo: `perfil`, Ação: `atualizado`, Nome: "Usuário ativado/desativado"
- [x] Arquivo: `frontend/blueprints/admin.py`

#### 6.4 Log de Alteração de Permissões de Abas
- [x] Rota `update_habilitar_abas` já existia - adicionado registro
- [x] Adicionar registro após alterar permissões
- [x] Tipo: `perfil`, Ação: `atualizado`, Nome: "Aba X habilitada/desabilitada"
- [x] Arquivo: `frontend/blueprints/admin.py`

### Estrutura de Dados no Histórico

| Campo | Exemplo Cadastro | Exemplo Role | Exemplo Toggle | Exemplo Permissões |
|-------|------------------|--------------|----------------|-------------------|
| tipo | perfil | perfil | perfil | perfil |
| ação | criado | atualizado | atualizado | atualizado |
| nome | "usuario@email.com" | "Role alterada para admin" | "Usuário ativado" | "Aba Cilindros habilitada" |
| user_id | ID do novo usuário | ID do admin | ID do admin | ID do admin |

---

## Fase 7 - Auditoria Frontend vs Backend (3ª Verificação) ⏳

### Inconsistências Encontradas

#### 7.7 admin.py - JSON export usa "temperaturas"
- **Arquivo**: `frontend/blueprints/admin.py`
- **Linha**: 321
- **Problema**: O JSON export usa `"temperaturas": pressoes_data` mas deveria ser `"pressoes": pressoes_data`
- **Status**: [x] Concluído ✅

#### 7.8 admin.py - CSV export usa "TEMPERATURAS"
- **Arquivo**: `frontend/blueprints/admin.py`
- **Linha**: 359
- **Problema**: O CSV export usa `# TEMPERATURAS\n` mas deveria ser `# PRESSOES\n`
- **Status**: [x] Concluído ✅

#### 7.9 admin.py - CSV export não inclui campo "pressao"
- **Arquivo**: `frontend/blueprints/admin.py`
- **Linha**: 368
- **Problema**: Os headers do CSV para pressoes não incluem o campo "pressao" (apenas inclui temperatura)
- **Status**: [x] Concluído ✅

---

## Fase 7 - Auditoria Frontend vs Backend (2ª Verificação) ✅ CONCLUÍDO

### Inconsistências Encontradas

#### 7.6 auth.py - Falta "pressao" no habilitar_abas do registro
- **Arquivo**: `frontend/blueprints/auth.py`
- **Linha**: 196
- **Problema**: Ao criar novo usuário via registro, o campo `habilitar_abas` não inclui "pressao"
- **Código atual**: `{"cilindro": True, "elemento": True, "amostra": True, "historico": True}`
- **Deveria ser**: `{"cilindro": True, "pressao": True, "elemento": True, "amostra": True, "historico": True}`
- **Status**: [x] Concluído ✅

### Resumo das Correções

| # | Arquivo | Linha | Problema | Solução |
|---|---------|-------|----------|---------|
| 1 | auth.py | 196 | Falta "pressao" no habilitar_abas | Adicionar "pressao": True ao JSON |

---

## Fase 7 - Auditoria Frontend vs Backend (1ª Verificação) ✅ CONCLUÍDO

### Descrição
Analise completa do projeto para verificar consistência entre as chamadas do frontend e a estrutura do banco de dados Supabase.

### Inconsistências Encontradas

#### 7.1 Bug Crítico - Exportação Excel em admin.py
- **Arquivo**: `frontend/blueprints/admin.py`
- **Linha**: 428
- **Problema**: Na exportação Excel, o sheet é criado como `ws_pressoes` mas na hora de adicionar dados, referencia `ws_temperaturas` que não existe
- **Código atual**: `ws_temperaturas.append(headers)`
- **Deveria ser**: `ws_pressoes.append(headers)`
- **Status**: [x] Concluído ✅

#### 7.2 Inconsistência "temperatura" vs "pressao" no admin.html
- **Arquivo**: `frontend/templates/admin.html`
- **Linha**: 61
- **Problema**: Usa `user.temperaturas` mas a variável correta é `user.pressoes`
- **Status**: [x] Concluído ✅

#### 7.3 Inconsistência no habilitar_abas (admin.html)
- **Arquivo**: `frontend/templates/admin.html`
- **Linha**: 67, 200
- **Problema**: Usa `user.habilitar_abas.temperatura` mas o campo correto é `user.habilitar_abas.pressao`
- **Status**: [x] Concluído ✅

#### 7.4 ABA errada no admin.html
- **Arquivo**: `frontend/templates/admin.html`
- **Linha**: 83, 216
- **Problema**: Usa `aba="temperatura"` mas deveria ser `aba="pressao"`
- **Status**: [x] Concluído ✅

#### 7.5 Delete não remove dados relacionados (admin.py)
- **Arquivo**: `frontend/blueprints/admin.py`
- **Linha**: 151-155
- **Problema**: Ao deletar usuário, não remove os registros de `pressao` e `historico_log` vinculados ao user_id
- **Status**: [x] Concluído ✅

### Resumo das Correções

| # | Arquivo | Linha | Problema | Solução |
|---|---------|-------|----------|---------|
| 1 | admin.py | 428 | `ws_temperaturas` → `ws_pressoes` | Corrigir nome da variável |
| 2 | admin.html | 61 | `user.temperaturas` → `user.pressoes` | Corrigir nome do campo |
| 3 | admin.html | 67 | `.temperatura` → `.pressao` | Corrigir nome do campo JSON |
| 4 | admin.html | 83 | `aba="temperatura"` → `aba="pressao"` | Corrigir valor do campo |
| 5 | admin.py | 151-155 | Adicionar deletes para pressao e historico_log | Adicionar client.table("pressao").delete() e client.table("historico_log").delete() |

---

## Fase 7 - Auditoria Frontend vs Backend (3ª Verificação) ✅ CONCLUÍDO

### Inconsistências Encontradas

#### 7.7 admin.py - JSON export usa "temperaturas"
- **Arquivo**: `frontend/blueprints/admin.py`
- **Linha**: 321
- **Problema**: O JSON export usa `"temperaturas": pressoes_data` mas deveria ser `"pressoes": pressoes_data`
- **Status**: [x] Concluído ✅

#### 7.8 admin.py - CSV export usa "TEMPERATURAS"
- **Arquivo**: `frontend/blueprints/admin.py`
- **Linha**: 359
- **Problema**: O CSV export usa `# TEMPERATURAS\n` mas deveria ser `# PRESSOES\n`
- **Status**: [x] Concluído ✅

#### 7.9 admin.py - CSV export não inclui campo "pressao"
- **Arquivo**: `frontend/blueprints/admin.py`
- **Linha**: 368
- **Problema**: Os headers do CSV para pressoes não incluem o campo "pressao" (apenas inclui temperatura)
- **Status**: [x] Concluído ✅

---

## Fase 8 - Documentação do Banco de Dados ✅ CONCLUÍDO

### Descrição
Criar diretório database/ com schema, RLS, seed e diagrama do banco de dados.

### Tarefas
- [x] Criar diretório `database/`
- [x] Criar `schema.sql` com CREATE TABLE + índices
- [x] Criar `rls.sql` com políticas RLS
- [x] Criar `seed.sql` com elementos padrão (referência)
- [x] Criar `diagram.md` com diagrama em formato Mermaid

---

## Fase 10 - Deploy Vercel (Frontend Only) ✅ CONCLUÍDO

### Descrição
Deploy do frontend na Vercel. Problema: erro 500 FUNCTION_INVOCATION_FAILED.

### Problema Identificado
1. O código usava `load_dotenv('.env.local')` que não existe na Vercel
2. Variáveis do Supabase com nomes diferentes (SUPABASE_ANON_KEY vs SUPABASE_KEY)
3. 404: Rotas não reconhecidas

### Solução Aplicada
- **load_dotenv**: Agora tenta carregar .env.local mas não falha se não existir
- **Variáveis Supabase**: Usa fallback para ambos os nomes (local e Vercel)
- **vercel.json**: Criado em frontend/ para configuração específica

### Configurações do Projeto Vercel

| Configuração | Valor |
|-------------|-------|
| Framework Preset | Flask |
| Build Command | *(vazio)* |
| Output Directory | *(vazio)* |

### Environment Variables Necessárias

| Variável | Descrição |
|----------|------------|
| SECRET_KEY | Chave secreta para sessões (gere com Python) |
| As variáveis do Supabase são injetadas automaticamente | |

### Nomenclatura de Variáveis

| Ambiente | Variáveis Usadas |
|----------|------------------|
| **Desenvolvimento Local** | `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY` |
| **Vercel (automático)** | `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` |

### Deploy Simplificado
- Apenas frontend deployado (backend não necessário)
- Todo o código (UI + API) está em frontend/app.py
- Arquivo de configuração: `frontend/vercel.json`

---

## Fase 9 - Limpeza de Arquivos ✅ CONCLUÍDO

### Descrição
Remover arquivos e diretórios desnecessários do projeto.

### Tarefas
- [x] Remover diretório `codigo/` (vazio)
- [x] Remover diretório `figuras/` (vazio)
- [x] Adicionar diretório `database/` à documentação

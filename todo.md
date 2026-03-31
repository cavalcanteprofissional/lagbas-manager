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

## Fase 5 - Controle de Acesso às Abas (Futuro) ⏳

### Descrição
Admin pode habilitar/desabilitar acesso às abas para usuários comuns.

### Abas Controladas
- Cilindros
- Elementos
- Amostras
- Histórico

### Comportamento Default
- Todas as abas **desabilitadas** para usuários comuns por padrão
- Admin tem acesso a todas as abas

### Tarefas
- [ ] Adicionar campo `habilitar_abas` na tabela perfil (JSON)
- [ ] Criar função `pode_acessar_aba()` em helpers.py
- [ ] Verificar permissão nas rotas de cilindro, elemento, amostra, historico
- [ ] Adicionar UI no admin para gerenciar permissões
- [ ] Ocultar menus das abas se usuário não tem permissão

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

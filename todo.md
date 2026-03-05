# Tarefas Pendentes

## Projeto Concluído ✅

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

# Tarefas Pendentes

Nenhuma tarefa pendente no momento.

---

## Histórico de Correções

### 2026-03-04
- Adicionado sistema de registro de histórico de atividades (tabela `historico_log`)
- Removido seletor de filtro "compartilhado" nas abas Elementos e Cilindros
- Corrigido filtro de "Cilindros" na aba Histórico (typeMap JavaScript)
- Adicionado campo data default (data de hoje) na aba Amostras
- Ordenação alfabética nos seletores de Cilindro/Elemento na aba Amostras
- Adicionado coluna "Usuário" no Histórico
- Unificação arquivos BD (`bd.md`, `rls_politicians_bd.md`, `schema_bd.md` → `database.md`)
- Correção erro RLS criação cilindro/elemento/amostra (admin usa `get_admin_client()`)
- Correção exclusão cilindro/elemento (verificação de amostras vinculadas para admin)
- Remoção de elementos duplicados no filtro/seletor de amostras

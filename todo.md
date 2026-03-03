# Tarefas Pendentes

## Bug: Filtro de Elementos na aba Histórico

**Descrição:** Na aba "Histórico", o filtro de "Elementos" não retorna nenhum resultado, enquanto os filtros de "Cilindros" e "Amostras" funcionam corretamente.

**Localização:** `frontend/templates/historico.html`

**Problema:** A função JavaScript `filterHistory()` não está conseguindo normalizar o texto do badge de "Elementos" para corresponder ao valor do filtro.

**Última tentativa de correção:** 
- Adicionei mapeamento explícito (`typeMap`) para converter "elementos" → "elemento", mas não funcionou.

**Próximos passos sugeridos:**
1. Verificar no navegador (F12 → Elements) o texto exato que aparece no badge de "Elementos"
2. Pode ser que o texto seja "Elemento" (singular) ao invés de "Elementos" (plural)
3. Ajustar o mapeamento conforme necessário

---

## Histórico de Correções

### 2026-03-03
- Corrigido filtro na aba "Amostras" - índices de células errados na função JavaScript
- Corrigido admin para visualizar todos os usuários - agora usa `get_admin_client()` com service_role key
- Adicionado validação de código de cilindro (CIL-XXX)
- Adicionado normalização de nomes de elementos (primeira letra maiúscula)

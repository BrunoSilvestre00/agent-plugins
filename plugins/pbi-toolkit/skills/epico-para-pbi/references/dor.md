# Definition of Ready (PBI pronto para a sprint)

- [ ] Issue criada no Jira, vinculada ao épico pai, **sem assignee**, com o corpo completo do PBI e a linha `📄 Fonte versionada: <link com repositório identificado>` no topo
- [ ] Artefato `.md` gravado em `docs/pbis/<epico>/` com frontmatter completo (incluindo `jira:`)
- [ ] Título no padrão `[Área] Verbo + objeto`
- [ ] Contexto/valor explícito (responde "por quê?")
- [ ] Gherkin: pelo menos 1 caminho feliz + 1 caso de erro
- [ ] Fora de escopo preenchido
- [ ] Dependências mapeadas (`depende_de` no frontmatter + links no Jira); nenhuma bloqueia o início
- [ ] Restrições contêm só imposições reais (sem decisões de implementação disfarçadas)
- [ ] Se este é o PBI que introduz uma entidade nova (tipicamente o caminho mínimo/walking skeleton): Regras de negócio tem o contrato de campos completo (cada campo, obrigatório ou opcional) — não uma lista de exemplos
- [ ] Design linkado ou "não se aplica" (com estados vazio/carregando/erro/sucesso, se houver UI)
- [ ] Medição definida
- [ ] Cabe em 1 sprint
- [ ] Pendências, se aceitas pelo PO, estão como `[NEEDS CLARIFICATION]` explícito no artefato

- [ ] Sem `[NEEDS CLARIFICATION]` → pode ir para o `{status_ready}` (se configurado); com pendência, fica fora até o PO resolver

> A Definition of Done técnica (tasks, testes, lint, PR, verificação por critério de aceite) pertence ao toolkit/processo de desenvolvimento que o time usar naquele repo. Não duplique aqui.

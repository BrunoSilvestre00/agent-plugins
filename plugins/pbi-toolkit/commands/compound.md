---
description: Extrai e salva as lições aprendidas de um épico/PBI em docs/knowledge/, para os próximos refinamentos consultarem
argument-hint: [chave do épico/PBI ou contexto do que foi aprendido — opcional]
---

Use a skill `epico-para-pbi` deste plugin, seção "Compound — lições aprendidas", seguindo o formato de `references/licoes.md`.

Contexto fornecido: $ARGUMENTS

Fontes a considerar: a conversa atual, os artefatos em `docs/pbis/`, o estado das issues no Jira (via tools oficiais da Atlassian, se disponíveis — ex.: PBIs que voltaram, viraram bug ou estouraram a sprint) e o histórico do git quando relevante.

Extraia no máximo 1–3 lições por execução, valide cada uma com o usuário antes de gravar, verifique contradições com lições existentes em `docs/knowledge/` e não commite sem o usuário pedir.

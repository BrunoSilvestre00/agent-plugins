---
name: code-review-conventions
description: Convenções do time para revisar pull requests com foco em correção, clareza e feedback acionável — vale para qualquer stack.
version: 0.1.0
---

# Convenções de code review

Use esta skill ao revisar um pull request do time, de qualquer stack. Se
o repositório também tiver uma skill de review específica de stack
(`frontend-code-review-conventions`, `backend-code-review-conventions`),
use as duas juntas — esta cobre as prioridades gerais, a outra cobre os
pontos específicos daquele stack.

## Prioridades da revisão (nesta ordem)

1. **Correção**: o código faz o que o PR diz que faz? Há casos de borda não tratados?
2. **Testes**: toda mudança de comportamento tem teste correspondente; teste novo falha sem a mudança.
3. **Clareza**: nomes descritivos, funções curtas, sem comentários que apenas repetem o código.
4. **Escopo**: o PR faz uma coisa só; refactors oportunistas vão em PR separado.

## Como comentar

- Prefixe cada comentário com a severidade: `[blocker]`, `[sugestão]` ou `[nit]`.
- Todo `[blocker]` explica o problema e propõe um caminho — nunca só aponta.
- Elogie o que está bom: revisão não é só encontrar defeito.
- Dúvida sobre intenção é pergunta, não afirmação.

## Quando aprovar

Aprove quando não restar nenhum `[blocker]` aberto e a suíte de CI estiver verde.
`[sugestão]` e `[nit]` não bloqueiam merge; ficam a critério do autor.

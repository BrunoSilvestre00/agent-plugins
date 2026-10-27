---
name: commit-messages
description: Padrão do time para escrever mensagens de commit consistentes e rastreáveis (Conventional Commits + referência de task) — vale para qualquer stack.
metadata:
  version: "0.1.0"
---

# Mensagens de commit

Use esta skill ao escrever qualquer mensagem de commit em repositórios do
time, de qualquer stack.

## Formato

```
<tipo>(<escopo opcional>): <resumo no imperativo, minúsculo, ≤ 72 chars>

<corpo opcional: o PORQUÊ da mudança, não o como>
```

## Tipos aceitos

`feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`.

## Regras

- Resumo no imperativo: "adiciona validação", não "adicionada validação".
- Um commit = uma mudança lógica; não misture refactor com feature.
- Se o trabalho vem de uma task ou issue, referencie o identificador
  (ex.: `[T012]`) no início do resumo ou no corpo.
- O corpo explica motivação e contexto; o diff já mostra o "como".

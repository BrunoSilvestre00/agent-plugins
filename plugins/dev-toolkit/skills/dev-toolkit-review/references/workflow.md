# Revisão retroativa de arquitetura

PBI/épico alvo: **{ALVO}**

Roda a mesma revisão final que a Fase 9 do `work-task` já faz — mas fora
do ciclo ativo. Pensado pra PBIs/épicos que já estão em `status_testing`
ou já concluídos, quando ninguém rodou (ou é preciso rodar de novo) essa
verificação depois que o trabalho já saiu da sessão original de
`work-task` (ex.: achado durante uma auditoria, ou pra fechar uma dúvida
levantada depois do fato). Não substitui a Fase 9 — complementa pra
quando o trabalho já não está mais "ao vivo".

## Passos

1. Leia `## Dev Flow Config` do ARQUIVO_CONFIG. Sem ela, PARE e sugira
   `dev-toolkit-setup`.
2. Verifique que `{ALVO}` foi informado e que seu prefixo está em
   `jira_projects` deste repositório — mesma guarda do Fase 0 do
   `work-task` (passo 2 de lá), sem as guardas irrelevantes aqui (working
   tree limpo, `gh auth status` — este comando não implementa nada).
   Busque a issue no Jira via MCP — descrição completa e critérios de
   aceite, **qualquer status** (diferente do `work-task`, que só opera
   em PBI recém-assumido). **Não encontrou a issue**: PARE, informe que
   `{ALVO}` não foi encontrado em `jira_projects` e não prossiga — nunca
   chute uma issue parecida.
   - **`{ALVO}` é um PBI**: busque o épico pai e a decisão de arquitetura
     registrada (comentário `## Decisão de Arquitetura`), se houver.
   - **`{ALVO}` é um épico**: este comando reconstrói por PBI (a convenção
     de commit é por PBI, não por épico) — liste os PBIs filhos do
     épico e pergunte ao usuário qual(is) revisar; rode o passo 3 em
     diante para cada um escolhido, separadamente.
3. **Reconstrua o que foi implementado** — pode não haver branch viva:
   - Branch `feat/{PBI-ID}` ainda existe (local ou remota): use
     `git diff {base_branch}...feat/{PBI-ID}` normalmente, igual à
     Fase 9.
   - Sem branch viva: busque no histórico de `{base_branch}` (só o que
     já foi mesclado — nunca `--all`, que pegaria branch de worktree
     temporária abandonada, tipo `tmp/{PBI-ID}/T0NN`, que o `work-task`
     deveria ter apagado mas pode ter sobrado) os commits que
     referenciam o PBI na mensagem: `git log {base_branch} --grep="({PBI-ID}):"`.
     **A busca precisa ser ancorada** (o padrão exato `(<ID>):`, com o
     parêntese de fechamento colado no ID), nunca uma substring solta do
     ID. Um grep sem âncora por `{PBI-ID}` sozinho (ex.: `EI-146`)
     também acha `EI-1460`, `EI-14600` etc. — IDs que só por acaso
     compartilham o prefixo, contaminando a análise com commit de outro
     PBI completamente sem relação. Use o diff agregado desses commits
     como "o que foi implementado".
   - Nem branch nem commit referenciando o PBI: PARE e pergunte ao
     usuário onde está o código implementado (path/branch/commit
     específico) — nunca adivinhe ou pule a revisão silenciosamente.
4. Se `.dev-flow/{PBI-ID}/tasks.md` ainda existir localmente (mesmo
   repo ou worktree antigo), releia o preâmbulo "Dependências
   identificadas na Fase 3" — mesmo registro durável que a Fase 9 usa.
5. Invoque o agent `architect` em escopo **revisão final**, passando:
   **os critérios de aceite completos do PBI** (buscados no passo 2 —
   necessário pro check de omissão do `architect`, que cruza o que o
   PBI/sua métrica exige contra o diff, não só contra o que a Fase 3
   perguntou na época — essencial aqui, já que um PBI revisado
   retroativamente pode ter sido implementado antes de alguma dimensão
   do checklist existir), o diff (ou o diff agregado reconstruído), a
   checklist de dependências da Fase 3 (passo 4) sempre que existir, e
   a decisão de arquitetura, se houver.
6. Veredito:
   - **SEM DESVIO**: reporte ao usuário e pare — nada a refletir no
     board, nada a gravar como lição.
   - **DESVIO ENCONTRADO**: siga os passos 7-9.
7. **Reflita no board**: ofereça comentar na issue (`{PBI-ID}`, ou no
   épico original se `{ALVO}` era um épico e o desvio for de composição)
   descrevendo o achado — o que diverge,
   onde, por que importa — com o marcador `## Revisão Retroativa de
   Arquitetura` — **só com confirmação explícita do usuário**. Pergunte
   **separadamente** se ele também quer transicionar o status (ex.: de
   volta para `status_in_progress`, pra retrabalho) — NUNCA transicione
   por conta própria, e nunca invente nome de status fora do `## Dev
   Flow Config`. Comentar sem transicionar é uma resposta válida.
8. **Ofereça registrar uma lição pro compound**: o tipo de gap que uma
   revisão retroativa encontra costuma valer a pena compartilhar (ex.:
   "fluxo com métrica medida por período, mas sem gatilho decidido,
   passou despercebido na Fase 3") — mesmo mecanismo e schema do
   `dev-toolkit-compound`/`pbi-toolkit-compound` (`docs/knowledge/`,
   `tipo: armadilha`/`insight`, formato de `references/licoes.md` do
   `pbi-toolkit`). **Nunca grave sem confirmação explícita do usuário**,
   mesma disciplina do compound normal.
9. Reporte o resultado final: veredito, o que foi comentado (se
   confirmado), se o status mudou (se confirmado), se uma lição foi
   gravada (se confirmado).

## Regras

- NUNCA transicione o status da issue sem confirmação explícita — mesmo
  com um desvio claramente encontrado.
- NUNCA invente nome de status do Jira.
- NUNCA comente na issue/épico sem confirmação explícita.
- NUNCA grave lição no compound sem confirmação explícita.
- NUNCA adivinhe onde está o código implementado quando não há branch
  nem commit referenciando o PBI — pergunte.
- Esta revisão pode rodar quantas vezes o usuário quiser sobre o mesmo
  PBI/épico — não é um gate de uso único.

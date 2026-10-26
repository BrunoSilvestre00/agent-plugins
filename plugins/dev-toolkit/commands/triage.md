---
description: Varre PBIs/PRs em andamento e lista achados que precisam de atenção humana (CI quebrado, PBI parado, ADR pendente) — pensado pra rodar via /loop
argument-hint: "[projeto] (opcional, filtra por chave Jira)"
---

# Triagem do ciclo dev-toolkit

Entrada (pode estar vazia): $ARGUMENTS

Varre o estado atual dos PBIs em andamento e lista o que precisa de
atenção humana — **não corrige nada, só relata**. Pensado pra rodar
periodicamente via `/loop` (ex.: `/loop 30m /dev-toolkit:triage`), não
como parte do ciclo normal de `work-task`. É o "inbox" pra achados que
o ciclo automático não consegue resolver sozinho.

## Passos

1. Leia `## Dev Flow Config` do CLAUDE.md — mesma config de sempre. Sem
   ela, PARE e sugira `/dev-toolkit:setup` (igual ao `work-task`).
2. Busque no Jira (via MCP) as issues de `jira_projects` (filtradas por
   $ARGUMENTS se informado) que estão em `status_in_progress` ou
   `status_testing`.
3. Para cada uma, verifique:
   - **Em `status_in_progress` sem PR aberto e sem branch `feat/<ID>`**
     (local ou remota) há mais de um dia útil: flag "PBI assumido mas
     sem trabalho visível" — pode ter travado numa sessão que nunca
     terminou.
   - **Em `status_testing` com PR aberto**: rode `gh pr checks
     feat/<ID>` no repositório correspondente.
     - Check vermelho: flag "PR em Testing com CI não-verde" — não
       deveria ter chegado aqui se a Fase 11 do `work-task` rodou; cobre
       o caso de alguém ter dado push depois, ou a branch base ter
       quebrado algo desde então.
     - Sem nenhuma review/aprovação há muitos dias: flag "aguardando
       review" — isso é sinal de gargalo humano, não de erro do ciclo;
       reporte com severidade menor que CI vermelho.
4. Busque, nos épicos com PBIs ativos, comentários `## Decisão de
   Arquitetura` marcados como "proposto (aguardando confirmação
   humana)" que nunca viraram uma decisão confirmada: flag "ADR
   pendente de decisão".
5. Para cada PBI ativo, se existir `.dev-flow/{PBI-ID}/tasks.md` na
   branch: confira se há alguma task marcada bloqueada — flag "task
   bloqueada esperando decisão" com o motivo já registrado ali.
6. **PBIs paralelos esperando resposta**: rode `git worktree list` neste
   repositório e, pra cada worktree (inclusive o diretório atual),
   confira se existe `.dev-flow/*/aguardando.md` — é o marcador que o
   `work-task` grava sempre que PARA esperando o usuário (qualquer
   fase). Achou algum: flag "PBI parado esperando você" com o
   PBI-ID, o caminho da worktree, e o conteúdo do arquivo (fase +
   pergunta pendente, já resumidos ali). Isso é o que dá visão de qual
   worktree, entre várias rodando em paralelo, precisa de atenção agora
   — sem esse marcador o dev teria que checar terminal por terminal.
   **Limitação conhecida**: `git worktree list` só enxerga worktrees
   deste repositório — um stack polyrepo (`repo`/`local_path`, clone
   separado, não worktree) não aparece aqui. Se souber que um PBI tem
   stack remoto, mencione isso no relatório como "não verificado" em vez
   de simplesmente omitir.
7. Apresente tudo como uma lista organizada por severidade (CI
   vermelho > ADR pendente > PBI parado esperando você > task
   bloqueada > PBI parado sem PR > aguardando review), com link de cada
   PBI/PR/comentário, ou caminho da worktree pro achado do passo 6.
   **Sem nenhum achado, diga isso claramente** — não invente urgência
   onde não há.

## Regras

- NUNCA transicione card, comente em issue, ou feche/edite PR — é
  somente leitura, igual ao `/dev-toolkit:tasks`.
- NUNCA invente um limite de tempo preciso — "um dia útil"/"muitos
  dias" acima são heurísticas de bom senso, não um SLA formal; se o
  time quiser afinar isso, é uma conversa de configuração futura, não
  algo pra decidir sozinho aqui.
- NUNCA rode `work-task` a partir daqui — a triagem só relata; retomar
  um PBI travado é decisão e ação do dev, não deste comando.

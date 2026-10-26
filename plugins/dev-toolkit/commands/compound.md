---
description: Extrai lições aprendidas do ciclo de desenvolvimento (bloqueios recorrentes, retrabalho) e grava em docs/knowledge/
argument-hint: "[PBI ou contexto do que foi aprendido — opcional]"
---

# Compound — lições aprendidas do ciclo de dev

Entrada (pode estar vazia): $ARGUMENTS

Extraia até 1–3 lições do que aconteceu nos ciclos recentes de
`work-task` e grave em `docs/knowledge/` — a mesma pasta que o
`pbi-toolkit` usa (se instalado) para as lições do lado do PO. **Uma
base de conhecimento só**, não duas, pro próximo ciclo consultar antes
de reaprender do zero o que já se sabia.

## Fontes a considerar

- A conversa atual (o que travou, o que precisou de retrabalho).
- `.dev-flow/*/tasks.md` de PBIs recentes — tasks marcadas bloqueadas,
  quantas rodadas implementer↔verifier precisou até aprovar.
- Comentários `## Decisão de Arquitetura` recentes nos épicos — decisão
  que se repetiu, ou que poderia ter sido antecipada.
- PBIs que voltaram de Testing pra in-progress (retrabalho) — via Jira,
  se as tools da Atlassian estiverem disponíveis.

## O que vale a pena virar lição

- Um tipo de critério de aceite que costuma sair ambíguo.
- Um padrão de bloqueio recorrente do `verifier` (mesmo tipo de
  REPROVADO em PBIs diferentes).
- Uma decisão de arquitetura que se repetiu sem estar registrada como
  convenção nova numa skill do `dev-patterns`.
- Um caso de CI vermelho (Fase 11 do `work-task`) por motivo recorrente
  e evitável.

## Passos

1. Se `docs/knowledge/` não existir, crie a pasta (com `.gitkeep`) —
   não assuma que o `pbi-toolkit` já rodou `/pbi-toolkit:setup`.
2. Releia as lições já existentes ali (grep por tags/termos relevantes)
   — **nunca registre uma lição que contradiga ou duplique** uma já
   gravada. Se a nova contradiz uma antiga, confirme com o usuário qual
   vale, marque `substitui:` na nova e mova a antiga para
   `docs/knowledge/arquivadas/`.
3. Extraia no máximo 1–3 lições desta execução — **mesmo formato do
   `pbi-toolkit`, é a mesma pasta e a mesma base de conhecimento**, não
   um schema próprio do lado do dev:

   ```markdown
   ---
   tipo: insight | armadilha | convencao | estimativa
   tags: [ex: pagamentos, integracao-x, ci]
   confianca: alta | media | baixa
   criado: AAAA-MM-DD
   fonte: <PBI de origem, ex.: PROJ-142>
   substitui: <slug de lição anterior, se esta a contradiz — opcional>
   ---

   # <Título afirmativo em 1 linha>

   <2-6 frases: o que aprendemos, em que contexto vale, e o que fazer
   diferente da próxima vez. Concreto e acionável.>
   ```

   Arquivo em `docs/knowledge/<slug-da-licao>.md`. `confianca: alta` só
   com evidência repetida (aconteceu 2+ vezes) — um caso isolado é
   `media`/`baixa`. Lição que não completa "da próxima vez, faça/considere
   X" não é lição, é desabafo — não grave.
4. Valide cada lição com o usuário antes de gravar — nunca grave sem
   confirmação explícita.
5. Se uma lição sugerir que falta uma skill/convenção no `dev-patterns`
   (ex.: um padrão que já se repetiu 3 vezes sem estar documentado em
   nenhuma skill), avise o usuário — **não crie a skill sozinho**, isso
   é decisão do time, não deste comando.
6. Reporte o que foi gravado. **Não commite sem o usuário pedir.**

## Regras

- NÃO grave lição sem confirmação explícita do usuário.
- NÃO duplique lição já registrada — releia antes de escrever.
- NÃO crie skill nova sozinho a partir de uma lição — só sinalize.
- NÃO commite sem o usuário pedir.

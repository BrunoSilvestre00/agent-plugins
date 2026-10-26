---
description: Refinamento técnico do backlog em status_ready, antes de um dev puxar o PBI — clareza do PBI, histórico do time, avaliação de arquitetura, diagrama (se disponível), e aponta pro Spec Kit se o repo usar
argument-hint: "[PBI-ID opcional — sem argumento, roda sobre todo o backlog em status_ready]"
---

# Refinamento técnico antes do pickup

Entrada (pode estar vazia): $ARGUMENTS

O `pbi-toolkit` já cobre o refinamento de produto (DoR, `[NEEDS
CLARIFICATION]` antes de liberar pra `status_ready`). Este comando cobre a
camada técnica que só faz sentido com olhar de quem vai implementar:
dependência de arquitetura, histórico de armadilhas do time, e ambiguidade
que só aparece lendo como dev. Roda ANTES de qualquer pessoa assumir o
PBI — achado aqui vira pauta de reunião de refinamento, não um bloqueio de
quem já começou a trabalhar (isso é papel do `work-task`).

**Mais caro que `/dev-toolkit:triage`** — chama o agent `architect`
(custo/tempo de um modelo grande) por PBI avaliado. Pensado pra rodar sob
demanda antes de planning/refinamento, não num intervalo curto de `/loop`.

## Passos

1. Leia `## Dev Flow Config` do CLAUDE.md. Sem ela, PARE e sugira
   `/dev-toolkit:setup`.
2. Determine o alvo:
   - `$ARGUMENTS` com um ID: verifique que o prefixo (a chave antes do
     hífen) está em `jira_projects` deste repositório — mesma guarda do
     Fase 0 do `work-task`. Se não estiver, PARE: informe os projetos
     configurados aqui e não prossiga, o PBI provavelmente pertence a
     outro repositório. Passando na guarda, refine só aquele PBI, mesmo
     que não esteja em `status_ready` — o time pode querer refinar algo
     cedo, antes de ir pro board de pronto.
   - Vazio: todos os PBIs em `status_ready` de `jira_projects` (via MCP do
     Jira).
3. Para cada PBI alvo, rode as cinco camadas abaixo até o fim e monte um
   relatório consolidado — achado numa camada não impede olhar as
   outras, nunca pare no meio.

### Camada 1 — Clareza do PBI

- Busque o corpo completo da issue no Jira. Procure `[NEEDS
  CLARIFICATION: ...]` explícito (convenção que o `pbi-toolkit` e o Spec
  Kit compartilham) — se houver, já é achado pronto, sem reinterpretar.
- Mesmo sem esse marcador, releia como a Fase 1 do `work-task` releria:
  critério de aceite ausente, contraditório, ou tecnicamente inviável
  também é achado aqui — só que vira pergunta de refinamento, não um PARE
  que trava alguém no meio do trabalho.

### Camada 2 — Histórico do time

- Se `docs/knowledge/` existir: releia as lições lá (`tipo: armadilha` ou
  `insight`, `tags`) e cruze com o tema deste PBI. Cada lição relevante
  vira uma pergunta objetiva e específica — não cite a lição
  genericamente, aponte o que ela pede pra confirmar NESTE PBI (ex.: "a
  lição sobre o provedor X diz que a credencial de sandbox costuma
  faltar — já temos ela pra este PBI?").
- Sem `docs/knowledge/`, pule esta camada silenciosamente — nada pra
  cruzar ainda, e não é este comando que cria a pasta (isso é o
  `/dev-toolkit:compound` ou o `pbi-toolkit`).

### Camada 3 — Avaliação de arquitetura

- Se o PBI não tiver épico pai, pule esta camada inteira — sem épico não
  há composição possível, mesma regra da Fase 3 do `work-task`.
- Mesma lógica da Fase 3 do `work-task`: busque o épico pai deste PBI; se
  já houver um comentário `## Decisão de Arquitetura` que plausivelmente
  cubra o PBI, não invoque o agent — só reporte que já está resolvido.
- Senão, invoque o agent `architect` em escopo **pré-decomposição**,
  passando os critérios de aceite deste PBI e, do mesmo épico, título +
  critérios dos PBIs irmãos (leitura rasa, igual ao `work-task`).
- Reporte o veredito **e** a checklist de dependências **exatamente como
  o agent devolveu**, sempre que ela existir — não resuma, é insumo
  direto pra reunião de refinamento. Isso vale mesmo quando o veredito é
  SEM IMPACTO: um item "RESOLVIDA (vira task)" não vem com rascunho de
  ADR nenhum (o `architect` só produz ADR pra impacto genuíno ou
  dependência em aberto), mas ainda assim precisa aparecer no relatório
  — é como o time fica sabendo que aquele PBI vai precisar de uma task de
  infra, mesmo sem nenhuma decisão de arquitetura pra confirmar. Só
  inclua o rascunho de ADR completo quando ele de fato existir (impacto
  ou dependência em aberto).
- **Se o `architect` sinalizar que parte do escopo merece PBI próprio**
  (campo "Consequências" do ADR): destaque isso separadamente no
  relatório — é justamente numa reunião de refinamento que faz mais
  sentido decidir isso, antes de qualquer dev puxar o PBI. Se o time
  concordar ali mesmo, sugira `/pbi-toolkit:quebrar-epico <épico>` (modo
  incremental) — mas não invoque por conta própria, é decisão do PO.
- **Se o time confirmar a decisão ali mesmo, nesta sessão**: siga o
  processo COMPLETO da Fase 3 do `work-task`, os mesmos passos, não só o
  comentário:
  1. **Antes de postar, releia os comentários do épico MAIS UMA VEZ** —
     nunca confie só na leitura de alguns parágrafos acima. Se este
     `refine` está avaliando o backlog inteiro em lote, é fácil um outro
     PBI do mesmo épico (avaliado antes nesta mesma sessão, ou por uma
     sessão de `work-task`/`refine` em paralelo) já ter postado uma
     decisão nesse intervalo. Achou um `## Decisão de Arquitetura` novo
     que não estava lá quando a Camada 3 começou: PARE, não poste a
     sua — apresente o conflito ao usuário e peça pra reconciliar antes
     de seguir (mesma disciplina da Fase 3 do `work-task`).
  2. Comente no ÉPICO com o marcador `## Decisão de Arquitetura` já como
     definitiva (nunca copie o conteúdo inteiro num arquivo de
     repositório, mesma regra de sempre).
  3. Para cada repositório listado em "Repositórios afetados" que já usar
     a convenção `docs/adr/` (verifique se a pasta existe naquele repo):
     crie lá o mesmo arquivo stub que a Fase 3 do `work-task` criaria,
     linkando o comentário no épico. Se este repositório for um dos
     afetados, o stub entra num commit direto aqui (fora de qualquer
     branch de PBI, já que ainda não existe uma); se for outro
     repositório, apenas avise que o stub fica pendente para quando
     alguém rodar o ciclo lá.
  Isso faz o `work-task` de quem pegar este PBI depois reconhecer que já
  foi decidido e pular a Fase 3 sozinho — sem retrabalho, sem duplicar
  decisão, e sem stub faltando. Sem confirmação agora, deixe como
  rascunho e não comente nem crie arquivo nenhum.

### Camada 4 — Spec Kit (só se detectado)

- Verifique se `.specify/` existe neste repositório. Se não, pule esta
  camada — nunca sugira instalar Spec Kit por conta própria, isso é
  decisão do time.
- Se existir: procure um spec/feature relacionado a este PBI (ex.:
  `specs/*/spec.md` cujo conteúdo referencie o ID ou o título do PBI). Se
  achar um com `[NEEDS CLARIFICATION]` ainda no arquivo, ou se não achar
  spec nenhum ainda pra este PBI: recomende ao usuário rodar
  `/speckit.specify` e/ou `/speckit.clarify`. **Nunca tente conduzir isso
  por conta própria** — `/speckit.clarify` é interativo por natureza
  (pergunta uma de cada vez, espera resposta, grava no spec), não algo
  que este comando possa disparar e resumir sozinho.

### Camada 5 — Diagrama de arquitetura (se aplicável)

- Só roda se a Camada 3 tiver produzido um rascunho de ADR (impacto
  genuíno ou dependência em aberto) — sem decisão de arquitetura
  proposta, não há o que desenhar aqui.
- Ofereça rodar `/dev-toolkit:diagram <épico>` pra visualizar a
  arquitetura proposta — dá algo concreto pra reunião de refinamento, não
  só prosa. Esse comando isolado já trata disponibilidade da skill,
  instalação opcional, modo (IaC real vs. brainstorm) e fallback Mermaid
  — não duplique nada disso aqui, só ofereça a chamada.

## Relatório final

Por PBI, nesta ordem: link do PBI, achados da Camada 1, achados da
Camada 2, veredito + achados da Camada 3, recomendação da Camada 4 (se
aplicável), link/arquivo do diagrama da Camada 5 (se gerado). Feche com
duas listas separadas, nunca misturadas:

- **Perguntas em aberto pra reunião de refinamento** — o que exige
  decisão humana: dependência EM ABERTO, decisão de arquitetura
  proposta, ambiguidade da Camada 1, recomendação da Camada 4. Isso é o
  que o time leva pra discutir.
- **Infra a criar, já resolvida** — item "RESOLVIDA (vira task)" da
  Camada 3: não é pergunta, é aviso de que aquele PBI vai gerar uma task
  de infra quando alguém rodar `work-task`. Não precisa de decisão de
  ninguém, só ciência.

Ofereça comentar essa lista consolidada na(s) issue(s) correspondente(s)
do Jira, com o marcador `## Refinamento Técnico Pendente` — **só com
confirmação explícita do usuário**, nunca automaticamente.

## Regras

- NUNCA transicione o status de nenhum PBI — refinar não é assumir; quem
  assume é o `work-task`.
- NUNCA rode `work-task` a partir daqui.
- NUNCA finalize uma decisão de arquitetura sem confirmação explícita do
  usuário — mesma disciplina do `architect`/Fase 3 do `work-task`.
- NUNCA comente no Jira sem confirmação explícita do usuário.
- NUNCA tente conduzir `/speckit.clarify` por conta própria — é
  interativo, só aponte que existe e por quê.
- NUNCA instale plugin/marketplace nenhum por conta própria (Camada 5
  inclusive) — só mencione a opção, o usuário decide e instala.
- Achado numa camada nunca impede reportar as outras — sempre rode as 5
  camadas até o fim antes de reportar.

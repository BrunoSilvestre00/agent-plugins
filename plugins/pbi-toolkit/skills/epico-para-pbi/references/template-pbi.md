# Template — PBI (corpo do artefato .md e da issue no Jira)

> Título: `[Área] Verbo no infinitivo + objeto` (máx. 80 caracteres)
> No Jira: **História** vinculada ao épico pai. No repo: `docs/pbis/<epico>/NN-<slug>.md`.
> A descrição da issue no Jira = este corpo COMPLETO (o Jira é a fonte da verdade para o dev), iniciando por:
> `📄 Fonte versionada: https://github.com/<org>/<repo>/blob/<branch>/docs/pbis/<epico>/NN-<slug>.md (esta descrição é a cópia integral; divergiu, o PO atualiza os dois).`
> Sempre com o repositório identificado (link completo, ou `<org>/<repo> → caminho` na ausência de remote) — as fontes do time vivem em repositórios diferentes.

## 🎯 Contexto e valor
2–4 frases: dor/oportunidade, ligação com o objetivo do épico (traga o contexto para cá — o dev não deve precisar abrir o épico), o que acontece se não fizermos.

## 👤 História
> **Como** <persona>, **quero** <capacidade>, **para** <benefício mensurável>.

## ✅ Critérios de aceite (Gherkin)
Um cenário por comportamento. Mínimo: 1 caminho feliz + 1 caso de erro. Estes cenários são o contrato — o Spec Kit deriva a spec deles.

```gherkin
Cenário: <caminho feliz>
  Dado <estado inicial>
  Quando <ação>
  Então <resultado observável>

Cenário: <erro/limite>
  Dado <estado inicial>
  Quando <ação inválida ou condição de borda>
  Então <comportamento esperado>
```

## 📏 Regras de negócio
RN01, RN02... — o que os cenários não expressam sozinhos: limites, permissões, prazos, arredondamentos.

Se este PBI captura/persiste uma entidade (ex.: o PBI de caminho mínimo/walking skeleton que dá origem a ela, princípio 3 de `regras-fatiamento.md`), liste o contrato de campos **completo e exaustivo**, nunca só exemplos ilustrativos: cada campo que a entidade tem, e se é obrigatório (a entidade é rejeitada/sinalizada sem ele) ou opcional (a entidade é aceita, o campo fica ausente/nulo). "Dados obrigatórios (título, empresa, X)" é insuficiente — falta decidir e escrever, campo a campo, quais dos demais atributos conhecidos da entidade entram como obrigatórios e quais como opcionais; campo omitido da lista é ambiguidade que o dev resolve sozinho, silenciosamente.

## 🚫 Fora de escopo
O que alguém poderia achar que está incluso, mas NÃO está (e em qual PBI/épico vive, se souber).

## ⛓️ Restrições
Somente imposições REAIS (compliance/LGPD, integração obrigatória com sistema X, SLA, prazo regulatório). **Não** preencher com preferências de implementação — stack e arquitetura são decisão do `/speckit.plan`.

## 🔗 Dependências
Outros PBIs deste épico (por arquivo `NN-...`), times externos, APIs de terceiros, feature flags.

## 📐 Design / UX
Link do Figma ou "não se aplica". Com UI: estados vazio, carregando, erro e sucesso.

## 📊 Medição
Evento/métrica que comprova o valor em produção.

---
Decisões de produto em aberto devem aparecer no ponto exato do texto como `[NEEDS CLARIFICATION: <pergunta objetiva>]` — nunca omitidas.

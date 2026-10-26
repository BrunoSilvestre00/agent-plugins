# Handoff — do PBI para o desenvolvimento

O PBI vive em dois lugares sincronizados: o artefato `docs/pbis/<epico>/NN-<pbi>.md` (fonte versionada, dona: PO) e a issue no Jira (cópia integral do corpo — **fonte da verdade para o time de dev**, que não lê spec de arquivos do repo). Por isso o corpo do PBI precisa ser autossuficiente: tudo que o dev precisa está na descrição da issue.

Consumidores no lado do dev (o PBI não assume nenhum — por isso precisa ser autossuficiente no Jira):
- **Dev direto**: lê o card e implementa; os cenários Gherkin são o contrato de aceite.
- **dev-toolkit** (se instalado no repo): `/dev-toolkit:work-task <ID>` lê o PBI do Jira e decompõe em tasks; o gate de compreensão dele PARA em critérios ambíguos — mais um motivo para pendências serem `[NEEDS CLARIFICATION]` explícito e PBI pendente não ir para o status de pronto.
- **Spec Kit** (se o time optar): `/speckit.specify Implemente o PBI descrito em docs/pbis/<epico>/NN-<pbi>.md`, depois `/speckit.clarify`, `/speckit.plan`, `/speckit.tasks`.

Regra de ouro: nada neste plugin pode depender de qual consumidor existe do outro lado.

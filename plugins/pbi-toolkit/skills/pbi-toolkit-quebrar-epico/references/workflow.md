Use a skill [epico-para-pbi](../../epico-para-pbi/SKILL.md) deste plugin
para conduzir o refinamento completo.

Entrada fornecida pelo PO: ENTRADA

Se a entrada for uma chave de issue do Jira (ex.: PROJ-123), busque o épico no Jira via MCP da Atlassian antes de começar. Se for um caminho de arquivo, leia o arquivo. Se estiver vazia, pergunte qual épico será refinado.

Siga o fluxo da skill do início ao fim: entrevista (ou, se `docs/pbis/<epico>/` já existir, modo incremental — sem repetir a entrevista) → proposta de fatiamento → aprovação → artefatos .md no repositório → criação das issues no Jira (com confirmação antes de criar).

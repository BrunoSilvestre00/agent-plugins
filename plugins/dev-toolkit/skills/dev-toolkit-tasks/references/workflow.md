# Listar PBIs disponíveis

Contexto adicional do usuário (pode estar vazio): ENTRADA

## Instruções

1. Leia a seção `## Dev Flow Config` do ARQUIVO_CONFIG deste repositório para obter:
   - `jira_projects`: lista de chaves de projeto no Jira (ex: PLAT, MOB, PAY).
     Retrocompatibilidade: se existir apenas `jira_project` (singular),
     trate como lista de um único projeto.
   - `status_ready`: o nome do status que indica "pronto para dev"

   Se o ARQUIVO_CONFIG não tiver essa seção, PARE e informe o usuário que o
   repositório ainda não foi configurado (aponte para o exemplo no README
   do plugin). Não tente adivinhar chaves de projeto.

2. Interprete ENTRADA:
   - Se contiver uma chave que esteja em `jira_projects` (ex: `PAY`),
     limite a busca a esse projeto.
   - Se contiver uma chave que NÃO esteja em `jira_projects`, PARE e
     informe quais projetos estão configurados neste repositório.
   - Qualquer outro texto é filtro adicional (ex: prioridade, label).

3. Busque no Jira, via MCP da Atlassian, as issues com JQL:
   `project IN ({projetos selecionados}) AND status = "{status_ready}" AND assignee IS EMPTY ORDER BY priority DESC, created ASC`
   incorporando filtros adicionais de ENTRADA, se houver.

4. Apresente o resultado como uma tabela enxuta:
   | ID | Título | Projeto | Prioridade | Estimativa |
   Ordenada por prioridade. Máximo de 15 issues. Omita a coluna Projeto
   se houver apenas um projeto configurado.

5. Termine com: "Para iniciar um PBI: `dev-toolkit-work-task <ID>`.
   Para trabalhar em paralelo, use `dev-toolkit-worktree <ID>` primeiro."

## Regras

- NÃO transicione nenhum card neste comando. Ele é somente leitura.
- NÃO se atribua a nenhuma issue neste comando.

Provisione este repositório para a esteira de refinamento e desenvolvimento do time.

Entrada (pode estar vazia): ENTRADA

## Passos

1. **ARQUIVO_CONFIG**: verifique se existe na raiz.
   - Não existe → crie um mínimo: título com o nome do repo, 1 parágrafo de descrição (inferida do código/README) e a seção abaixo. Sugira complementar depois as instruções do projeto no agente utilizado.
   - Existe sem `## Dev Flow Config` → apenas ADICIONE a seção ao final, sem tocar no resto.
   - Existe com a seção → informe que já está configurado, mostre os valores atuais e pare (a menos que o usuário peça para alterar).

2. **Preencher a seção**: use ENTRADA como `jira_projects` se informado; senão pergunte (uma pergunta por vez, com sugestão). Se as tools da Atlassian estiverem disponíveis, consulte os status reais do workflow do projeto e sugira nomes exatos — nunca invente nomes de status. Config mínima deste plugin (seção `## PBI Config`, ou `## Dev Flow Config` se já existir/o usuário preferir a convenção compartilhada):

   ```markdown
   ## PBI Config

   - jira_projects: <KEYS>
   - status_ready: <status exato do workflow, opcional>
   - issue_type_pbi: História
   - issue_type_epico: Épico
   ```

   Depois pergunte: "Este repositório também vai usar o plugin dev-toolkit?" Se sim, grave a seção como `## Dev Flow Config` e acrescente as chaves dele (`status_in_progress`, `status_testing`, `base_branch`, `test_command`, `lint_command` — detectando test/lint/branch pelo repo). Se não, pare na config mínima — não polua o ARQUIVO_CONFIG com chaves de um plugin que não está em uso.

3. **Estrutura de pastas**: crie (com `.gitkeep`) o que faltar: `docs/prd/`, `docs/pbis/`, `docs/knowledge/`.

4. **Verificação**: confira se existe `.pbi-toolkit.json` legado — se existir, migre os valores para a seção e sugira remover o arquivo.

5. Reporte o que foi criado/alterado e sugira commitar. **Não commite sem o usuário pedir.**

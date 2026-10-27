---
name: epico-para-pbi
description: >-
  Transforma um épico em PBIs padronizados, gravando um artefato .md por PBI no
  repositório do projeto (insumo direto do /speckit.specify) e criando as
  issues correspondentes no Jira via MCP da Atlassian. Use sempre que o usuário
  mencionar refinar ou quebrar um épico, criar PBIs ou histórias a partir de
  uma iniciativa, preparar backlog para o time de desenvolvimento, ou rodar o
  comando pbi-toolkit-quebrar-epico — mesmo que ele cole apenas um texto solto
  descrevendo a iniciativa (por exemplo "quebra esse épico", "gera os PBIs
  disso", "cria os cards no Jira").
---

Leia primeiro [as regras de execução](../../references/runtime.md).

# Épico → PBIs: artefatos no repo + issues no Jira

Fluxo agentic executado pelo PO **dentro do repositório do projeto**. Nada de copy-paste: a skill produz, por PBI:

1. **Artefato `.md` no repositório** — em `docs/pbis/<slug-do-epico>/NN-<slug-do-pbi>.md`. É a fonte de verdade e o insumo do `/speckit.specify`.
2. **Issue no Jira** — História vinculada ao épico, com a descrição do PBI e o caminho do artefato no repo.

Esta skill **não gera tasks** — o dev deriva tasks no próprio repo com `/speckit.specify` → `/speckit.plan` → `/speckit.tasks`.

## Pré-checagens (faça antes de tudo)

1. **Configuração do repositório**: leia a config de destino no `ARQUIVO_CONFIG` da raiz. Este plugin procura, nesta ordem, uma seção `## PBI Config` ou `## Dev Flow Config` (esta última é a convenção compartilhada quando o repo também usa o plugin `dev-toolkit` — leia dela apenas as chaves abaixo e ignore as demais). Chaves usadas:
   - `jira_projects` (ou `jira_project`): chave(s) do projeto Jira. Uma → use direto; várias → pergunte em qual projeto este épico vive (e valide chaves citadas na conversa contra a lista).
   - `status_ready` (opcional): status do workflow que marca "pronto para desenvolvimento" (usado no passo 6.6).
   - `issue_type_pbi` / `issue_type_epico` (opcionais; padrão: História / Épico).
   Com config presente, não pergunte projeto/tipo — informe no resumo de confirmação e siga. O que o usuário disser na conversa sempre prevalece. Sem config: aceite `.pbi-toolkit.json` legado se existir; senão pergunte no passo 6 e ofereça gravar a config no ARQUIVO_CONFIG (na seção `## Dev Flow Config` se ela já existir; senão em `## PBI Config`).
2. **Tools da Atlassian disponíveis?** Verifique se há tools do MCP oficial da Atlassian incluído no plugin ou conectado à sessão. Se não houver, avise o usuário no início que vai gerar os artefatos locais, mas a criação de issues requer conectar e autenticar o MCP oficial da Atlassian no agente atual e siga o fluxo até o passo 5. **Use somente as tools oficiais da Atlassian para falar com o Jira** — nunca skills ou CLIs de terceiros, mesmo que estejam instaladas no ambiente.
3. **Contexto do projeto**: confira se existe `.specify/` ou `specs/` (Spec Kit inicializado) e `docs/pbis/`. Se `docs/pbis/` não existir, crie na hora de gravar.
4. **Épico**: se o usuário passou uma chave (ex.: PROJ-123), busque a issue no Jira e use descrição + comentários como material de partida.
5. **Modo incremental**: verifique se `docs/pbis/<slug-do-epico>/README.md` já existe. Se sim, este épico já foi decomposto antes — o passo 1 abaixo entra em **modo incremental** (adicionar um PBI a um épico existente), não repete a entrevista completa do zero. Se não existir, siga o fluxo completo normalmente.

## Fluxo (sempre nesta ordem)

### 1. Entender o épico

**Modo incremental** (`docs/pbis/<slug-do-epico>/README.md` já existe — épico já decomposto antes):
- Leia esse `README.md` (resumo do entendimento original, lições já consideradas) e a lista de PBIs existentes (`NN-*.md`, títulos e dependências) — **não repita a entrevista do `checklist-epico.md` do zero**, ele já foi respondido; releia só se o motivo do PBI novo tocar um item que mudou (ex.: uma restrição nova, uma dependência externa que não existia).
- Pergunte o que é específico deste PBI novo: o que motivou a adição — nova necessidade de negócio, algo que o corte original não previu, uma descoberta do lado do dev (ex.: o `architect` do `dev-toolkit`, numa avaliação de arquitetura ou revisão final, sinalizou que o escopo era maior que uma task e sugeriu um PBI novo), ou uma descoberta do próprio PO numa revisão manual (ex.: um PBI já avançado tinha uma decisão de negócio incompleta ou ilustrativa em vez de exaustiva — como um contrato de campos citado só por exemplo, ver `template-pbi.md`/`dor.md`)? Essa origem importa — vira o "motivo" registrado no README e é insumo pra seção de compound mais abaixo.
- **Releia o limite de `regras-fatiamento.md`**: conte quantos `NN-*.md` já existem nessa pasta (contando este PBI novo) e compare com 6–8 PBIs por épico — não estime de olho. Se o total já bate ou passa do teto, avise o usuário que isso é sinal de que a iniciativa cresceu além do épico original — sugira abrir um épico novo em vez de continuar empilhando PBI aqui, e pergunte como prosseguir. Não decida sozinho, só avise.
- Consulte `docs/knowledge/` do mesmo jeito que o fluxo completo faria (próximo bullet) — a origem incremental não isenta dessa consulta.

**Fluxo completo** (primeira decomposição deste épico):
**Primeiro, consulte as lições do time**: se existir `docs/knowledge/`, busque lições relevantes ao épico (grep por termos/tags) e use-as conforme `references/licoes.md` — lição encontrada vira resposta-padrão a confirmar, não pergunta do zero.

Depois leia `references/checklist-epico.md`. Extraia o que já está respondido no material disponível (issue do Jira, documento, código do repo); entreviste só as lacunas:
- **Uma pergunta por vez**, nunca uma lista.
- **Sempre com resposta recomendada** ("Minha sugestão: X, porque Y. Confirma?").
- Se a resposta estiver no código/documentos do repo, procure lá primeiro e só confirme.
- Normalmente 4–9 perguntas. Pare quando o checklist estiver coberto.

### 2. Propor o fatiamento (ou o encaixe, no modo incremental)

**Modo incremental**: apresente só o PBI novo (título + 1 frase de valor + dependências com os PBIs já existentes, citados pelo arquivo `NN-...`) e onde ele entra na ordem — o próximo `NN` livre, a menos que o usuário indique que ele precisa vir antes de algum PBI ainda não iniciado. **Aguarde aprovação/ajuste antes de detalhar**, mesma disciplina do fluxo completo.

**Fluxo completo**: apresente a lista proposta de PBIs (título + 1 frase de valor + dependências) e o racional, conforme `references/regras-fatiamento.md`. **Aguarde aprovação/ajuste do usuário antes de detalhar.**

### 3. Escrever cada PBI
Preencha `references/template-pbi.md` por completo para cada PBI aprovado:
- Título: `[Área] Verbo no infinitivo + objeto` (máx. 80 caracteres).
- Gherkin: mínimo 1 caminho feliz + 1 caso de erro.
- Só "o quê" e "por quê" — decisões de implementação ficam para o `/speckit.plan`. Restrições reais (compliance, legado obrigatório, SLA) entram na seção Restrições.
- Lacunas viram `[NEEDS CLARIFICATION: <pergunta>]` no corpo — nunca invente.

### 4. Validar contra a Definition of Ready
Rode `references/dor.md` em cada PBI e reporte falhas. O usuário decide se segue com pendências.

### 5. Gravar os artefatos no repositório
Para cada PBI, grave o arquivo em:

```
docs/pbis/<slug-do-epico>/NN-<slug-do-pbi>.md
```

- `NN` = ordem sugerida de execução (01, 02...). **Modo incremental**: `NN` continua do maior já existente (+1) — nunca reinicie em 01.
- **Fluxo completo**: crie `docs/pbis/<slug-do-epico>/README.md` com: link/chave do épico, resumo do entendimento (passo 1), lista dos PBIs com dependências e racional do corte.
- **Modo incremental**: **leia o `README.md` inteiro antes de editar** e faça uma edição pontual nele — nunca regenere o arquivo do zero, mesmo que pareça mais organizado reescrever. Acrescente o PBI novo à lista de PBIs existente (com dependências) e acrescente/atualize a seção `## Adições pós-fatiamento inicial` (data + PBI + motivo em 1 frase, incluindo se veio de descoberta do dev). Todo o resto do arquivo — resumo do entendimento original, lições já citadas, racional do corte original — permanece byte a byte como estava; regenerar o arquivo destruiria esse contexto acumulado.
- Siga o formato de arquivo definido em `references/handoff-speckit.md` (frontmatter YAML + corpo).
- Sugira ao usuário commitar (`git add docs/pbis && git commit`), mas **não commite sem ele pedir**.

### 6. Criar as issues no Jira
Com as tools oficiais da Atlassian:
1. Determine o destino pela config da pré-checagem 1 (ou confirme com o usuário, na ausência dela). Confirme o épico pai (key); se o épico ainda não existe no Jira, ofereça criá-lo primeiro.
2. Mostre o resumo do que será criado (títulos + épico pai + projeto) e **peça confirmação explícita antes de criar qualquer issue**.
3. Crie cada PBI como issue vinculada ao épico, **sem assignee** (a atribuição é decisão do time no momento de puxar o trabalho; muitos fluxos — automatizados ou não — selecionam apenas cards sem dono). Descrição da issue = corpo COMPLETO do PBI (sem o frontmatter). O Jira é a fonte da verdade para o time de dev: nada essencial pode existir só no arquivo. Primeira linha da descrição — identifique o repositório, pois as fontes podem estar espalhadas em vários repos:
   - Descubra o remote (`git remote get-url origin`) e a branch default, e monte o link completo para o arquivo:
     `📄 Fonte versionada: https://github.com/<org>/<repo>/blob/<branch>/docs/pbis/<slug-do-epico>/NN-<slug>.md (esta descrição é a cópia integral; divergiu, o PO atualiza os dois).`
   - Sem remote configurado, use `<org>/<repo> → docs/pbis/...` com o nome que o usuário confirmar — nunca deixe o caminho sem o repositório.
   - O link aponta para a branch default; lembre o usuário de que ele só funciona após o commit/push dos artefatos.
4. Se houver dependências entre PBIs, crie os links de issue (blocks/is blocked by) quando as tools suportarem.
5. Atualize o frontmatter de cada artefato com a chave criada (`jira: PROJ-456`) e reporte a lista: chave → título → arquivo.
6. **Liberação para desenvolvimento**: se houver `status_ready` configurado, para cada PBI que passou na DoR **sem pendências** (nenhum `[NEEDS CLARIFICATION]`), ofereça transicionar o card para esse status — é o sinal, no workflow do time, de que o PBI está pronto para ser puxado (por um dev ou por qualquer automação que o time use). PBIs com pendências permanecem fora desse status até o PO resolvê-las; nunca transicione um PBI pendente. Sem `status_ready` configurado, deixe no status de criação e apenas informe.
Se alguma criação falhar, reporte o erro exato, o que foi criado e o que faltou — nunca finja sucesso.

### 7. Fechar o ciclo
Ao concluir, sugira commitar os artefatos e lembre o usuário de que, ao fim do épico (ou quando algo relevante for aprendido no meio), existe o `pbi-toolkit-compound`.

**PBI incremental motivado por descoberta (dev ou PO)**: se o passo 1 registrou que este PBI nasceu de uma descoberta do lado do dev (ex.: `architect` do `dev-toolkit` sinalizou, numa avaliação de arquitetura ou revisão final, que o corte original do épico não previa esse escopo) **ou de uma revisão manual do próprio PO** (ex.: percebeu depois que um PBI já avançado tratou uma decisão de negócio de forma ilustrativa em vez de exaustiva), ofereça registrar isso como lição agora mesmo, no mesmo mecanismo do `pbi-toolkit-compound` — não é obrigatório esperar o fim do épico pra esse caso específico, porque é exatamente o tipo de padrão que `checklist-epico.md` (itens "riscos e incertezas" / "dependências externas") ou o contrato de campos de `template-pbi.md`/`dor.md` deveria ter capturado desde o início. Mesma disciplina do compound: 1 lição, valida com o usuário, nunca grava sem confirmação.

## Compound — lições aprendidas (`pbi-toolkit-compound`)

Quando invocado, extraia 1–3 lições do ciclo e grave em `docs/knowledge/` seguindo estritamente `references/licoes.md` (formato, regras de escrita, checagem de contradições, validação com o usuário). Boas fontes de lição: PBIs que voltaram do desenvolvimento com dúvidas, `[NEEDS CLARIFICATION]` recorrentes do mesmo tema, fatiamentos que se provaram grandes/pequenos demais, dependências externas que surpreenderam, estimativas de restrição que falharam, e PBI incremental motivado por descoberta do dev (passo 7) que ainda não tiver virado lição. O objetivo: o próximo refinamento começa mais inteligente que este — e essa mesma pasta `docs/knowledge/` é lida pelo `dev-toolkit-refine` (se o repo também usar o `dev-toolkit`), então uma lição registrada aqui também informa o lado do dev, não só o próximo refinamento do PO.

## Divisão de responsabilidades

| Etapa | Dono | Ferramenta |
|---|---|---|
| Discovery / escrita do épico | PO | plugin `product-management` (Anthropic) |
| Épico → PBIs (.md no repo + issues no Jira) | PO | **este plugin** (+ grill-me no refinamento, se instalado) |
| Criação/atualização de issues | PO | MCP oficial da Atlassian |
| PBI pronto → implementação | Dev | Toolkit de desenvolvimento que o time usar no repo — ex.: `dev-toolkit` (lê o PBI do Jira) ou Spec Kit (`/speckit.specify` sobre o artefato .md). Este plugin não depende de nenhum deles. |

## Política de ferramentas (decisão do time — respeite)

Ferramentas aprovadas: **Spec Kit** (github/spec-kit, sem extensões da comunidade), **MCP oficial da Atlassian**, **product-management@knowledge-work-plugins** e **grill-me** (somente do repositório original de Matt Pocock). Não use nem recomende skills, plugins, agents ou CLIs de terceiros fora desta lista, mesmo que pareçam úteis ou estejam instalados. Se identificar valor em algo novo, sugira ao usuário levar ao time para aprovação — não use por conta própria.

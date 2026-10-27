---
name: frontend-code-review-conventions
description: Checklist de revisão para PRs frontend neste stack (React/TS/Redux/styled-components) — sinaliza padrões legados que não devem voltar e lacunas de teste/segurança conhecidas.
metadata:
  version: "0.1.0"
---

<!-- Use junto com a skill `code-review-conventions` deste mesmo plugin
     (prioridades gerais de review, formato de comentário) — esta aqui
     cobre só os pontos específicos deste stack (React/TS/Redux). -->

# Revisão de código frontend (React/TS/Redux)

Use esta skill ao revisar um pull request de frontend deste stack, além das
prioridades gerais de `code-review-conventions`.

## Bloqueadores — padrão legado voltando em código novo

Qualquer um destes num arquivo **novo** (não numa edição pequena de arquivo
legado existente) é `[blocker]`:

- Class component novo em vez de função + hooks.
- `connect()`/`mapStateToProps`/`mapDispatchToProps` para ler/disparar
  estado — use `useSelector`/`useDispatch` (ver `redux-domain-pattern`).
- `import "*.scss"` ou classe do Bootstrap/reactstrap/`@coreui` — UI nova
  usa o design system + styled-components (ver `react-view-component-pattern`).
- Nova instância `axios.create()` — ver `http-client-pattern`.
- `register()` manual ou `Controller` direto num formulário que usa
  componentes do design system — eles já encapsulam isso (ver
  `react-hook-form-pattern`).
- Reducer com switch/case manual e mutação fora de um draft do Immer.

## Bloqueadores — teste e segurança

- Código novo sem teste correspondente em `__test__/` para os critérios de
  aceite do PR (ver `frontend-tdd`) — hoje isso não é gate de CI, mas é
  gate de revisão humana.
- Asserção de teste presa a `toHaveStyle`/detalhe de implementação quando
  existia uma query por role/label disponível.
- Qualquer token, chave ou segredo em texto puro em código de `src/` —
  bloqueador de segurança, não estético; peça para mover para variável de
  ambiente/backend antes de aprovar.

## Sugestões (não bloqueiam, mas vale comentar)

- Flag de loading por campo (`loadingX`) em vez do shape padronizado
  `{data, loading, error}`.
- Prop-drilling de `control`/`errors` de formulário em vez de
  `useFormContext()`.
- Duplicação de lógica de fetch que já existe em outro domínio — sugerir
  extrair para o hook genérico de `http-client-pattern`.

## Quando aprovar

Aprove quando não restar `[blocker]` aberto — mesmo sem gate de CI
automatizado para lint/teste/tipo, a revisão humana é hoje o único portão
de qualidade real deste projeto; trate os itens acima com o mesmo rigor que
um CI verde exigiria.

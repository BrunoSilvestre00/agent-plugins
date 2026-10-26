---
name: frontend-tdd
description: Disciplina de TDD para componentes/views React deste stack — teste primeiro, colocado em __test__/, queries centradas no usuário, com renderWithRedux e mocks de store.
version: 0.1.0
---

<!-- Esta skill existe para preencher uma lacuna real: o projeto de
     referência nasceu com cobertura de teste quase nula e nenhum gate de
     CI/commit que exija teste — o conteúdo abaixo é prescritivo (o padrão
     que DEVE passar a ser seguido), não uma descrição do que já é
     praticado hoje. -->

# TDD para componentes/views (React + Jest + Testing Library)

Use esta skill **antes** de escrever a implementação de qualquer componente,
view ou hook novo — o teste vem primeiro, não depois.

## RED — escreva o teste primeiro

1. Para cada critério de aceite da task, escreva um teste que descreve o
   comportamento esperado do ponto de vista de quem usa a tela — não do
   ponto de vista de como o componente é implementado por dentro.
2. Rode o teste e confirme que ele FALHA (o componente ainda não existe ou
   não faz o que o teste espera). Não escreva a implementação antes disso.

## Onde o teste vive

```
minha-feature/
  index.tsx
  __test__/
    index.test.tsx
```

Colocado ao lado do componente, nunca numa pasta `__tests__` centralizada
distante do código testado.

## GREEN — implemente o mínimo que faz passar

Implemente só o suficiente para o teste ficar verde, respeitando
`react-view-component-pattern`/`redux-domain-pattern`. Rode a suíte inteira
(`yarn test`), não só o arquivo novo.

## Como escrever a asserção

**Prefira, nesta ordem**: `getByRole` / `getByLabelText` > `getByText` >
`getByTestId`. Use `data-testid` só quando não existir um role/label
semântico razoável (ex.: um `<div>` decorativo) — não é a query padrão,
é o último recurso.

Teste comportamento visível ao usuário, não detalhe de implementação:

```tsx
// ❌ evite — acopla o teste ao CSS
expect(image).toHaveStyle('visibility: hidden');

// ✅ prefira — testa o que o usuário percebe
expect(screen.queryByRole('img', { name: /certificado/i })).not.toBeVisible();
```

## Componentes conectados ao Redux

Use `renderWithRedux` de `utils/tests/tests.utils` — ele já embrulha Provider
real + i18n + tema + router. Passe `initialState` para simular o cenário
que o teste precisa, a partir de `store/__mock__/redux-state`:

```tsx
import { renderWithRedux } from 'utils/tests/tests.utils';
import { mockStoreDefaultState } from 'store/__mock__/redux-state';

renderWithRedux(<MinhaFeature />, {
  initialState: { ...mockStoreDefaultState, meuDominio: { data: null, loading: true, error: null } },
});
```

Componente de apresentação pura (sem Redux) usa o `render` padrão do
Testing Library — não precisa de `renderWithRedux` para tudo.

## Checklist antes de considerar a task pronta

- [ ] Todo critério de aceite tem pelo menos um teste correspondente.
- [ ] Os testes falharam antes da implementação (você confirmou isso, não
      só assumiu).
- [ ] A suíte inteira passa, não só os testes novos.
- [ ] Nenhuma asserção depende de estilo computado ou de `data-testid`
      quando havia uma query por role/label disponível.

## Nota sobre o estado atual do projeto de referência

Hoje não há gate de CI nem de pre-commit exigindo teste — isso é uma lacuna
conhecida, não um padrão a preservar. Ao adicionar código novo seguindo
esta skill, você já está corrigindo essa lacuna localmente; não espere o
gate de CI existir para aplicar a disciplina.

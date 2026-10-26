---
name: react-view-component-pattern
description: Estrutura de pasta e convenções para criar um componente ou view novo em apps React/TypeScript com styled-components e um design system próprio.
version: 0.1.0
---

# Padrão de componente/view (React + TS + styled-components)

Use esta skill ao criar um componente reutilizável ou uma view/tela nova.

## Estrutura de pasta

```
minha-feature/
  index.tsx          # o componente
  index.styled.ts     # styled-components desta pasta
  __test__/
    index.test.tsx    # teste colocado (ver skill de TDD)
  components/          # subcomponentes, cada um com a mesma estrutura
    sub-item/
      index.tsx
      index.styled.ts
```

- Nome da pasta em **kebab-case**; nunca PascalCase.
- Nunca `<nome>.tsx` solto na raiz do módulo — sempre `index.tsx`, para que o import fique `from "./minha-feature"`, não `from "./minha-feature/minha-feature"`.
- Um barrel `components/index.ts` reexporta os subcomponentes quando a pasta pai precisa expô-los: `export { default as SubItem } from "./sub-item";`.

## O componente (`index.tsx`)

- Props tipadas com `interface Props` **inline no próprio arquivo** — não crie um arquivo `@types/<nome>.ts` externo só para isso.
- `export default` do componente — não use export nomeado para componentes de view/feature.
- Estilos vêm de `import * as S from "./index.styled"` e são usados como `<S.Container>`, `<S.Label>` etc. — nunca `className` com SCSS em código novo.

```tsx
import * as S from './index.styled';

interface Props {
  title: string;
  onConfirm: () => void;
}

const MinhaFeature: React.FC<Props> = ({ title, onConfirm }) => (
  <S.Container>
    <S.Title>{title}</S.Title>
    <Button onClick={onConfirm}>Confirmar</Button>
  </S.Container>
);

export default MinhaFeature;
```

## UI básica: sempre o design system, nunca a lib de terceiros

- Componentes de UI básica (botão, input, select, modal, tabela, checkbox...) vêm de `components/common`/`components/core`/`components/ui`. **Nunca** importe `reactstrap` ou `@coreui/react` em código novo — são bibliotecas legadas em migração, mantidas só por compatibilidade com telas antigas.
- Se o design system não tiver o componente que você precisa, adicione lá (seguindo esta mesma estrutura de pasta) em vez de importar de uma lib externa pontualmente.

## O que NÃO fazer (padrão legado, não replicar)

- `index.js` com class component.
- `import "./style.scss"` + `className` do Bootstrap.
- Arquivo `<nome>.tsx` com export nomeado + tipos em `@types/<nome>.ts` externo (esse foi um padrão intermediário do design system antigo — a convenção atual é tipos inline, como acima).
- HOC `connect()`/`mapStateToProps` para ler estado — veja a skill `redux-domain-pattern` para o padrão atual (hooks).

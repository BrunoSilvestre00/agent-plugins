---
name: redux-domain-pattern
description: Convenção para adicionar um novo domínio de estado Redux (types/actions/reducers com ReducerBuilder+Immer) e consumi-lo via hooks, sem duplicar boilerplate de loading/erro.
metadata:
  version: "0.1.0"
---

# Padrão de domínio Redux

Use esta skill ao adicionar um novo pedaço de estado global (Redux) ao app.

## Anatomia de um domínio

```
meu-dominio/
  types.ts      # enum de ActionTypes + interface State + INITIAL_STATE
  models.ts     # interfaces de domínio (o shape dos dados, não do Redux)
  actions.ts    # thunks tipados
  reducers.ts   # ReducerBuilder
```

### `types.ts`

```ts
export enum ActionTypes {
  FETCH = '@meu-dominio/FETCH',
  FETCH_SUCCESS = '@meu-dominio/FETCH_SUCCESS',
  FETCH_FAIL = '@meu-dominio/FETCH_FAIL',
}

export interface State {
  data: MeuDominio | null;
  loading: boolean;
  error: string | null;
}

export const INITIAL_STATE: State = { data: null, loading: false, error: null };
```

Use sempre o shape `{ data, loading, error }` — nunca uma flag de loading por campo (`loadingX`, `loadingY`...). Isso evita a duplicação que existe em domínios antigos do projeto.

### `actions.ts` — thunk com `typesafe-actions`

```ts
import { action } from 'typesafe-actions';
import { ActionTypes } from './types';
import { client } from 'client';

export const fetchMeuDominio = () => async (dispatch: Dispatch) => {
  dispatch(action(ActionTypes.FETCH));
  try {
    const { data } = await client.get('/meu-dominio');
    dispatch(action(ActionTypes.FETCH_SUCCESS, data));
  } catch (err) {
    dispatch(action(ActionTypes.FETCH_FAIL, String(err)));
  }
};
```

### `reducers.ts` — `ReducerBuilder`, nunca switch/case manual

```ts
import { ReducerBuilder } from 'store/reducer-builder';
import { ActionTypes, INITIAL_STATE } from './types';

export default new ReducerBuilder(INITIAL_STATE)
  .addMutableReducer(ActionTypes.FETCH, state => { state.loading = true; state.error = null; })
  .addMutableReducer(ActionTypes.FETCH_SUCCESS, (state, action) => { state.loading = false; state.data = action.payload; })
  .addMutableReducer(ActionTypes.FETCH_FAIL, (state, action) => { state.loading = false; state.error = action.payload; })
  .build();
```

`addMutableReducer` já usa Immer por baixo — pode escrever `state.x = y` direto no draft. **Nunca** mude isso para mutação direta do array/objeto de estado fora de um draft do Immer (ex.: `state.items.push(x)` num reducer que não passa pelo builder) — isso já causou bug em domínios antigos do projeto.

Registre o reducer novo no combinador do domínio pai (`store/reducers.ts` ou o `reducers.ts` da view, dependendo de onde o domínio vive).

## Consumo: hooks, nunca `connect()`

```ts
const { data, loading, error } = useSelector((state: AppState) => state.meuDominio);
const dispatch = useDispatch();

useEffect(() => { dispatch(fetchMeuDominio()); }, [dispatch]);
```

`connect()`/`mapStateToProps`/`mapDispatchToProps` é padrão legado e não deve ser usado em código novo — mesmo para class components (prefira converter para função).

## O que NÃO fazer

- Reducer com switch/case manual e spread de objeto grande — use `ReducerBuilder`.
- Flag de loading por campo em vez do shape `{data, loading, error}`.
- `connect()` para ler ou disparar estado.
- Adicionar `redux-persist` a um domínio novo sem confirmar com o time — a dependência está instalada mas hoje não está conectada a nenhum reducer; não assuma que ela "só funciona".

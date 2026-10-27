---
name: http-client-pattern
description: Um cliente HTTP único e um hook de data-fetching genérico para chamadas de API, em vez de instâncias axios duplicadas e boilerplate de loading/erro repetido por view.
metadata:
  version: "0.1.0"
---

<!-- O projeto de referência tinha várias instâncias axios quase
     idênticas e nenhum hook de fetch genérico — o conteúdo abaixo é o
     padrão recomendado a seguir a partir de agora, não uma descrição do
     estado atual. -->

# Padrão de cliente HTTP e data-fetching

Use esta skill sempre que precisar chamar uma API nova ou adicionar um
endpoint a um domínio existente.

## Um cliente, não uma instância nova

**Nunca crie uma nova instância `axios.create()`** para um serviço/API novo.
Estenda o cliente HTTP já existente do projeto (interceptors de
autenticação, headers padrão, tratamento de 401/403 e retry devem viver num
único lugar). Se o serviço novo precisa de uma `baseURL` diferente, isso é
uma opção de configuração do cliente existente, não motivo para duplicar a
instância inteira — cada instância duplicada é mais um lugar para lembrar
de atualizar quando a regra de auth mudar.

Se o cliente atual do projeto ainda não suporta isso de forma centralizada,
trate a consolidação como um passo explícito, não como algo a contornar
criando mais uma instância.

## Hook de data-fetching, não thunk manual repetido

Em vez de repetir PENDING/SUCCESS/FAIL manualmente em cada `actions.ts`,
use (ou crie, se ainda não existir) um hook genérico que padroniza o shape
`{ data, loading, error }` (o mesmo shape de `redux-domain-pattern`):

```ts
const { data, loading, error, refetch } = useApiResource<MeuRecurso>('/meu-recurso');
```

Se a chamada precisa disparar efeito colateral em outro domínio Redux (não
só guardar o resultado local), ainda pode passar por um thunk — mas o thunk
delega a chamada HTTP ao cliente único, nunca reimplementa
`try/catch`+`axios` do zero.

## Nunca hardcode de segredo no client-side

Token de API, chave de criptografia ou qualquer credencial **nunca** vai em
código-fonte do frontend — qualquer coisa em `src/` vai para o bundle
público, visível a qualquer usuário no DevTools. Use variável de ambiente
injetada em build (`REACT_APP_*`) para configuração pública, e nunca para
segredo real — segredo de verdade não pertence ao frontend, só ao backend.

## O que NÃO fazer

- Criar uma nova instância axios com seus próprios interceptors de
  auth/retry — estenda a existente.
- Configurar `axios-retry` com `retries: 0` "só pra deixar plugado" — se
  não vai retentar, não adicione a dependência.
- Repetir `dispatch(PENDING)` / `.then()` / `.catch()` manual em cada
  domínio — use o hook genérico.
- Token/chave/segredo em texto puro em qualquer arquivo de `src/`.

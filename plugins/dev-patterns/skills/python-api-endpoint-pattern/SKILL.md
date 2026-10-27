---
name: python-api-endpoint-pattern
description: Router FastAPI com injeção de dependência, ciclo de vida explícito da Unit of Work e schema de resposta separado da entidade — incluindo o caso de webhook.
metadata:
  version: "0.1.1"
---

# Padrão de endpoint (FastAPI + DI)

Use esta skill ao adicionar uma rota HTTP nova (endpoint ou webhook).

## Router por recurso, descoberto automaticamente

Um router por recurso/feature, num arquivo próprio na pasta de routers —
não precisa registrar manualmente em lugar nenhum além de expor
`router = APIRouter(...)` no módulo; a aplicação descobre por convenção
de pasta.

## Injeção de dependência + ciclo de vida da UoW explícito

```python
@router.get('/{id}')
@inject
async def get_detail(
    id: str,
    uow: UnitOfWork = Depends(Provide[Container.uow]),
    meu_use_case: MeuUseCase = Depends(Provide[Container.meu_use_case]),
) -> Response:
    async with uow:
        try:
            resultado = await meu_use_case.execute(MeuUseCaseInput(algum_id=id))
        except AgregadoNaoEncontradoError:
            await uow.rollback()
            return Response(ResponseError(message="Não encontrado").model_dump_json(), status_code=404)
        except Exception as e:
            await uow.rollback()
            logger.error(f'Erro no endpoint: {e}')
            return Response(status_code=500)
    return Response(MeuResponse(resultado=resultado.resultado).model_dump_json(), status_code=200)
```

- **Quem commita é quem tem a última palavra sobre a unidade de
  trabalho** — se o endpoint delega a um use case que já chama
  `await self.uow.commit()` internamente (`python-use-case-pattern`),
  o endpoint **não** commita de novo; commitar aqui só quando o
  endpoint mexe no repositório diretamente, sem passar por um use case.
  Um commit duplicado não corrompe dado (é no-op), mas é ambiguidade
  desnecessária sobre quem é dono da fronteira da transação.
- Toda leitura/escrita passa por `async with uow:` — nunca abra sessão
  fora disso.
- Resultado de negócio esperado (não encontrado, acesso negado, dado
  inválido) chega como uma **exceção nomeada** do use case
  (`python-use-case-pattern`) e é capturado num `except` específico,
  ANTES do `except Exception` genérico — nunca um `Response` de erro
  esperado tratado igual a um bug real (500). O `except Exception`
  genérico é só para o caminho realmente inesperado.
- Schema de resposta é um modelo Pydantic próprio (`schema/<recurso>/response.py`),
  nunca a entidade de domínio serializada direto.

## Webhook: mais um passo antes de processar

Todo endpoint que recebe webhook de um provedor externo:

1. Loga o payload bruto (auditoria) **antes** de qualquer processamento.
2. Verifica a assinatura do provedor antes de confiar no conteúdo.
3. Só então delega ao use case correspondente.
4. Responde com status code explícito — nunca deixa o provedor
   reenviando indefinidamente por falta de resposta clara.

## O que NÃO fazer

- Query/commit fora de `async with uow:`.
- Deixar um resultado de negócio esperado (ex.: "recurso não
  encontrado") cair no `except Exception` genérico e virar 500 — a
  exceção nomeada do use case precisa de um `except` próprio, antes do
  genérico.
- Serializar a entidade de domínio direto como resposta HTTP — sempre
  via schema próprio.
- Processar payload de webhook antes de verificar assinatura.

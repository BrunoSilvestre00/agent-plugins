---
name: python-repository-pattern
description: Repositório fino por agregado, Unit of Work como context manager assíncrono, mapeamento imperativo do SQLAlchemy mantendo a entidade sem ORM.
metadata:
  version: "0.1.1"
---

# Padrão de repositório e Unit of Work (Python + SQLAlchemy async)

Use esta skill ao adicionar persistência para um agregado/entidade novo.

## Repositório: só os métodos que os use cases realmente usam

Nada de base genérica com `create`/`read`/`update`/`delete` que ninguém
usa por completo. Um repositório por agregado, com os métodos que a
aplicação de fato precisa:

```python
class MeuRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, agregado: MeuAgregado) -> MeuAgregado:
        self.session.add(agregado)
        return agregado

    async def get_by_id(self, id: int) -> MeuAgregado | None:
        query = select(MeuAgregado).where(MeuAgregado.id == id).limit(1)
        result = await self.session.execute(query)
        return result.scalars().first()
```

## Unit of Work: um por execução, repositórios como atributos

```python
class UnitOfWork:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def __aenter__(self):
        self._session = self._session_factory.session()
        self.meu_repository = MeuRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                await self._session.rollback()
        finally:
            await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
```

Todo caso de uso e todo endpoint que precisa de dados usa
`async with uow: ...` e chama `await uow.commit()`/`await uow.rollback()`
explicitamente — nunca confie em commit automático no fechamento do
context manager. Mas **fechar a sessão no `__aexit__` não é opcional**:
sem `await self._session.close()` ali, cada `async with uow` vaza uma
conexão do pool — sob carga concorrente isso esgota o pool em produção,
com ou sem exceção no caminho. O rollback condicional a `exc_type` é uma
rede de segurança pra exceção que escapou de um caminho que esqueceu de
chamar `uow.rollback()` explicitamente — não substitui o rollback
explícito, só evita conexão presa em transação aberta.

## Mapeamento imperativo: entidade não sabe que existe banco

A entidade de domínio (`python-domain-entity-pattern`) nunca herda de
`Base` do SQLAlchemy nem tem `Column(...)`. O mapeamento vive num módulo
central e separado, usando `registry().map_imperatively`:

```python
mapper_registry = registry()

meu_agregado_table = Table(
    "meus_agregados",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("status", Enum(MeuAgregadoStatus, native_enum=False)),
)

mapper_registry.map_imperatively(MeuAgregado, meu_agregado_table)
```

Isso mantém a entidade testável sem banco e sem import de SQLAlchemy —
só o módulo de mapeamento conhece a tabela.

## O que NÃO fazer

- Repositório genérico com métodos que nenhum use case chama.
- Commit implícito — sempre explícito, sempre dentro do `async with uow`.
- `__aexit__` que não fecha a sessão (`pass` ou só `commit`/`rollback`
  manual) — vaza conexão do pool a cada uso, mesmo no caminho feliz.
- Entidade com `Column`/`relationship`/decorator de ORM direto nela —
  isso vai pro módulo de mapeamento.
- Query solta espalhada fora do repositório (em um use case ou endpoint)
  — toda query SQL/ORM vive dentro de um método de repositório.

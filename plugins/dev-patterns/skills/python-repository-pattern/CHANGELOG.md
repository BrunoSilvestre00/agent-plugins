# Changelog — python-repository-pattern

## 0.1.1 (patch)

- Corrige `__aexit__` do exemplo, que era `pass` — não fechava a sessão
  em nenhum caminho, um vazamento de conexão garantido sob carga.
  Agora fecha sempre e faz rollback se saiu por exceção.

## 0.1.0 (minor)

- Versão inicial: repositório fino por agregado, Unit of Work como
  context manager assíncrono com commit/rollback explícitos, mapeamento
  imperativo do SQLAlchemy separado da entidade de domínio.

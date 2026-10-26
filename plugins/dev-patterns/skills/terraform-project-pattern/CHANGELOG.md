# Changelog — terraform-project-pattern

## 0.1.0 (minor)

- Versão inicial: flat vs módulo local (só extrai quando repete), state
  remoto por ambiente (bucket por conta, lock nativo S3), Makefile como
  interface única com validação de `ENV`, reaproveitar infra existente via
  data source (variável sem default), gate de CI estático/plan-só-leitura/
  apply-manual, padrão de Lambda com placeholder + `ignore_changes`.

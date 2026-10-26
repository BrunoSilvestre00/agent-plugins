# Changelog — python-observability-datadog-pattern

## 0.1.0 (minor)

- Versão inicial: `patch_all` com exclusão nomeada em vez de allowlist
  estreito (achado real: allowlist deixava chamada de saída pro gateway
  de pagamento e queries de banco sem span nenhum), sampling por padrão
  com exceção documentada para caminho crítico, logs estruturados com
  `DD_LOGS_INJECTION`, unified service tagging.

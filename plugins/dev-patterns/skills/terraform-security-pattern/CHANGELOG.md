# Changelog — terraform-security-pattern

## 0.1.0 (minor)

- Versão inicial: OIDC federado sem access key, identidade de deploy
  separada da de infra (infra sempre só-leitura, apply sempre manual),
  `lifecycle.precondition` como barreira de segurança executável, mínimo
  privilégio por função/serviço, distinção entre segredo de origem
  externa (container só) e gerado pelo Terraform (ciclo completo OK),
  execution role vs. task/runtime role.

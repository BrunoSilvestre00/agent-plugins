---
name: terraform-security-pattern
description: Identidades OIDC por ambiente/propósito, mínimo privilégio por função/serviço, barreiras de segurança executáveis (lifecycle precondition) e manuseio correto de segredo no Terraform.
version: 0.1.0
---

# Padrão de segurança em Terraform (AWS)

Use esta skill ao desenhar como o CI acessa a AWS, como uma função/serviço
recebe permissão, ou como um segredo é provisionado.

## CI nunca usa access key — sempre OIDC federado

Toda identidade que o CI assume vem de um `data "aws_iam_openid_connect_provider"`
já existente (nunca criado por este módulo) — nunca uma
`aws_iam_access_key` de longa duração. A trust policy restringe por
`StringEquals` (nunca `StringLike`/wildcard) ao repositório + ambiente
exatos do GitHub:

```hcl
condition {
  test     = "StringEquals"
  variable = "token.actions.githubusercontent.com:sub"
  values   = ["repo:${var.github_repo}:environment:${var.environment}"]
}
```

## Separe a identidade de deploy da identidade de infraestrutura

Duas identidades por ambiente, nunca uma só:

- **`ci-deploy`**: builda/publica imagem, atualiza o serviço (ECS/Lambda).
  Sem permissão de gerenciar infraestrutura além do necessário para isso.
- **`ci-infra`**: **100% leitura** (`Describe`/`Get`/`List`) sobre o
  `plan` de Terraform — zero `Create`/`Update`/`Delete`/`Put` em qualquer
  recurso. `apply` real **nunca** roda com essa identidade nem em
  nenhuma outra rodando em CI — é sempre o condutor humano, fora do
  pipeline, sem exceção.

## Barreira de segurança executável, não só documentada

Uma regra de segurança importante deve travar o `plan`/`apply`, não só
viver como comentário. Use `lifecycle.precondition`:

```hcl
resource "aws_lb_listener_rule" "servico" {
  # ...
  lifecycle {
    precondition {
      condition     = data.aws_lb.existing.internal == true
      error_message = "O load balancer referenciado precisa ser interno."
    }
  }
}
```

Isso falha a execução **antes** de criar qualquer recurso se alguém
apontar para um load balancer público por engano.

## Mínimo privilégio por função/serviço, nunca uma role compartilhada

Cada Lambda/serviço ganha sua **própria** role, com policy escopada
exatamente ao que ela usa — nunca uma role genérica reaproveitada por
várias funções "pra simplificar":

```hcl
data "aws_iam_policy_document" "minha_funcao" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.meu_segredo.arn]  # ARN exato, nunca "*"
  }
  statement {
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.minha_funcao.arn}:*"]  # só o próprio log group
  }
}
```

Permissão condicional (ex.: uma integração opcional) vai via `count`
sobre a variável que a habilita, não por uma policy sempre presente com
recurso vazio:

```hcl
resource "aws_iam_role_policy" "extra" {
  count = var.fila_arn != "" ? 1 : 0
  # ...
}
```

## Segredo: depende de quem o gerou

- **Segredo de origem externa** (token de API, credencial que já existe
  fora do Terraform): o Terraform cria só o **container**
  (`aws_secretsmanager_secret`), nunca a versão com o valor. O valor é
  inserido manualmente depois do `apply`, fora do Terraform:
  ```sh
  aws secretsmanager put-secret-value --secret-id "$(terraform output -raw meu_segredo_arn)" --secret-string '<valor real, nunca commitado>'
  ```
  Motivo: o state do Terraform grava tudo em texto plano — `sensitive = true`
  só esconde o eco no CLI, não criptografa o arquivo de state.
- **Segredo gerado pelo próprio Terraform** (ex.: senha de banco via
  `random_password`): aí sim é normal o Terraform gerenciar o ciclo de
  vida completo, incluindo `aws_secretsmanager_secret_version` com o
  valor — não existe um "original" externo pra proteger, o Terraform É a
  fonte.
- Em qualquer um dos dois casos: **nunca** um segredo em texto puro
  numa env var de task/Lambda — sempre uma referência (`valueFrom`/ARN),
  nunca o valor literal.

## Execution role vs. task/runtime role (ECS/Lambda)

- **Execution role**: usada pelo agente da plataforma pra colocar o
  processo no ar (pull de imagem, logs, secret específico da
  inicialização).
- **Task/runtime role**: assumida pelo processo em si. Se o código não
  faz nenhuma chamada a API AWS em runtime, crie a role mesmo assim,
  **vazia** (zero policy anexada) — em vez de omitir — pra a ausência de
  permissão ficar auditável por inspeção direta, não por inferência.

## O que NÃO fazer

- Access key de longa duração pra qualquer identidade de CI.
- Uma única identidade de CI fazendo deploy E aplicando infraestrutura.
- Regra de segurança só em comentário/README sem `precondition` que a
  imponha de verdade.
- Role compartilhada entre várias funções/serviços "pra não repetir".
- `Resource = "*"` numa policy quando o ARN exato é conhecido.
- Valor de segredo de origem externa dentro de um `aws_*_secret_version`
  gerenciado pelo Terraform.
- Segredo (de qualquer origem) como valor literal numa env var.

---
name: terraform-project-pattern
description: Estrutura de projeto Terraform do time — state remoto por ambiente, interface única via Makefile, reaproveitar infra existente em vez de recriar, e quando extrair módulo local.
metadata:
  version: "0.1.0"
---

# Padrão de projeto Terraform

Use esta skill ao criar ou alterar infraestrutura Terraform de um serviço
do time (AWS).

## Plano vs. módulo: comece flat, extraia só quando repetir

Um serviço único vive num diretório **flat** — `versions.tf`, `providers.tf`,
`variables.tf`, `locals.tf`, `iam.tf`, `secrets.tf`, `<recurso>.tf` por
concern (ex.: `ecs.tf`, `alb.tf`, `ecr.tf`) — sem submódulo nenhum
enquanto for um serviço só. Só extraia um módulo local (`modules/<nome>/`)
quando o **mesmo** conjunto de recursos se repete de verdade dentro do
repositório (ex.: um produto com vários contexts/serviços que todos
sobem um serviço ECS Fargate do mesmo jeito — aí `modules/ecs/service`
compensa). Extrair módulo antes de haver repetição real é complexidade
sem benefício.

Produto com múltiplos serviços/contexts independentes: um diretório raiz
de Terraform **por context**, cada um com seu próprio state — não um
único root gigante misturando tudo. Um context `shared/` à parte para
recursos de fato transversais (ex.: observability, bucket compartilhado).

## State remoto por ambiente, nunca local

```hcl
# versions.tf
terraform {
  required_version = ">= 1.10.0, < 2.0.0"

  # Bloco vazio de propósito — nunca hardcode bucket/key/region aqui.
  # Todo parâmetro vem de envs/<ambiente>.backend.hcl via -backend-config.
  # Efeito desejado: sem -backend-config, `init` FALHA em vez de cair
  # silenciosamente em state local.
  backend "s3" {}
}
```

- Um bucket S3 **por ambiente** (idealmente por conta AWS separada), nunca
  um bucket único compartilhado entre stage/production.
- Lock nativo do S3 (`use_lockfile = true` no `.backend.hcl`, Terraform
  >= 1.10) dispensa tabela DynamoDB.
- Provider pinado em versão **exata** (tem lockfile próprio,
  `.terraform.lock.hcl`, commitável); o binário `terraform` em si pode
  ficar numa faixa (`>=`/`<`), não tem lockfile equivalente no projeto.

## Interface única: nunca `terraform` cru com flags manuais

Um `Makefile` (ou script equivalente) é o único jeito de rodar
`init`/`plan`/`apply`/`output` — nunca uma chamada direta. `ENV` é
obrigatório, validado **antes** de qualquer chamada ao `terraform`
(inclusive em tempo de parse do Make), restrito a um conjunto fixo de
ambientes válidos, selecionando o par `envs/$(ENV).backend.hcl` +
`envs/$(ENV).tfvars` inteiro — nunca permita misturar backend de um
ambiente com valores de outro.

```
make plan  ENV=stage        # terraform plan -var-file=envs/stage.tfvars
make apply ENV=stage        # aprovação interativa — NUNCA -auto-approve
make plan  ENV=              # falha ANTES de invocar terraform: "ENV obrigatório"
```

## Nunca recrie o que já existe

VPC, subnets, load balancer, cluster — se a infra da empresa já existe,
referencie via `data source`, nunca crie de novo. A variável que recebe
esse identificador (`vpc_id`, `existing_alb_listener_arn`,
`existing_ecs_cluster_name`...) **não tem default** — força quem roda
`plan`/`apply` a informar o valor real, em vez de esconder o requisito
atrás de um valor implícito que arrisca criar infraestrutura nova por
acidente.

```hcl
variable "existing_ecs_cluster_name" {
  description = "Nome de um cluster ECS JÁ EXISTENTE nesta conta."
  type        = string
  # sem default
}

data "aws_ecs_cluster" "existing" {
  cluster_name = var.existing_ecs_cluster_name
}
```

## Gate de CI: estático sempre, plan só leitura, apply nunca automático

- Todo PR que toca `infra/**`: job estático (`terraform fmt -check`,
  `init -backend=false`, `validate`, `tflint`) — **sem** credencial AWS
  nenhuma.
- Job de `plan` (opcional): assume uma identidade **só leitura** (ver
  `terraform-security-pattern`), comenta o resultado no PR.
- `apply` real **nunca** roda em CI — é sempre manual, do condutor
  humano, fora de qualquer pipeline.

## Lambda: Terraform provisiona a forma, o deploy entrega o código

Quando o recurso é uma Lambda, o `apply` inicial não precisa (e não
deve) esperar o código de aplicação de verdade — use um placeholder e
ignore mudanças de código depois:

```hcl
data "archive_file" "placeholder" {
  type        = "zip"
  output_path = "${path.module}/.build/placeholder.zip"
  source {
    content  = "def handler(event, context): pass"
    filename = "handler.py"
  }
}

resource "aws_lambda_function" "minha_funcao" {
  filename = data.archive_file.placeholder.output_path
  # ...

  lifecycle {
    ignore_changes = [filename, source_code_hash]
  }
}
```

O pipeline de deploy (fora do Terraform) atualiza o código depois —
Terraform nunca precisa saber que o código mudou.

## O que NÃO fazer

- Bloco `backend "s3"` com bucket/key/region hardcoded no `.tf` versionado.
- Rodar `terraform` direto com `-var-file`/`-backend-config` na mão em
  vez de passar pela interface única (`make`).
- `apply` com `-auto-approve` em qualquer ambiente que não seja
  descartável.
- Variável de "recurso que já existe" com um default que mascara a
  obrigação de informar o valor real.
- Extrair módulo local antes de o mesmo padrão se repetir de verdade no
  repositório.

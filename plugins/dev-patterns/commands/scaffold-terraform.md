---
description: Cria o esqueleto inicial de um módulo Terraform (state remoto por ambiente, Makefile como interface única)
argument-hint: "<nome-do-projeto> (ex: meu-servico)"
---

# Scaffold inicial — Terraform (AWS)

Projeto: **$1**

Cria só o esqueleto (arquivos de configuração funcionais) — nenhum
recurso de aplicação (ECS/Lambda/etc.) de exemplo. O primeiro recurso
real usa as skills `terraform-project-pattern` (estrutura, state,
Makefile, reaproveitar infra existente) e `terraform-security-pattern`
(OIDC, mínimo privilégio, segredo) — este comando só prepara o chão
onde elas vão se aplicar.

## Passos

1. Confirme que o diretório `infra/terraform/` (ou o diretório atual, se
   for um repo dedicado a infra) está vazio ou é claramente o módulo
   novo de $1. Se houver `.tf` de outro projeto, PARE e pergunte.

2. Crie `versions.tf` — backend S3 vazio de propósito (nunca preencher
   bucket/key/region aqui; vem de `envs/<ambiente>.backend.hcl` — ver
   `terraform-project-pattern`):

   ```hcl
   terraform {
     required_version = ">= 1.10.0, < 2.0.0"

     required_providers {
       aws = {
         source  = "hashicorp/aws"
         version = "~> 5.0"  # trocar por versão exata após o primeiro `init`
       }
     }

     backend "s3" {}
   }
   ```

3. Crie `providers.tf`:

   ```hcl
   provider "aws" {
     region = var.aws_region

     default_tags {
       tags = local.common_tags
     }
   }
   ```

4. Crie `variables.tf` — só as variáveis universais; adicione as de
   rede/infra existente (`vpc_id`, `existing_*`) quando o primeiro
   recurso real precisar delas:

   ```hcl
   variable "project" {
     description = "Nome curto do projeto — usado em nomes de recursos e na tag `project`."
     type        = string
     default     = "$1"
   }

   variable "environment" {
     description = "Ambiente do deploy — exatamente \"stage\" ou \"production\"."
     type        = string

     validation {
       condition     = contains(["stage", "production"], var.environment)
       error_message = "environment deve ser exatamente \"stage\" ou \"production\"."
     }
   }

   variable "aws_region" {
     description = "Região AWS onde os recursos são criados."
     type        = string
   }
   ```

5. Crie `locals.tf`:

   ```hcl
   locals {
     name_prefix = "${var.project}-${var.environment}"

     common_tags = {
       project     = var.project
       environment = var.environment
       managed_by  = "terraform"
     }
   }
   ```

6. Crie `outputs.tf` (vazio, comentário-guia):

   ```hcl
   # Adicione outputs conforme os recursos reais forem criados —
   # ex.: ARNs/nomes que um workflow de deploy vai consumir.
   ```

7. Crie `envs/stage.backend.hcl` e `envs/production.backend.hcl` — dois
   arquivos, um por ambiente, cada um com sua própria `key` (placeholders
   — nunca commitar valor real sem confirmar com o time de infra):

   `envs/stage.backend.hcl`:
   ```hcl
   # bucket = "CHANGEME-bucket-terraform-state"
   # key    = "$1/stage/terraform.tfstate"
   # region = "CHANGEME"
   # use_lockfile = true
   ```

   `envs/production.backend.hcl` (idêntico, exceto a `key`):
   ```hcl
   # bucket = "CHANGEME-bucket-terraform-state"
   # key    = "$1/production/terraform.tfstate"
   # region = "CHANGEME"
   # use_lockfile = true
   ```

8. Crie `envs/stage.tfvars` e `envs/production.tfvars` — dois arquivos
   idênticos neste esqueleto (o conteúdo diverge conforme a infra real de
   cada ambiente for definida):

   ```hcl
   aws_region = "CHANGEME"
   ```

9. Crie `Makefile` — interface única, `ENV` obrigatório e validado antes
   de qualquer chamada ao terraform (ver `terraform-project-pattern`):

   ```makefile
   SHELL := /bin/bash
   ROOT_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
   VALID_ENVS := stage production
   ENV_TARGETS := init plan apply output

   .DEFAULT_GOAL := help
   .PHONY: help init plan apply output

   ifneq ($(filter $(ENV_TARGETS),$(MAKECMDGOALS)),)
   ifndef ENV
   $(error ENV obrigatório. Ambientes válidos: $(VALID_ENVS) (ex.: make plan ENV=stage))
   endif
   ifeq ($(filter $(ENV),$(VALID_ENVS)),)
   $(error ENV="$(ENV)" inválido. Ambientes válidos: $(VALID_ENVS))
   endif
   endif

   help:
   	@echo "Uso: make <init|plan|apply|output> ENV=<stage|production>"

   init:
   	cd "$(ROOT_DIR)" && terraform init -backend-config="envs/$(ENV).backend.hcl"

   plan:
   	cd "$(ROOT_DIR)" && terraform plan -var-file="envs/$(ENV).tfvars" -var="environment=$(ENV)"

   apply:
   	cd "$(ROOT_DIR)" && terraform apply -var-file="envs/$(ENV).tfvars" -var="environment=$(ENV)"

   output:
   	cd "$(ROOT_DIR)" && terraform output
   ```

10. Crie `.gitignore`:

    ```
    .terraform/
    *.tfstate
    *.tfstate.*
    .terraform.lock.hcl
    ```

    (Nota: alguns times preferem commitar `.terraform.lock.hcl` — se
    for o caso deste projeto, remova essa linha do `.gitignore`.)

11. Crie `.github/workflows/infra-ci.yml` — só o gate estático, sem
    credencial AWS (ver `terraform-project-pattern`; o job de `plan`
    com identidade OIDC só-leitura é adicionado depois, quando as
    identidades de `terraform-security-pattern` existirem):

    ```yaml
    name: Infra CI
    on:
      pull_request:
        paths: ["infra/**"]
    jobs:
      static:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: hashicorp/setup-terraform@v3
          - run: terraform fmt -check -recursive
          - run: terraform init -backend=false
          - run: terraform validate
    ```

12. Crie `README.md`:

    ```markdown
    # infra/terraform — $1

    Módulo Terraform único (sem submódulo — ver `terraform-project-pattern`,
    "flat até repetir"). State remoto por ambiente, `Makefile` como única
    interface (nunca `terraform` cru).

    ## Uso

    make init  ENV=stage
    make plan  ENV=stage
    make apply ENV=stage   # aprovação interativa, nunca -auto-approve

    ## Pendências do primeiro uso

    - Confirmar bucket S3 de state com o time de infra e preencher
      `envs/<ambiente>.backend.hcl`.
    - Preencher `aws_region` em `envs/<ambiente>.tfvars`.
    - Ao adicionar o primeiro recurso real: seguir
      `terraform-project-pattern` (reaproveitar VPC/ALB/cluster
      existentes via data source) e `terraform-security-pattern`
      (identidades OIDC de CI, mínimo privilégio, segredo).
    ```

13. Reporte ao usuário: estrutura criada, pendências que exigem
    confirmação humana antes do primeiro `apply` real (bucket de state,
    região, qualquer identificador de infra existente).

## Regras

- NÃO crie nenhum recurso de aplicação (ECS, Lambda, RDS, etc.) de
  exemplo — isso é infraestrutura real, fora do escopo deste comando.
- NÃO rode `terraform init`/`plan`/`apply` — isso exige credencial e
  confirmação do bucket de state, sempre uma ação do condutor humano.
- NÃO rode `git init`/commit — deixe isso para o usuário decidir.
- Se o diretório já tiver `.tf` de outro projeto, PARE e pergunte.

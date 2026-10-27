# Scaffold inicial — backend Python

Projeto: **{ALVO}**

Cria só o esqueleto (pastas + configuração funcional) — nenhum código de
domínio/exemplo. O primeiro caso de uso/entidade real do projeto usa as
skills `python-domain-entity-pattern`, `python-use-case-pattern`,
`python-repository-pattern`, `python-domain-event-pattern`,
`python-provider-adapter-pattern`, `python-api-endpoint-pattern`,
`backend-testing-pattern` — este comando só prepara o chão onde elas vão
se aplicar.

## Passos

1. Confirme que o diretório atual está vazio ou é claramente o repo novo
   do projeto {ALVO} (se houver arquivos de outro projeto, PARE e pergunte).

2. Crie a estrutura de pastas (com `.gitkeep` nas que ficam vazias):

   ```
   src/domain/entity/.gitkeep
   src/domain/event/.gitkeep
   src/application/use_case/.gitkeep
   src/application/event/.gitkeep
   src/infrastructure/repository/.gitkeep
   src/infrastructure/service/.gitkeep
   src/infrastructure/configuration/.gitkeep
   src/infrastructure/database/.gitkeep
   src/infrastructure/container/.gitkeep
   src/infrastructure/event_bus/.gitkeep
   src/infrastructure/event_store/.gitkeep
   src/presentation/api/app/router/.gitkeep
   src/presentation/api/app/schema/.gitkeep
   src/presentation/lambda/.gitkeep
   src/seed_works/helpers/.gitkeep
   src/seed_works/constants/.gitkeep
   test/domain/entity/.gitkeep
   test/application/use_case/.gitkeep
   alembic/versions/.gitkeep
   ```

3. Crie `pyproject.toml` (gerenciador de pacote: **uv** — lockfile de verdade
   em vez de `requirements.txt` solto):

   ```toml
   [project]
   name = "{ALVO}"
   version = "0.1.0"
   requires-python = ">=3.13"
   dependencies = [
       "fastapi",
       "uvicorn",
       "dependency-injector",
       "pydantic-settings",
       "sqlalchemy",
       "asyncpg",
       "alembic",
       "pytest",
       "pytest-custom_exit_code",
       "ruff",
   ]

   [tool.ruff]
   line-length = 120

   [tool.ruff.lint]
   preview = true
   select = ['I', 'F', 'E', 'W', 'PL']

   [tool.ruff.format]
   preview = true
   quote-style = 'single'

   [tool.ruff.lint.pylint]
   max-args = 10

   [tool.pytest.ini_options]
   pythonpath = ["src", "./"]
   ```

4. Crie `.pre-commit-config.yaml`:

   ```yaml
   repos:
     - repo: https://github.com/astral-sh/ruff-pre-commit
       rev: v0.8.4
       hooks:
         - id: ruff
         - id: ruff-format
   ```

5. Crie `src/infrastructure/container/container.py` — container de DI
   vazio, pronto para receber a primeira entrada quando o primeiro caso
   de uso for adicionado (ver `python-use-case-pattern`):

   ```python
   from dependency_injector import containers, providers

   from infrastructure.configuration.base import Config


   class Container(containers.DeclarativeContainer):
       config = providers.Configuration(pydantic_settings=[Config()])
       config.load()

       # Novo caso de uso? Registre aqui como providers.Factory —
       # ver a skill python-use-case-pattern.
   ```

6. Crie `src/infrastructure/configuration/base.py`:

   ```python
   from pydantic_settings import BaseSettings, SettingsConfigDict


   class Config(BaseSettings):
       model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

       DATABASE_HOST: str = ''
       DATABASE_PORT: str = ''
       DATABASE_NAME: str = ''
       DATABASE_USER: str = ''
       DATABASE_PASSWORD: str = ''
   ```

7. Crie `src/presentation/api/app/main.py` — bootstrap mínimo,
   descoberta dinâmica de router (o primeiro router real segue
   `python-api-endpoint-pattern`):

   ```python
   from fastapi import FastAPI

   from infrastructure.container.container import Container

   app = FastAPI(title='{ALVO} API')
   container = Container()
   app.container = container  # type: ignore
   ```

8. Crie `Dockerfile` (multi-stage, gate de teste no build). Copie cada
   módulo de `src/` separadamente — `main.py` precisa terminar na raiz
   do `WORKDIR` pra bater com o `CMD uvicorn main:app` abaixo, não dentro
   de `presentation/api/app/`. Sem `uv.lock` ainda (dia zero), o build
   usa `uv sync` puro — depois do primeiro `uv lock` local (passo 12),
   troque por `uv sync --locked` pra build reprodutível de verdade:

   ```dockerfile
   FROM python:3.13-slim AS builder
   COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
   WORKDIR /app
   COPY pyproject.toml ./
   RUN uv sync

   FROM python:3.13-slim
   WORKDIR /app
   COPY --from=builder /app/.venv /app/.venv
   ENV PATH="/app/.venv/bin:$PATH"
   COPY ./src/domain ./domain
   COPY ./src/application ./application
   COPY ./src/infrastructure ./infrastructure
   COPY ./src/seed_works ./seed_works
   COPY ./src/presentation/api/app ./
   COPY ./test ./test
   # --suppress-no-test-exit-code (plugin pytest-custom_exit_code): trata
   # "nenhum teste coletado" como sucesso — só no dia zero, antes do
   # primeiro teste real existir. Um teste real que FALHA continua
   # quebrando o build normalmente; a flag só cobre a suíte vazia.
   RUN pytest ./test --suppress-no-test-exit-code
   RUN rm -rf test
   EXPOSE 8000
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

9. Crie `.github/workflows/ci.yml` — gate de lint+teste em todo PR
   (mesma flag do Dockerfile pra suíte vazia no dia zero):

   ```yaml
   name: CI
   on: [pull_request]
   jobs:
     lint-test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: astral-sh/setup-uv@v3
         - run: uv sync
         - run: uv run ruff check .
         - run: uv run pytest ./test --suppress-no-test-exit-code
   ```

10. Crie `ARQUIVO_CONFIG`:

    ```markdown
    # {ALVO}

    Backend Python — Clean/Hexagonal Architecture. Convenções em
    `python-domain-entity-pattern`, `python-domain-event-pattern`,
    `python-use-case-pattern`, `python-repository-pattern`,
    `python-provider-adapter-pattern`, `python-api-endpoint-pattern`,
    `backend-testing-pattern`, `backend-code-review-conventions`
    (plugin `dev-patterns`).

    ## Dev Flow Config

    - jira_projects: <preencher>
    - status_ready: Ready for Dev
    - status_in_progress: In Progress
    - status_testing: Testing
    - base_branch: main
    - test_command: uv run pytest ./test
    - lint_command: uv run ruff check .
    ```

    `test_command`/`lint_command`/`base_branch` acima já são os valores
    reais que este scaffold acabou de configurar — não são placeholder.
    Só `jira_projects` e os nomes de status ficam genéricos aqui.

11. **Se o comando `dev-toolkit-setup` estiver disponível nesta sessão**
    (plugin `dev-toolkit` instalado — este scaffold não depende dele,
    mas se estiver presente, aproveite): invoque-o agora, passando
    `jira_projects` se o usuário já tiver informado. Ele detecta que
    `test_command`/`lint_command` já estão preenchidos (não pergunta de
    novo), consulta os status reais do workflow do Jira via Atlassian e
    completa a seção — bem melhor que os placeholders genéricos acima.
    Se o comando não estiver disponível, deixe os placeholders e avise
    no relatório final que rodar `dev-toolkit-setup` (caso o plugin seja
    instalado depois) substitui os nomes de status genéricos pelos reais.

12. Reporte ao usuário: estrutura criada, próximos passos sugeridos
    (`uv sync` pra criar o `.venv` local, depois `uv lock` e commitar
    `uv.lock` — só a partir daí o Dockerfile deve trocar pra `uv sync
    --locked` —, preencher `.env`, e — só se o passo 11 não tiver rodado
    o `dev-toolkit-setup` — preencher `jira_projects`/status na mão no
    ARQUIVO_CONFIG).

## Regras

- NÃO crie nenhum caso de uso/entidade/endpoint de exemplo — isso é
  código de domínio real, fora do escopo deste comando.
- NÃO rode `git init`/commit — deixe isso para o usuário decidir.
- Se o diretório já tiver conteúdo de outro projeto, PARE e pergunte.

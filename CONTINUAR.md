# Guia de Continuidade do Projeto

Este arquivo existe para permitir clonar o projeto em outra maquina e entender rapidamente onde o desenvolvimento parou.

## Objetivo do projeto

Construir uma pipeline de engenharia de dados para analisar criptomoedas usando a API da CoinGecko.

Fluxo planejado:

```text
CoinGecko API
  -> Python extraction
  -> Bronze local em Parquet
  -> Carga no PostgreSQL
  -> DBT Silver e Gold
  -> Dashboard Streamlit
```

O diagrama do projeto esta em:

```text
assets/diagrama.png
```

## Branches importantes

Estado local atual:

```text
main
feat/python-src-foundation
```

Uso esperado:

```text
main
```

Branch com a estrutura base do projeto.

```text
feat/python-src-foundation
```

Branch de trabalho atual. E nela que a `src` esta sendo reconstruida.

## Estrutura atual da src

```text
src/
  config.py
  logger.py

  api/
    __init__.py
    coingecko.py

  ingestion/
    __init__.py
    markets.py
    history.py
    metadata.py

  storage/
    __init__.py
    parquet.py
```

Responsabilidades:

```text
src/config.py
```

Le configuracoes do ambiente, como URL da API, timeout, quantidade de moedas, `DATA_DIR` e `LOG_DIR`.

```text
src/logger.py
```

Centraliza logs do projeto.

```text
src/api/coingecko.py
```

Cliente HTTP da CoinGecko. Ja possui base para `GET`, `params`, timeout, retry e tratamento de erro.

```text
src/storage/parquet.py
```

Funcao para salvar dados em Parquet.

```text
src/ingestion/markets.py
src/ingestion/history.py
src/ingestion/metadata.py
```

Arquivos reservados para as proximas extracoes da camada Bronze.

## Estado em que parou

Ambiente Docker foi testado e subiu corretamente:

```text
Postgres: healthy, porta 5432
pgAdmin: up, porta 5050
Airflow webserver: up, porta 8080
Airflow scheduler: up
DBT: healthy
Streamlit: up, porta 8501
```

A estrutura Python tambem foi testada:

```text
poetry check
poetry run ruff check .
poetry run pytest
```

Resultado esperado:

```text
ruff: ok
pytest: 8 passed
```

O proximo passo tecnico e testar a primeira extracao real:

```text
src/ingestion/markets.py
```

Objetivo dessa etapa:

```text
CoinGecko /coins/markets
  -> Top N moedas por market cap
  -> salvar Parquet em data/bronze/coingecko/markets/
```

## Como continuar em outra maquina

1. Clonar o repositorio:

```bash
git clone <url-do-repositorio>
cd pipeline-dados-etl
```

2. Entrar na branch de trabalho:

```bash
git switch feat/python-src-foundation
```

3. Criar o `.env`:

```bash
cp .env_example .env
```

4. Ajustar variaveis no `.env`, principalmente:

```text
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
POSTGRES_PORT
PGADMIN_DEFAULT_EMAIL
PGADMIN_DEFAULT_PASSWORD
AIRFLOW_USER_USERNAME
AIRFLOW_USER_PASSWORD
AIRFLOW_USER_EMAIL
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
DATABASE_URL
API_URL
API_KEY
DATA_DIR
LOG_DIR
```

5. Instalar dependencias locais:

```bash
poetry install
```

6. Rodar validacoes:

```bash
poetry check
poetry run ruff check .
poetry run pytest
```

7. Subir Docker:

```bash
docker compose up --build
```

Ou em segundo plano:

```bash
docker compose up --build -d
```

8. Conferir containers:

```bash
docker compose ps
```

Servicos esperados:

```text
Streamlit: http://localhost:8501
Airflow: http://localhost:8080
pgAdmin: http://localhost:5050
Postgres: localhost:5432
```

Observacao: Postgres nao abre no navegador. Ele deve ser acessado via pgAdmin, DBeaver, psql ou outro cliente SQL.

## Proximos commits sugeridos

1. Implementar extracao de mercados:

```text
feat: implement markets bronze extraction
```

Escopo:

```text
src/ingestion/markets.py
tests/unit/test_markets.py
```

2. Implementar extracao de historico:

```text
feat: implement history bronze extraction
```

3. Implementar extracao de metadados:

```text
feat: implement metadata bronze extraction
```

4. Criar DAG Bronze no Airflow:

```text
feat: add bronze ingestion airflow dag
```

5. Carregar Bronze no PostgreSQL:

```text
feat: load bronze parquet into postgres
```

6. Criar modelos DBT Silver e Gold:

```text
feat: add dbt silver and gold models
```

7. Conectar Streamlit na camada Gold:

```text
feat: build streamlit dashboard
```

## Observacoes importantes

- A pasta `data/` e a pasta `logs/` sao artefatos locais e nao devem ser commitadas.
- O arquivo `.env` nao deve ser commitado.
- O arquivo `poetry.lock`, quando gerado, deve ser commitado para travar dependencias.
- Antes de trocar de maquina, faca commit e push da branch atual.

## Como levar esta tarefa para outro PC

Esta conversa em si nao vai junto automaticamente para outro computador.

O que deve ir para o GitHub:

```text
codigo
commits
branches
CONTINUAR.md
README.md
```

Fluxo recomendado antes de trocar de maquina:

```bash
git status
git add CONTINUAR.md
git commit -m "docs: add project continuation guide"
git push origin feat/python-src-foundation
```

Depois, na outra maquina:

```bash
git clone <url-do-repositorio>
cd pipeline-dados-etl
git switch feat/python-src-foundation
```

Entao abra este arquivo:

```text
CONTINUAR.md
```

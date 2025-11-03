# -------------------
# Stage 1: Builder
# -------------------
FROM python:3.11-slim-bookworm AS builder

ARG POETRY_VERSION=1.8.2

# Instalar dependências de build apenas no builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version ${POETRY_VERSION}
ENV PATH="/root/.local/bin:$PATH"

# Configurar Poetry para não criar virtualenv
RUN poetry config virtualenvs.create false

WORKDIR /build

# Copiar apenas arquivos de dependências (melhor cache)
COPY pyproject.toml poetry.lock ./

# Instalar dependências em /usr/local
RUN poetry install --only=main --no-root --no-interaction --no-ansi

# -------------------
# Stage 2: Runtime (Imagem Final)
# -------------------
FROM python:3.11-slim

ARG USER_ID=1000
ARG GROUP_ID=1000

# Instalar apenas dependências runtime necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        bash \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Criar usuário não-root
RUN groupadd -g ${GROUP_ID} appuser \
    && useradd -m -u ${USER_ID} -g ${GROUP_ID} appuser

WORKDIR /app

# Copiar Python packages do builder (sem Poetry, sem build tools)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código da aplicação
COPY --chown=appuser:appuser ./src ./src
COPY --chown=appuser:appuser ./streamlit_app ./streamlit_app

# Mudar para usuário não-root
USER appuser

# Variáveis de ambiente
ENV PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
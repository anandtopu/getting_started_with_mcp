FROM python:3.12.13-slim-bookworm
RUN pip install --no-cache-dir uv==0.13.6
WORKDIR /course
COPY pyproject.toml uv.lock README.md ./
COPY common ./common
COPY scripts ./scripts
COPY data ./data
RUN uv sync --frozen --no-dev --extra http --extra auth
USER 65532:65532
ENV PYTHONDONTWRITEBYTECODE=1 LUMEN_BIND=0.0.0.0
EXPOSE 8000
ENTRYPOINT ["/course/.venv/bin/python", "-m", "common.deployment"]

FROM python:3.12.13-slim-bookworm
RUN pip install --no-cache-dir uv==0.13.6
WORKDIR /course
COPY pyproject.toml uv.lock README.md ./
COPY common ./common
COPY scripts ./scripts
RUN uv sync --frozen --no-dev
USER 65532:65532
ENV PYTHONDONTWRITEBYTECODE=1 LUMEN_NOTES_READ_ONLY=true
ENTRYPOINT ["/course/.venv/bin/python", "-m", "common.distributed_notes"]

FROM python:3.12.13-slim-bookworm
RUN pip install --no-cache-dir uv==0.13.6
WORKDIR /course
COPY pyproject.toml uv.lock README.md ./
COPY common ./common
COPY scripts ./scripts
COPY data ./data
COPY modules/12_security ./modules/12_security
RUN uv sync --frozen --no-dev
USER 65532:65532
ENTRYPOINT ["/course/.venv/bin/python", "modules/12_security/python/use_case/server.py"]

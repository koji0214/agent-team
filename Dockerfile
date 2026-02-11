FROM python:3.12-slim

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Use uv link mode instead of copy (faster)
# ENV UV_LINK_MODE=copy

# Place dependencies files - Assuming only pyproject.toml as uv.lock will be generated later or by user
COPY pyproject.toml ./

# Install dependencies into system site-packages (no venv needed in container)
# `uv pip sync` requires requirements.txt, but `uv pip install` works with pyproject.toml
# Or better, we can just use `uv pip install -r pyproject.toml` equivalent if uv supports it directly now,
# but usually `uv pip install` works with package specs.
# Since we have pyproject.toml, let's just install based on it.
# However, `uv pip install .` installs the current package.
# Let's ensure requirements are installed.
RUN uv pip install --system -r pyproject.toml

# Copy source code
COPY src/ ./src/

# Set Python path to include src
ENV PYTHONPATH=/app/src

# Default command
CMD ["python", "src/main.py"]

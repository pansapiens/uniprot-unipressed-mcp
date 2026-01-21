FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install build dependencies and clean up in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
#COPY pyproject.toml README.md ./
#COPY src/ ./src/
# Clone the repository
RUN git clone https://github.com/pansapiens/uniprot-unipressed-mcp.git

WORKDIR /app/uniprot-unipressed-mcp

# Install the package
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Default to stdio transport, but allow override for HTTP
ENTRYPOINT ["python", "-m", "uniprot_mcp.server"]


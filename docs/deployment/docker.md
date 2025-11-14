# Docker Setup

## Dockerfile

```dockerfile
# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Copy dependency files
COPY requirements.txt pyproject.toml ./

# Install dependencies using UV
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./static ./static

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
*.egg-info/
dist/
build/
*.md
.env
.env.local
node_modules/
static/css/input.css
tests/
```

## Building Docker Image

```bash
# Build image
docker build -t retail-branch-demo:latest .

# Run container locally
docker run -p 8080:8080 \
  -e PROJECT_ID=your-project \
  -e DATASET_ID=retail_branches \
  retail-branch-demo:latest
```

## Related Documentation

- [cloud-run.md](cloud-run.md) - Deploying to Google Cloud Run
- [cicd.md](cicd.md) - CI/CD pipeline with GitLab

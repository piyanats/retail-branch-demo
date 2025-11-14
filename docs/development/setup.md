# Local Development Setup

## Prerequisites

- Python 3.12+
- Node.js 18+ (สำหรับ Tailwind CSS)
- UV Package Manager
- Google Cloud Project with BigQuery & GCS

## Install UV Package Manager

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Setup Script (scripts/setup_local.sh)

```bash
#!/bin/bash

# Install UV if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create virtual environment with UV
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
uv pip install -r requirements.txt

# Install Node.js dependencies for Tailwind CSS
echo "Installing Node.js dependencies..."
npm install

# Build Tailwind CSS
echo "Building Tailwind CSS..."
npm run build

# Copy .env.example to .env
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update .env with your credentials"
fi

echo "Setup complete! Run './scripts/run_local.sh' to start the server"
```

## Run Script (scripts/run_local.sh)

```bash
#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Run Tailwind CSS in watch mode (background)
npm run dev &
TAILWIND_PID=$!

# Run FastAPI development server
echo "Starting FastAPI development server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Cleanup on exit
trap "kill $TAILWIND_PID" EXIT
```

## Quick Start

```bash
# Setup environment
chmod +x scripts/*.sh
./scripts/setup_local.sh

# Run development server
./scripts/run_local.sh
```

## Environment Variables

Create a `.env` file in the project root:

```bash
# Google Cloud Platform
PROJECT_ID=your-gcp-project-id
DATASET_ID=retail_branches
GCS_BUCKET=retail-branch-documents
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
SESSION_SECRET=your-random-secret-key-min-32-chars
```

## Related Documentation

- [guidelines.md](guidelines.md) - Development guidelines and code style
- [../ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture
- [../auth/oauth.md](../auth/oauth.md) - OAuth setup details

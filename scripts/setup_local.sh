#!/bin/bash
# scripts/setup_local.sh
# Local development environment setup

set -e  # Exit on error

echo "========================================="
echo "Retail Branch Demo - Local Setup"
echo "========================================="

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
uv pip install -r requirements.txt

# Install Node.js dependencies
if command -v npm &> /dev/null; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "Warning: npm not found. Skipping Node.js dependencies."
    echo "Install Node.js to build Tailwind CSS."
fi

# Build Tailwind CSS
if [ -f "package.json" ]; then
    echo "Building Tailwind CSS..."
    npm run build
fi

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your credentials!"
fi

echo "========================================="
echo "✅ Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Update .env with your credentials"
echo "2. Run './scripts/run_local.sh' to start the server"
echo ""

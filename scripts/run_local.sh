#!/bin/bash
# scripts/run_local.sh
# Run local development server

set -e  # Exit on error

echo "========================================="
echo "Starting Retail Branch Demo"
echo "========================================="

# Activate virtual environment
source .venv/bin/activate

# Run Tailwind CSS in watch mode (background)
if [ -f "package.json" ]; then
    echo "Starting Tailwind CSS watcher..."
    npm run dev &
    TAILWIND_PID=$!
fi

# Cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    if [ ! -z "$TAILWIND_PID" ]; then
        kill $TAILWIND_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Run FastAPI development server
echo "Starting FastAPI development server..."
echo "Server running at: http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

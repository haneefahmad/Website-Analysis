#!/bin/bash
# Startup script for WebsiteAnalysis

echo "Starting WebAudit LeadGen Engine..."

# Activate Python virtual environment and start FastAPI
cd "$(dirname "$0")/backend"
source .venv/bin/activate

echo "FastAPI Server running on: http://127.0.0.1:8000"
echo "Open http://127.0.0.1:8000 in your browser to view the application."

python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

#!/bin/bash
cd /home/site/wwwroot

# Install dependencies if needed
pip install -r requirements.txt

# Try Gunicorn first, fallback to Uvicorn if it fails
echo "Attempting to start with Gunicorn..."
if gunicorn app:app --bind=0.0.0.0:8000 --worker-class=sanic.workers.GunicornWorker --workers=1 --timeout=300; then
    echo "Gunicorn started successfully"
else
    echo "Gunicorn failed, trying Uvicorn..."
    uvicorn app:app --host=0.0.0.0 --port=8000 --workers=1
fi 
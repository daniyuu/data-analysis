#!/bin/bash
cd /home/site/wwwroot

# Install dependencies if needed
pip install -r requirements.txt

# Start the application with Gunicorn
# Using the correct worker class for Sanic
gunicorn app:app --bind=0.0.0.0:8000 --worker-class=sanic.worker.GunicornWorker --workers=1 --timeout=300 
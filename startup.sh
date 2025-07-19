#!/bin/bash
cd /home/site/wwwroot

# 方案1: 直接使用 Sanic (推荐)
python app.py

# 如果方案1不行，使用方案2:
# gunicorn app:app --bind 0.0.0.0:$PORT --worker-class sanic.worker.GunicornWorker --timeout 600

# 如果方案2不行，使用方案3:
# gunicorn app:app --bind 0.0.0.0:$PORT --timeout 600 --workers 1 
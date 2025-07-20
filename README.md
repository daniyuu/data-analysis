# data-analysis

pip download -r requirements.txt -d wheels

gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

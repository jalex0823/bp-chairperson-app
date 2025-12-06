web: gunicorn app:app --timeout 120
worker: python worker.py
release: flask --app app.py init-db
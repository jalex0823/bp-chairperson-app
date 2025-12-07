web: gunicorn app:app --timeout 120
worker: python worker.py
release: python add_missing_user_columns.py && flask --app app.py init-db
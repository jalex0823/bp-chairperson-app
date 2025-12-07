web: gunicorn app:app --timeout 120
worker: python worker.py
release: python add_missing_user_columns.py && python add_meeting_type_column.py && flask --app app.py init-db
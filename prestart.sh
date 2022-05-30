#! /usr/bin/env bash

# Let the DB start
# python /app/app/backend_pre_start.py

# Run migrations
# alembic upgrade head

# Create initial data in DB
# python /app/app/initial_data.py

exec uvicorn --host=0.0.0.0 --timeout-keep-alive=0 app.main:app --reload

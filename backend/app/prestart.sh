#! /usr/bin/env bash

echo "Running inside /app/prestart.sh, you could add migrations to this file, e.g.:"

# Let the DB start
python /app/app/backend_pre_start.py

# Let the DB start
sleep 10;
# Run migrations
alembic upgrade head
# seed db
python /app/app/seed_db.py
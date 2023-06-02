#! /usr/bin/env bash
set -e

celery -A app.tasks beat -s /mbache/.db/celerybeat-schedule

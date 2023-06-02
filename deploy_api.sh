#!/bin/env bash
# shellcheck disable=SC2164
cd /opt/alexbot
az login --identity
az acr login -n dannyongesaacr
docker-compose pull changachanga-backend changachanga-web
docker-compose up -d  changachanga-web changachanga-backend
docker-compose ps

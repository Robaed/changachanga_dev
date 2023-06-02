#!/usr/bin/env bash
echo 'Starting to Deploy...'
# shellcheck disable=SC2164
pushd /opt/app
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 796451236198.dkr.ecr.eu-west-2.amazonaws.com
docker image prune -f
docker compose stop postgres api
sudo rm -rf /data/postgres_data
docker compose pull api
docker compose up -d postgres api
echo 'Deployment completed successfully'
popd
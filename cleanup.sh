#!/bin/sh
set -e 

cd "$(dirname "$0")"
docker-compose down -v
docker-compose up -d

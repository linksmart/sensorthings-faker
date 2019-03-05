#!/bin/sh
set -e 

cd "$(dirname "$0")"
date
docker-compose down -v
sleep 30
docker-compose up -d

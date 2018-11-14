#!/bin/sh
set -e 

cd "$(dirname "$0")"
date
docker-compose down -v
docker-compose up -d

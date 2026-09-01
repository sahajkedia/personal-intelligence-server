#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/personal-intelligence-server}"

cd "$APP_DIR"

git fetch origin main
git reset --hard origin/main

docker compose up -d --build --remove-orphans
docker image prune -f

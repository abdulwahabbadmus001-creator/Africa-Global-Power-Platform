#!/usr/bin/env bash
set -e

echo "Starting AGP PostgreSQL and API..."
docker compose up -d --build

echo "Running database migrations..."
docker compose exec api alembic upgrade head

echo "AGP API: http://localhost:8000"
echo "Swagger: http://localhost:8000/docs"
echo "Start frontend separately: cd frontend && npm install && npm run dev"

#!/usr/bin/env bash
set -e
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

#!/bin/sh

alembic upgrade head

uvicorn app.main:app --proxy-headers --host 0.0.0.0 --port $BE_PORT --root-path $ROOT_PATH

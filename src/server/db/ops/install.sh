#!/usr/bin/env bash
set -e

apt-get update

# apt-get install -y alembic
# apt-get install -y build-essential

apt-get install -y python-mysqldb

pip install --no-cache-dir -r requirements.txt

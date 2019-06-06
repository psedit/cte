!/usr/bin/env bash
set -e

echo '=== MIGRATING DATABASE ==='
while ! mysqladmin ping -hdatabase --silent --user unilever -p$DATABASE_PASSWORD; do
    sleep 1
done

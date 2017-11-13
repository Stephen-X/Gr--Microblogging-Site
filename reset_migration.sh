#!/bin/sh
# This script resets all migrations. You'll need to rerun makemigrations & migrate after execution.
# Ref: https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
rm "db.sqlite3"

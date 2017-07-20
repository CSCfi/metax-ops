#!/bin/sh

TIMESTAMP=$(date +%Y%m%d%H%M%S)
pg_dump --format=custom $METAX_DATABASE_NAME -f {{ metax_db_backup_archive_path }}/metax_db_{{ deployment_environment_id }}_backup_${TIMESTAMP}.dump

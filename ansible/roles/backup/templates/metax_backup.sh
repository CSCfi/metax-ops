#!/bin/sh

TIMESTAMP=$(date +%Y%m%d%H%M%S)
pg_dump -f {{ metax_db_backup_path }}/archive/metax_db_{{ deployment_environment_id }}_backup_${TIMESTAMP}.dump

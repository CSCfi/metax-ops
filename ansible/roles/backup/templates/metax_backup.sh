#!/bin/sh

TIMESTAMP=$(date +%Y%m%d%H%M%S)
pg_basebackup -F t -D {{ metax_db_backup_path }}/metax_db_{{ deployment_environment_id }}_backup_${TIMESTAMP}

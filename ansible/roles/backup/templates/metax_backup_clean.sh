#!/bin/sh

find {{ metax_db_backup_archive_path }} -type f -mtime +10 -delete

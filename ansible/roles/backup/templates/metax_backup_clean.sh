#!/bin/sh

find {{ metax_db_backup_archive_path }} -type d -mtime +10 -delete

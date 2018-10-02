#!/bin/sh

MAILTO="res-paas@listat.csc.fi"
INSTANCE="$1"
VERSION="$2"
# USER="$VERSION"_"$INSTANCE"
PORT="$3"
ARCHIVEDIR="$4"
BACKUPDIR="$5"

# PG_BASEBACKUP='/usr/pgsql-9.3/bin/pg_basebackup'
DATE=`/bin/date +%Y%m%d%H%M%S`
DESTINATION="$BACKUPDIR/$DATE"

if [ ! -n "$1" ];then
  /bin/echo "usage: `basename $0` instance_name pg_version port archive_dir backup_dir"
  /bin/echo "example: `basename $0` template pg93 5500 /data/pg93/template/backup/archive /data/backup/template"
  exit
fi

case "$VERSION" in
pg93)
  PG_BASEBACKUP='/usr/pgsql-9.3/bin/pg_basebackup'
  ;;
pg96)
  PG_BASEBACKUP='/usr/pgsql-9.6/bin/pg_basebackup'
  ;;
*)
  /bin/echo "ERROR: Regognizes versions are \"pg93\" and \"pg96\". Now given \"$VERSION\""
  exit 1
  ;;
esac

# Tätä config filua voisi kehittää myös backupin tarpeisiin
# . /etc/sysconfig/pgsql/${USER}

# Check that archive directory exists and is readable.

if [ ! -d "$ARCHIVEDIR" -o ! -x "$ARCHIVEDIR" ];then
  if [ "$INSTANCE" = "metax_production" ];then
    /bin/echo "$HOSTNAME $INSTANCE backup skipped. Archive directory doesn't exist or not accessible." | /bin/mail -s "Backup $HOSTNAME" $MAILTO
  fi
  exit
fi

# Check that backup directory exists and is writable.
if [ ! -d "$BACKUPDIR" -o ! -w "$BACKUPDIR" ];then
  if [ "$INSTANCE" = "metax_production" ];then
    /bin/echo "$HOSTNAME $INSTANCE backup skipped. Backup directory doesn't exist or not writable." | /bin/mail -s "Backup $HOSTNAME" $MAILTO
  fi
  exit
fi

# Check that there is at least 2GB free space on the backup partition.
FREESPACE=`/bin/df $BACKUPDIR |grep -v Filesystem| awk '{print $4}'`
if [ $FREESPACE -lt "2000000" ];then
  if [ "$INSTANCE" = "metax_production" ];then
    /bin/echo "$HOSTNAME $INSTANCE backup skipped. Not enough available disk space." | /bin/mail -s "Backup $HOSTNAME" $MAILTO
  fi
  exit
fi

# Backup base.
#su $USER -c "$PG_BASEBACKUP -h /tmp -p $PORT -D $DESTINATION -F t -z -x -c spread"
$PG_BASEBACKUP -h /tmp -p $PORT -D $DESTINATION -F t -z -x -c spread

mv $DESTINATION/base.tar.gz $DESTINATION/base_$INSTANCE'_'$DATE.tar.gz

# Backup archives
# su $USER -c "tar -zcf $DESTINATION/archive_$INSTANCE'_'$DATE.tar.gz $ARCHIVEDIR"
tar -zcf $DESTINATION/archive_$INSTANCE'_'$DATE.tar.gz $ARCHIVEDIR

# Cleanup archives that are older than 2 days
find $ARCHIVEDIR -type f -mmin +2880 -exec rm {} \;

# Cleanup backups older than 5 days
find $BACKUPDIR -maxdepth 1 -type d -mmin +7200 -exec rm -rf {} \;

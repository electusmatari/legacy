#!/bin/bash

MYSQLFILEPATH="$1"
MYSQLFILE=`basename "$1"`

if [ -z "$MYSQLFILE" ]
then
    echo "usage: evedb.sh <mysqlfile>"
    exit 1
fi

set -e

WORKDIR=`mktemp -d --tmpdir=/tmp evedb.XXXXXXXXXX`

MYSQL2PGSQL="/home/forcer/Projects/eve-dbdump/dev/bin/mysql2pgsql.pl"
FIXUPS="/home/forcer/Projects/eve-dbdump/dev/data/update-fixups-and-fk.sql"

# VERS=-v1
VERS=$(echo "$MYSQLFILE" | sed 's/.*\(-v[0-9]*\)\.sql.*/\1/')
# PREF=tyr104
PREF=$(echo "$MYSQLFILE" | sed 's/^\([^-]*\)-.*/\1/')
# Temp DB name to use
DBNAME=mssql

bunzip2 -c "$MYSQLFILEPATH" > "$WORKDIR/${PREF}-mysql5$VERS.sql"

cd "$WORKDIR"

cat /dev/null > TMP-${PREF}-pgsql-IDX$VERS.sql
cat /dev/null > TMP-${PREF}-pgsql$VERS.sql
perl "$MYSQL2PGSQL" --noquotes --nounsignedchecks --nodrop --preserve_case \
    --sepfile TMP-${PREF}-pgsql-IDX$VERS.sql ${PREF}-mysql5$VERS.sql TMP-${PREF}-pgsql$VERS.sql
sed -e 's/`//g' "$FIXUPS" | grep FOREIGN > TMP-${PREF}-pgsql-FK$VERS.sql

dropdb $DBNAME || true
createdb $DBNAME
psql -q -f TMP-${PREF}-pgsql$VERS.sql $DBNAME
psql -q -f TMP-${PREF}-pgsql-IDX$VERS.sql $DBNAME
psql -q -f TMP-${PREF}-pgsql-FK$VERS.sql $DBNAME

pg_dump -x -O $DBNAME > ${PREF}-pgsql$VERS.sql
bzip2 -9f ${PREF}-pgsql$VERS.sql
dropdb $DBNAME

echo
echo "Conversion done, find your file here:"
echo
echo "$WORKDIR/${PREF}-pgsql$VERS.sql.bz2"

echo "Please delete $WORKDIR when done."

#!/bin/sh
set -e

umask 000

if [ "$(id -u)" != "0" ]; then
    exec "$@"
fi

PUID=${PUID:-1000}
PGID=${PGID:-1000}

if [ "$PUID" != "0" ] && [ "$PGID" != "0" ]; then
    chown -R "$PUID:$PGID" /app/config /app/logs /app/backup_config /app/downloads
    exec su-exec "$PUID:$PGID" "$@"
fi

exec "$@"

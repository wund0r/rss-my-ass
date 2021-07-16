#!/bin/sh
set -e

if [ "$1" = 'bot' ]; then
    exec python /bot.py
fi

exec "$@"

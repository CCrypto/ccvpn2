#!/bin/bash

CCVPN_PATH="$( cd "$( dirname "$0" )" && pwd )"
PATH="$HOME/.local/bin/:$PATH"

if [ -z "$1" ]; then
    echo "usage: cron_checkbtcorders.sh <config file>"
    exit 1
fi

ccvpn_checkbtcorders $1 >> $CCVPN_PATH/cron_checkbtcorders.log 2>&1


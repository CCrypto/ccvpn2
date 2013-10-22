#!/bin/bash

CCVPN_PATH="$( cd "$( dirname "$0" )" && pwd )"
PATH="$HOME/.local/bin/:$PATH"

ccvpn_checkbtcorders $CCVPN_PATH/development.ini >> $CCVPN_PATH/cron_checkbtcorders.log 2>&1


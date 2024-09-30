#!/usr/bin/env bash
#
# calls extract.py translating the args as passed from xargs
#

BUILD_DIR=${BUILD_DIR:-./build}

MAX_WAIT=${MAX_WAIT:-5}
# so they don't all start at the exact same time
WAIT=$((RANDOM % $MAX_WAIT))
echo "$1 INFO: waiting $WAIT seconds"
sleep $WAIT

# $1 is the line number
# $2 is the url
echo "$1 INFO: parallel extract starting"
./extract.py --prefix="$1 " "$2" >"${BUILD_DIR}/logos$1.json"
if [ $? -eq 0 ]; then
    echo "$1 INFO: parallel extract complete"
else
    echo "$1 ERROR: parallel extract failed"
    exit 255
fi

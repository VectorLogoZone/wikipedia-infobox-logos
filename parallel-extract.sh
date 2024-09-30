#!/usr/bin/env bash
#
# calls extract.py translating the args as passed from xargs
#

set -o errexit
set -o pipefail
set -o nounset

BUILD_DIR=${BUILD_DIR:-./build}

# $1 is the line number
# $2 is the url
./extract.py --prefix="$1 " "$2" >"${BUILD_DIR}/logos$1.json"

#!/usr/bin/env bash
#
# run the entire process
#

set -o errexit
set -o pipefail
set -o nounset

if [ -f ".env" ]; then
    export $(cat .env)
fi

BUILD_DIR=${BUILD_DIR:-./build}
if [ ! -d "${BUILD_DIR}" ]; then
    echo "INFO: creating build directory ${BUILD_DIR}"
    mkdir -p "${BUILD_DIR}"
fi

OUTPUT_DIR=${OUTPUT_DIR:-./build}
if [ ! -d "${OUTPUT_DIR}" ]; then
    echo "INFO: creating output directory ${OUTPUT_DIR}"
    mkdir -p "${OUTPUT_DIR}"
fi



export PYTHONUNBUFFERED=true

./wdumpfinder.py >"${BUILD_DIR}/files-all.txt"

wc -l "${BUILD_DIR}/files-all.txt"

./wsizecheck.py "${BUILD_DIR}/files-all.txt"

MAX_FILES=${MAX_FILES:-3}
echo "INFO: trimming list to ${MAX_FILES} files"
head -n "${MAX_FILES}" "${BUILD_DIR}/files-all.txt" >"${BUILD_DIR}/files-limited.txt"

./wsizecheck.py "${BUILD_DIR}/files-limited.txt"

# loop through the files and download them
IFS=$'\n'
FILES=($(cat "${BUILD_DIR}/files-limited.txt"))
COUNT=0
for FILE in "${FILES[@]}"; do
    echo "INFO: processing $COUNT $FILE"
    ./extract.py "$FILE" >"${BUILD_DIR}/logos${COUNT}.json"
    COUNT=$((COUNT+1))
done

echo "INFO: merging files"
./mkindex.py --output="${BUILD_DIR}/sourceData.json" "${BUILD_DIR}"/logos*.json

echo "INFO: creating sourceData.tgz in ${OUTPUT_DIR}"
tar cvzf "${OUTPUT_DIR}/sourceData.tgz" \
	"${BUILD_DIR}"/sourceData*.json

echo "INFO: build completed at $(date -u +%Y-%m-%dT%H:%M:%S)"

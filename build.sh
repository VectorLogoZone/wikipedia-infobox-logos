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

MAX_FILES=${MAX_FILES:-8}
echo "INFO: trimming list to ${MAX_FILES} files"
head -n "${MAX_FILES}" "${BUILD_DIR}/files-all.txt" >"${BUILD_DIR}/files-limited.txt"

./wsizecheck.py "${BUILD_DIR}/files-limited.txt"

echo "INFO: adding line numbers"
nl -nrz -w3 -s ' ' "${BUILD_DIR}/files-limited.txt" >"${BUILD_DIR}/files-numbered.txt"

MAX_PROCS=${MAX_PROCS:-4}
echo "INFO: extracting files in parallel with ${MAX_PROCS} processes"
cat "${BUILD_DIR}/files-numbered.txt" | xargs -n 2 -P ${MAX_PROCS} ./parallel-extract.sh

echo "INFO: merging files"
./mkindex.py --output="${BUILD_DIR}/sourceData.json" "${BUILD_DIR}"/logos*.json

echo "INFO: creating sourceData.tgz in ${OUTPUT_DIR}"
tar cvzf "${OUTPUT_DIR}/sourceData.tgz" \
	"${BUILD_DIR}"/sourceData*.json

echo "INFO: build completed at $(date -u +%Y-%m-%dT%H:%M:%S)"

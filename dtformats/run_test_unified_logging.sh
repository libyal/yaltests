#!/usr/bin/env bash
#
# Script that runs the dtFormats unified_logging.py scripts on all tracev3
# files in a storage media image. Using the dfImageTools list file entries
# script.

EXIT_FAILURE=1;
EXIT_SUCCESS=0;

DFIMAGETOOLS="${HOME}/Projects/dfimagetools";
DTFORMATS="${HOME}/Projects/dtformats";

OLDIFS=${IFS};
IFS="
";

set -e

echo "Scanning image for .tracev3 files";

TRACEV3_FILES=`PYTHONPATH=${DFIMAGETOOLS} ${DFIMAGETOOLS}/tools/list_file_entries.py --no-aliases --partitions=all --snapshots=none --volumes=all $1 | grep ".tracev3" | sed 's/^[^|]*|//;s/|.*//'`;

for TRACEV3_FILE in ${TRACEV3_FILES};
do
	PARTITIONS_ARGUMENT=`echo ${TRACEV3_FILE} | grep -e '^/p[0-9][0-9]*/' | sed 's?^/p\([0-9][0-9]*\)/.*?--partitions=\1?'`;
	TRACEV3_FILE=`echo ${TRACEV3_FILE} | sed 's?^/p[0-9][0-9]*/?/?'`;

	VOLUMES_ARGUMENT=`echo ${TRACEV3_FILE} | grep -e '/^apfs[0-9][0-9]*' | sed 's?^/apfs\([0-9][0-9]*\)/.*?--volumes=\1?'`;
	TRACEV3_FILE=`echo ${TRACEV3_FILE} | sed 's?^/apfs[0-9][0-9]*/?/?'`;

	echo "Processing: ${TRACEV3_FILE}";
	PYTHONPATH=${DTFORMATS} ${DTFORMATS}/scripts/unified_logging.py --image=$1 ${PARTITIONS_ARGUMENT} ${VOLUMES_ARGUMENT} ${TRACEV3_FILE} > /dev/null;
done

echo "Processing completed";

IFS=${OLDIFS};

exit ${RESULT};


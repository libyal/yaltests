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

# TODO: iterate all partitions individually or use dfImageTools partition identifier?

TRACEV3_FILES=`PYTHONPATH=${DFIMAGETOOLS} ${DFIMAGETOOLS}/tools/list_file_entries.py --partitions 2 $1 | grep ".tracev3" | sed 's/^[^|]*|//;s/|.*//'`;

for TRACEV3_FILE in ${TRACEV3_FILES};
do
	# Strip the partition and volume identifiers.
	# TODO: extend this.
	TRACEV3_FILE=`echo ${TRACEV3_FILE} | sed 's?^/gpt[^/]*/?/?'`;

	echo "Processing: ${TRACEV3_FILE}";
	PYTHONPATH=${DTFORMATS} ${DTFORMATS}/scripts/unified_logging.py --image $1 --partitions 2 ${TRACEV3_FILE} > /dev/null;
done

echo "Processing completed";

IFS=${OLDIFS};

exit ${RESULT};


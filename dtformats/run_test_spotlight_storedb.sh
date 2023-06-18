#!/usr/bin/env bash
#
# Script that runs the dtFormats spotlight_storedb.py scripts on all store.db
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

echo "Scanning image for store.db files";

STOREDB_FILES=`PYTHONPATH=${DFIMAGETOOLS} ${DFIMAGETOOLS}/tools/list_file_entries.py --no-aliases --partitions=all --snapshots=none --volumes=all $1 | grep "store.db" | sed 's/^[^|]*|//;s/|.*//'`;

for STOREDB_FILE in ${STOREDB_FILES};
do
	PARTITIONS_ARGUMENT=`echo ${STOREDB_FILE} | grep -e '^/p[0-9][0-9]*/' | sed 's?^/p\([0-9][0-9]*\)/.*?--partitions=\1?'`;
	STOREDB_FILE=`echo ${STOREDB_FILE} | sed 's?^/p[0-9][0-9]*/?/?'`;

	VOLUMES_ARGUMENT=`echo ${STOREDB_FILE} | grep -e '^/apfs[0-9][0-9]*' | sed 's?^/apfs\([0-9][0-9]*\)/.*?--volumes=\1?'`;
	STOREDB_FILE=`echo ${STOREDB_FILE} | sed 's?^/apfs[0-9][0-9]*/?/?'`;

	echo "Processing: ${STOREDB_FILE}";
	PYTHONPATH=${DTFORMATS} ${DTFORMATS}/scripts/spotlight_storedb.py --image=$1 ${PARTITIONS_ARGUMENT} ${VOLUMES_ARGUMENT} ${STOREDB_FILE} > /dev/null;
done

echo "Processing completed";

IFS=${OLDIFS};

exit ${RESULT};


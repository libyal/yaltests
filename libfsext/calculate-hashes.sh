#!/bin/bash
#
# Script to calculate hashes using the dfvfs-snippets recursive hasher script and libfsext.

EXIT_FAILURE=1;
EXIT_SUCCESS=0;

DFVFS_SNIPPETS="${HOME}/Projects/dfvfs-snippets";

if test $# -ne 1;
then
	echo "Usage: calculate-hashes.sh IMAGE";
	echo "";

	exit ${EXIT_FAILURE};
fi

set -e;

IMAGE=$1;

if ! test -f "${IMAGE}";
then
	echo "Missing image: ${IMAGE}";
	echo "";

	exit ${EXIT_FAILURE};
fi

IMAGE_NAME=`basename "${IMAGE}"`;

echo "Hashing ${IMAGE} with FSEXT (libfsext/pyfsext)";
time PYTHONPATH=${DFVFS_SNIPPETS}/ python3 ${DFVFS_SNIPPETS}/scripts/recursive_hasher.py --back-end EXT --output_file "${IMAGE_NAME}.hashes" --partitions all --snapshots none "${IMAGE}";

echo "";


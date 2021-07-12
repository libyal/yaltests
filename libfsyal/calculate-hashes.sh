#!/bin/bash
#
# Script to calculate hashes using the dfvfs-snippets recursive hasher script and a libyal file system library.

EXIT_FAILURE=1;
EXIT_SUCCESS=0;

DFVFS_SNIPPETS="${HOME}/Projects/dfvfs-snippets";

if test $# -ne 2;
then
	echo "Usage: calculate-hashes.sh VFS_BACK_END IMAGE";
	echo "";

	exit ${EXIT_FAILURE};
fi

set -e;

VFS_BACK_END=$1;
IMAGE=$2;

if ! test -f "${IMAGE}";
then
	echo "Missing image: ${IMAGE}";
	echo "";

	exit ${EXIT_FAILURE};
fi

IMAGE_NAME=`basename "${IMAGE}"`;

echo "Hashing ${IMAGE} with ${VFS_BACK_END}";
time PYTHONPATH=${DFVFS_SNIPPETS}/ python3 ${DFVFS_SNIPPETS}/scripts/recursive_hasher.py --back-end ${VFS_BACK_END} --output_file "${IMAGE_NAME}.hashes" --partitions all --snapshots none "${IMAGE}";

echo "";


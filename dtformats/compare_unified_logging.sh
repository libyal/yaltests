#!/bin/bash
#
# Script to compare macOS commandline utility log output with the dtFormats
# Unified Logging script.
# Requires macOS

EXIT_SUCCESS=0;
EXIT_FAILURE=1;

DTFORMATS="${HOME}/Projects/dtformats";

# Checks the availability of a binary and exits if not available.
#
# Arguments:
#   a string containing the name of the binary
#
assert_availability_binary()
{
	local BINARY=$1;

	which ${BINARY} > /dev/null 2>&1;
	if test $? -ne ${EXIT_SUCCESS};
	then
		echo "Missing binary: ${BINARY}";
		echo "";

		exit ${EXIT_FAILURE};
	fi
}

assert_availability_binary log;

if ! test -f ${TRACEV3_FILE};
then
	echo "Missing input file: ${TRACEV3_FILE}.";

	exit ${EXIT_FAILURE};
fi

TMP_PATH="compare$$";

mkdir -p ${TMP_PATH};

set -e;

log show --style json --timezone UTC --backtrace --debug --info --loss --signpost --file ${TRACEV3_FILE} > ${TMP_PATH}/log.json

PYTHONPATH=${DTFORMATS} ${DTFORMATS}/scripts/unified_logging.py --format json ${TRACEV3_FILE} > ${TMP_PATH}/dtformats.json

# Note cannot use diff since output of log is not sorted.
./compare_json.py ${TMP_PATH}/log.json ${TMP_PATH}/dtformats.json

rm -rf ${TMP_PATH};


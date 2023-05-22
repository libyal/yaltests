#!/usr/bin/env bash
#
# Script to test ewfacquire with various options
# Requires Linux with ewfacquire

EXIT_FAILURE=1;
EXIT_SUCCESS=0;

EWFACQUIRE="ewfacquire";

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

if test $# -ne 1;
then
	echo "Usage: ewfacquire.sh IMAGE_FILE";
	echo "";

	exit ${EXIT_FAILURE};
fi

assert_availability_binary ewfacquire;

set -e;

IMAGE_FILE=$1;

if ! test -f "${IMAGE_FILE}";
then
	echo "Missing image file: ${IMAGE_FILE}";
	echo "";

	exit ${EXIT_FAILURE};
fi

IMAGE_NAME=`basename "${IMAGE_FILE}"`;
IMAGE_NAME=${IMAGE_NAME/[.][^.]*/};

# Run tests using buffered read and write functions.
OUTPUT_DIRECTORY="output_buffered";

mkdir -p ${OUTPUT_DIRECTORY};

# Test all output formats.
for FORMAT in ewf smart ftk encase1 encase2 encase3 encase4 encase5 encase6 encase7 encase7-v2 linen5 linen6 linen7 ewfx;
do
	OUTPUT_NAME=${IMAGE_NAME}_format_${FORMAT};

	${EWFACQUIRE} -q -u -f ${FORMAT} -C case -D ${OUTPUT_NAME} -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/${OUTPUT_NAME} ${IMAGE_FILE}
done

# Test all block sizes.
for BLOCK_SIZE in 16 32 64 128 256 512 1024 2048 4096 8192 16384 32768;
do
	OUTPUT_NAME=${IMAGE_NAME}_block_${BLOCK_SIZE};

	${EWFACQUIRE} -q -u -b ${BLOCK_SIZE} -C case -D ${OUTPUT_NAME} -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/${OUTPUT_NAME} ${IMAGE_FILE}
done

# Test all compression methods.
# TODO: add bzip2
for COMPRESSION_METHOD in none deflate;
do
	OUTPUT_NAME=${IMAGE_NAME}_compression_${COMPRESSION_METHOD};

	${EWFACQUIRE} -q -u -c ${COMPRESSION_METHOD} -C case -D ${OUTPUT_NAME} -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/${OUTPUT_NAME} ${IMAGE_FILE}
done

# Test all additional digest hashes.
for DIGEST in sha1 sha256;
do
	OUTPUT_NAME=${IMAGE_NAME}_digest_${DIGEST}

	${EWFACQUIRE} -q -u -d ${DIGEST} -C case -D ${OUTPUT_NAME} -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/${OUTPUT_NAME} ${IMAGE_FILE}
done

# Test writing a secondary target.
${EWFACQUIRE} -q -u -C case -D ewf_with_secondary -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/ewf_primary -2 ${OUTPUT_DIRECTORY}/ewf_secondary ${IMAGE_FILE}

# Test byte swap.
${EWFACQUIRE} -q -u -s -C case -D ewf_with_byte_swap -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/ewf_byte_swap ${IMAGE_FILE}

# Run tests using chunk data read and write functions.
OUTPUT_DIRECTORY="output_chunk_data";

mkdir -p ${OUTPUT_DIRECTORY};

# Test all output formats.
for FORMAT in ewf smart ftk encase1 encase2 encase3 encase4 encase5 encase6 encase7 encase7-v2 linen5 linen6 linen7 ewfx;
do
	OUTPUT_NAME=${IMAGE_NAME}_format_${FORMAT};

	${EWFACQUIRE} -q -u -x -f ${FORMAT} -C case -D ${OUTPUT_NAME} -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/${OUTPUT_NAME} ${IMAGE_FILE}
done

# Test all block sizes.
for BLOCK_SIZE in 16 32 64 128 256 512 1024 2048 4096 8192 16384 32768;
do
	OUTPUT_NAME=${IMAGE_NAME}_block_${BLOCK_SIZE};

	${EWFACQUIRE} -q -u -x -b ${BLOCK_SIZE} -C case -D ${OUTPUT_NAME} -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/${OUTPUT_NAME} ${IMAGE_FILE}
done

# Test all compression methods.
# TODO: add bzip2
for COMPRESSION_METHOD in none deflate;
do
	OUTPUT_NAME=${IMAGE_NAME}_compression_${COMPRESSION_METHOD};

	${EWFACQUIRE} -q -u -x -c ${COMPRESSION_METHOD} -C case -D ${OUTPUT_NAME} -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/${OUTPUT_NAME} ${IMAGE_FILE}
done

# Test all additional digest hashes.
for DIGEST in sha1 sha256;
do
	OUTPUT_NAME=${IMAGE_NAME}_digest_${DIGEST}

	${EWFACQUIRE} -q -u -x -d ${DIGEST} -C case -D ${OUTPUT_NAME} -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/${OUTPUT_NAME} ${IMAGE_FILE}
done

# Test writing a secondary target.
${EWFACQUIRE} -q -u -x -C case -D ewf_with_secondary -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/ewf_primary -2 ${OUTPUT_DIRECTORY}/ewf_secondary ${IMAGE_FILE}

# Test byte swap.
${EWFACQUIRE} -q -u -x -s -C case -D ewf_with_byte_swap -e examiner -E evidence -m removable -M logical -N notes -S $(( 1024 * 1024 )) -t ${OUTPUT_DIRECTORY}/ewf_byte_swap ${IMAGE_FILE}


#!/bin/bash
#
# Script to compare multiple versions of libfsntfs.

EXIT_FAILURE=1;
EXIT_SUCCESS=0;

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

EWFMOUNT="ewfmount";
QCOWMOUNT="qcowmount";

if test $# -ne 3;
then
	echo "Usage: compare-versions.sh BASE_FSNTFSINFO TEST_FSNTFSINFO IMAGE";
	echo "";

	exit ${EXIT_FAILURE};
fi

assert_availability_binary ewfmount;
assert_availability_binary file;
assert_availability_binary gdisk;
assert_availability_binary qcowmount;

set -e;

BASE_FSNTFSINFO=$1;

if ! test -x "${BASE_FSNTFSINFO}";
then
	echo "Missing base version of fsntfsinfo";
	echo "";

	exit ${EXIT_FAILURE};
fi

TEST_FSNTFSINFO=$2;

if ! test -x "${TEST_FSNTFSINFO}";
then
	echo "Missing test version of fsntfsinfo";
	echo "";

	exit ${EXIT_FAILURE};
fi

IMAGE=$3;

if ! test -f "${IMAGE}";
then
	echo "Missing image: ${IMAGE}";
	echo "";

	exit ${EXIT_FAILURE};
fi

IS_QCOW=0;

if [[ "${IMAGE}" == *.img ]];
then
	file "${IMAGE}" | grep QCOW >/dev/null;
	IS_QCOW=1;
fi
if [[ "${IMAGE}" == *.e01 || "${IMAGE}" == *.E01 ]];
then
	if test -e "fuse";
	then
		echo "Mount point: fuse already exists";
		echo "";

		exit ${EXIT_FAILURE};
	fi
	mkdir -p fuse;

	${EWFMOUNT} -X allow_root "${IMAGE}" fuse;

	RAW_IMAGE="fuse/ewf1";

elif [[ "${IMAGE}" == *.qcow2 || ${IS_QCOW} -ne 0 ]];
then
	if test -e "fuse";
	then
		echo "Mount point: fuse already exists";
		echo "";

		exit ${EXIT_FAILURE};
	fi
	mkdir -p fuse;

	${QCOWMOUNT} -X allow_root "${IMAGE}" fuse;

	RAW_IMAGE="fuse/qcow1";

else
	RAW_IMAGE=${IMAGE};
fi

BASE_VERSION=`${BASE_FSNTFSINFO} -V | head -n1 | sed 's/^[^0-9]*\([0-9][0-9]*\)$/\1/'`;
TEST_VERSION=`${TEST_FSNTFSINFO} -V | head -n1 | sed 's/^[^0-9]*\([0-9][0-9]*\)$/\1/'`;

set +e;

# Test if fsntfsinfo is able to find a NTFS volume.
${BASE_FSNTFSINFO} ${RAW_IMAGE} > /dev/null 2>&1;
RESULT=$?;

set -e;

if test ${RESULT} -eq ${EXIT_SUCCESS};
then
	echo "Comparing fsntfsinfo ${TEST_VERSION} with ${BASE_VERSION} on p1 of ${IMAGE}";
	${BASE_FSNTFSINFO} -B p1.base.bodyfile -d -H ${RAW_IMAGE} > /dev/null;
	${TEST_FSNTFSINFO} -B p1.test.bodyfile -d -H ${RAW_IMAGE} > /dev/null;
	diff --report-identical-files p1.base.bodyfile p1.test.bodyfile;
	rm -f p1.base.bodyfile p1.test.bodyfile;
	echo "";
fi

if test ${RESULT} -ne ${EXIT_SUCCESS};
then
	SECTOR_SIZE=`gdisk -l "${RAW_IMAGE}" | grep 'Sector size (logical):' | sed 's/^Sector size (logical): //;s/ bytes$//' 2> /dev/null`;

	OLDIFS=${IFS};
	IFS="
";

	PARTITIONS=`gdisk -l "${RAW_IMAGE}" | sed '1,/Number  Start (sector)    End (sector)  Size       Code  Name/ d' 2> /dev/null`;

	for PARTITION in ${PARTITIONS};
	do
		PARTITION_NUMBER=`echo ${PARTITION} | awk '{ print $1 }'`;
		START_SECTOR=`echo ${PARTITION} | awk '{ print $2 }'`;
		START_OFFSET=$(( ${START_SECTOR} * ${SECTOR_SIZE} ));

		MOUNT_POINT="p${PARTITION_NUMBER}";

		set +e;

		# Test if fsntfsinfo is able to find a NTFS volume.
		${BASE_FSNTFSINFO} -o ${START_OFFSET} ${RAW_IMAGE} > /dev/null 2>&1;
		RESULT=$?;

		set -e;

		if test ${RESULT} -eq ${EXIT_SUCCESS};
		then
			echo "Comparing fsntfsinfo ${TEST_VERSION} with ${BASE_VERSION} on ${MOUNT_POINT} of ${IMAGE}";
			${BASE_FSNTFSINFO} -B ${MOUNT_POINT}.base.bodyfile -d -H -o ${START_OFFSET} ${RAW_IMAGE} > /dev/null;
			${TEST_FSNTFSINFO} -B ${MOUNT_POINT}.test.bodyfile -d -H -o ${START_OFFSET} ${RAW_IMAGE} > /dev/null;
			diff --report-identical-files ${MOUNT_POINT}.base.bodyfile ${MOUNT_POINT}.test.bodyfile;
			rm -f ${MOUNT_POINT}.base.bodyfile ${MOUNT_POINT}.test.bodyfile;
			echo "";
		fi
	done

	IFS=${OLDIFS};
fi

if [[ -d "fuse" ]];
then
	sudo umount "fuse";

	sleep 1;

	rmdir "fuse";
fi


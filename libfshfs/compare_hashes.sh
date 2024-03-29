#!/usr/bin/env bash
#
# Script to compare libfshfs with the operating system HFS/HFS+/HFSX implementation and libtsk
# Using the dfImageTools recursive hasher script.

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

DFIMAGETOOLS="${HOME}/Projects/dfimagetools";
EWFMOUNT="ewfmount";
QCOWMOUNT="qcowmount";

if test $# -ne 1;
then
	echo "Usage: compare-hashes.sh IMAGE";
	echo "";

	exit ${EXIT_FAILURE};
fi

assert_availability_binary ewfmount;
assert_availability_binary file;
assert_availability_binary gdisk;
assert_availability_binary qcowmount;

set -e;

IMAGE=$1;

rm -rf fshfs.hashes fshfs.hashes.sorted oshfs.hashes oshfs.hashes.sorted tsk.hashes tsk.hashes.sorted;

if ! test -f "${IMAGE}";
then
	echo "Missing image: ${IMAGE}";
	echo "";

	exit ${EXIT_FAILURE};
fi

if [[ "${IMAGE}" == *.dd || "${IMAGE}" == *.e01 || "${IMAGE}" == *.E01 || "${IMAGE}" == *.img  || "${IMAGE}" == *.qcow2 || "${IMAGE}" == *.raw ]];
then
	IS_QCOW=0;

	echo "Hashing ${IMAGE} with OS";

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

	elif [[ "${IMAGE}" == *.dd || "${IMAGE}" == *.img || "${IMAGE}" == *.raw ]];
	then
		RAW_IMAGE=${IMAGE};
	fi
	if test -e p1;
	then
		echo "Mount point: p1 already exists";
		echo "";

		exit ${EXIT_FAILURE};
	fi
	mkdir p1;

	set +e;

	# Try mounting the image as a volume image first.
	sudo mount -oro "${RAW_IMAGE}" p1;
	RESULT=$?;

	set -e;

	if test ${RESULT} -eq ${EXIT_SUCCESS};
	then
		time sudo su -c "PYTHONPATH=${DFIMAGETOOLS}/ python3 ${DFIMAGETOOLS}/tools/recursive_hasher.py --output_file oshfs.p1.hashes p1";
		sudo umount p1;
	fi
	sleep 1;

	rmdir p1;

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

			if test -e ${MOUNT_POINT};
			then
				echo "Mount point: ${MOUNT_POINT} already exists";
				echo "";

				exit ${EXIT_FAILURE};
			fi
			mkdir ${MOUNT_POINT};

			set +e;

			sudo mount -oro,offset=${START_OFFSET} "${RAW_IMAGE}" ${MOUNT_POINT};
			RESULT=$?;

			set -e;

			if test ${RESULT} -eq ${EXIT_SUCCESS};
			then
				time sudo su -c "PYTHONPATH=${DFIMAGETOOLS}/ python3 ${DFIMAGETOOLS}/tools/recursive_hasher.py --output_file oshfs.${MOUNT_POINT}.hashes ${MOUNT_POINT}";
				sudo umount ${MOUNT_POINT};
			fi
			sleep 1;

			rmdir ${MOUNT_POINT};
		done

		IFS=${OLDIFS};
	fi
	if [[ -d "fuse" ]];
	then
		sudo umount "fuse";

		sleep 1;

		rmdir "fuse";
	fi
	set +e;

	cat oshfs.p*.hashes > oshfs.hashes;

	set -e;

	rm -f oshfs.p*.hashes;
fi

echo "Hashing ${IMAGE} with TSK (libtsk/pytsk)";
time PYTHONPATH=${DFIMAGETOOLS}/ python3 ${DFIMAGETOOLS}/tools/recursive_hasher.py --back-end TSK --output_file tsk.hashes --partitions all --snapshots none "${IMAGE}";

echo "";
echo "Hashing ${IMAGE} with FSHFS (libfshfs/pyfshfs)";
time PYTHONPATH=${DFIMAGETOOLS}/ python3 ${DFIMAGETOOLS}/tools/recursive_hasher.py --back-end HFS --output_file fshfs.hashes --partitions all --snapshots none "${IMAGE}";

if test -f oshfs.hashes;
then
	cat oshfs.hashes | sed 's?\t?\t/?' | sort -k 2 > oshfs.hashes.sorted;
fi
cat tsk.hashes | sort -k 2 > tsk.hashes.sorted;
cat fshfs.hashes | sort -k 2 > fshfs.hashes.sorted;

echo "";
echo "Comparing TSK (libtsk/pytsk) and FSHFS (libfshfs/pyfshfs) for ${IMAGE}";
diff --report-identical-files tsk.hashes.sorted fshfs.hashes.sorted;

if test -f oshfs.hashes;
then
	echo "";
	echo "Comparing OS and FSHFS (libfshfs/pyfshfs) for ${IMAGE}";
	diff --report-identical-files oshfs.hashes.sorted fshfs.hashes.sorted;
fi

echo "";


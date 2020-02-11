#!/bin/bash
#
# Script to compare libfsntfs with ntfs3g and libtsk
# Using the dfvfs-snippets recursive hasher script.

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

if test $# -ne 1;
then
	echo "Usage: compare-hashes.sh IMAGE";
	echo "";

	exit ${EXIT_FAILURE};
fi

assert_availability_binary gdisk;

set -e;

IMAGE=$1;

rm -rf fsntfs.hashes fsntfs.hashes.sorted ntfs3g.hashes ntfs3g.hashes.sorted tsk.hashes tsk.hashes.sorted;

if ! test -f "${IMAGE}";
then
	echo "Missing image: ${IMAGE}";
	echo "";

	exit ${EXIT_FAILURE};
fi

if [[ "${IMAGE}" == *.dd || "${IMAGE}" == *.raw ]];
then
	echo "Hashing ${IMAGE} with OS (ntfs3g)";

	SECTOR_SIZE=`gdisk -l "${IMAGE}" | grep 'Sector size (logical):' | sed 's/^Sector size (logical): //;s/ bytes$//'`;

	OLDIFS=${IFS};
	IFS="
";

	PARTITIONS=`gdisk -l "${IMAGE}" | sed '1,/Number  Start (sector)    End (sector)  Size       Code  Name/ d'`;

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

		sudo mount -oro,offset=${START_OFFSET},show_sys_files,streams_interface=windows "${IMAGE}" ${MOUNT_POINT};

		time PYTHONPATH=${HOME}/Projects/dfvfs-snippets/ python3 ${HOME}/Projects/dfvfs-snippets/scripts/recursive_hasher.py --output_file ntfs3g.${MOUNT_POINT}.hashes ${MOUNT_POINT};

		sudo umount ${MOUNT_POINT};

		sleep 1;

		rmdir ${MOUNT_POINT};
	done

	IFS=${OLDIFS};

	cat ntfs3g.p*.hashes > ntfs3g.hashes;

	rm -f ntfs3g.p*.hashes;
fi

echo "Hashing ${IMAGE} with TSK (libtsk/pytsk)";
time PYTHONPATH=${HOME}/Projects/dfvfs-snippets/ python3 ${HOME}/Projects/dfvfs-snippets/scripts/recursive_hasher.py --back-end TSK --output_file tsk.hashes --partitions all --snapshots none "${IMAGE}";

echo "";
echo "Hashing ${IMAGE} with FSNTFS (libfsntfs/pyfsntfs)";
time PYTHONPATH=${HOME}/Projects/dfvfs-snippets/ python3 ${HOME}/Projects/dfvfs-snippets/scripts/recursive_hasher.py --back-end NTFS --output_file fsntfs.hashes --partitions all --snapshots none "${IMAGE}";

cat ntfs3g.hashes | sed 's?\t?\t/?' | sort -k 2 > ntfs3g.hashes.sorted;
cat tsk.hashes | sort -k 2 > tsk.hashes.sorted;
cat fsntfs.hashes | sort -k 2 > fsntfs.hashes.sorted;

echo "";
diff --report-identical-files tsk.hashes.sorted fsntfs.hashes.sorted;

echo "";
diff --report-identical-files ntfs3g.hashes.sorted fsntfs.hashes.sorted;

echo "";


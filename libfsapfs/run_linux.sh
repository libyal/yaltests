#!/usr/bin/env bash
#
# Script to create a bodyfile and hash file content.

fsapfstools/fsapfsinfo -B ${BODYFILE} -H -f 1 -o ${OFFSET} -r ${RECOVERY_PASSWORD} ${IMAGE}

mkdir -p fuse

fsapfstools/fsapfsmount -f 1 -o ${OFFSET} -r ${RECOVERY_PASSWORD} ${IMAGE} fuse

(cd fuse/ && find . -type f -exec md5sum {} \; > ${HOME}/MD5SUMS )

cat ${HOME}/MD5SUMS | sort -k2 > ${HOME}/MD5SUMS.sorted

# Remove sockets
grep -v d41d8cd98f00b204e9800998ecf8427e ${HOME}/MD5SUMS.sorted > ${HOME}/MD5SUMS.filtered


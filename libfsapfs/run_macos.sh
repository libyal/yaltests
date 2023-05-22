#!/usr/bin/env bash
#
# Script to create a bodyfile and hash file content on Mac OS.

sudo hdiutil attach -imagekey diskimage-class=CRawDiskImage -blocksize ${SECTORSIZE} -nomount -readonly ${IMAGE}

diskutil apfs unlockVolume ${DEVICE}

(cd ${MOUNT_POINT} && find . -exec stat -f "0|%N|%i|%p|%u|%u|%z|%a.0|%m.0|%c.0|%B.0" -t "%s" {} \; > ${HOME}/bodyfile );
(cd ${MOUNT_POINT} && find . -type f -exec md5 {} \; > ${HOME}/MD5SUMS );

cat ${HOME}/MD5SUMS | sed 's/^MD5 (\(.*\)) = \(\S*\)/\2  \1/' | sort -k2 > ${HOME}/MD5SUMS.sorted

sudo hdiutil detach ${DEVICE}


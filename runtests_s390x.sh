#!/bin/bash
#
# Script to run tests on s390x
# Requires Linux with QEMU and Docker

LIBRARY_NAME=`basename $PWD`;

cat >Dockerfile <<EOT
FROM s390x/ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install autoconf automake autopoint build-essential git libtool locales pkg-config
RUN apt-get clean && rm -rf /var/cache/apt/* /var/lib/apt/lists/*

# Set terminal to UTF-8 by default
RUN locale-gen en_US.UTF-8
RUN update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
EOT

docker build --tag test_${LIBRARY_NAME}_on_s390x .
docker run -t -v "${PWD}:/${LIBRARY_NAME}:z" ${LIBRARY_NAME}_s390x_test sh -c "cd ${LIBRARY_NAME} && tests/build.sh && tests/runtests.sh"

rm -f Dockerfile


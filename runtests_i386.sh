#!/usr/bin/env bash
#
# Script to run tests on i386
# Requires Linux with QEMU and Docker

LIBRARY_NAME=`basename $PWD`;

cat >Dockerfile <<EOT
FROM i386/ubuntu:22.04

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

TAG="test_${LIBRARY_NAME}_on_i386";

make clean
docker image build --file Dockerfile --platform linux/i386 --tag ${TAG} .
docker run -t -v "${PWD}:/${LIBRARY_NAME}:z" ${TAG} sh -c "cd ${LIBRARY_NAME} && tests/build.sh && tests/runtests.sh"

rm -f Dockerfile


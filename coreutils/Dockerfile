FROM ubuntu:26.04

ENV DEBIAN_FRONTEND=noninteractive

# Combining the apt commands into a single run reduces the size of the resulting image.
# The apt installations below are interdependent and need to be done in sequence.
RUN apt -y update && \
    apt -y install apt-transport-https apt-utils && \
    apt -y install libterm-readline-gnu-perl software-properties-common && \
    apt -y upgrade && \
    apt -y install --no-install-recommends \
        coreutils \
        locales && \
    apt clean && rm -rf /var/cache/apt/* /var/lib/apt/lists/*

# Set terminal to UTF-8 by default
RUN locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

WORKDIR /home/ubuntu

USER root

ENV TZ=UTC

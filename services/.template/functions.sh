#!/bin/sh

ACTION="$1"   # One of `bringup` and `start`
WORKDIR="$2"  # This is the persistent store, at persist/<service-name>
SRCDIR="$3"   # This is the source directory, at services/<service-name>

case "$1" in
bringup)
    ;;
start)
    ;;
esac

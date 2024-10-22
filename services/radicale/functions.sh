#!/bin/sh

ACTION="$1"
WORKDIR="$2"
SRCDIR="$3"

case "$1" in
bringup)
    python3 -m venv "${WORKDIR}/venv"
    "${WORKDIR}/venv/bin/"pip3 install radicale
    cp "${SRCDIR}/config" "${WORKDIR}/config"
    cp "${SRCDIR}/users" "${WORKDIR}/users"
    ;;
start)
    cd "$WORKDIR"
    exec .//venv/bin/python3 -m radicale -C ./config
    ;;
esac

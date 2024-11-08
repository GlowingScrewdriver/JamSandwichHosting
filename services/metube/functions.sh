#!/bin/sh

ACTION="$1"   # One of `bringup` and `start`
WORKDIR="$2"  # This is the persistent store, at persist/<service-name>
SRCDIR="$3"   # This is the source directory, at services/<service-name

case "$1" in
bringup)
    cd "$WORKDIR"
    # Run from Git repository
    [ -d metube ] || git clone https://github.com/alexta69/metube.git

    # This bit is ripped off MeTube's README.md
    cd metube/ui # NodeJS stuff
    pnpm install
    node_modules/.bin/ng build
    cd .. # Python stuff
    pipenv install
    ;;
start)
    cd "${WORKDIR}/metube"
    export URL_PREFIX="/metube/"
    exec pipenv run python3 app/main.py
    ;;
esac

#!/bin/sh

ACTION="$1"   # One of `bringup` and `start`
WORKDIR="$2"  # This is the persistent store, at persist/<service-name>
SRCDIR="$3"   # This is the source directory, at services/<service-name>

latest_release () {
    curl https://api.github.com/repos/GlowingScrewdriver/memos/releases/latest | jq -r "
        .assets |
        .[] |
        if .name | test(\"${1}\";\"\")
            then .
            else empty
        end |
        .browser_download_url
    "
}

case "$1" in
bringup)
    cd "$WORKDIR"

    # Get latest release
    dl_url=`latest_release linux_amd64`
    if [ ! -f ./memos ]; then
        curl -L $dl_url | tar -xz memos
    fi
    ;;
start)
    cd "$WORKDIR"
    ./memos
    ;;
esac

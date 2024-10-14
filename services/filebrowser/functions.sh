#!/bin/sh

ACTION="$1"
WORKDIR="$2"

cd "$WORKDIR"

latest_release () {
    curl https://api.github.com/repos/filebrowser/filebrowser/releases/latest | jq -r "
        .assets |
        .[] |
        if .name == \"${1}\"
            then .
            else empty
        end |
        .browser_download_url
    "
}

config_setup () {
    ./filebrowser config init
    ./filebrowser users add admin super-secure-pw --perm.admin
    ./filebrowser config set -a 0.0.0.0
}

case "$1" in
bringup)
    curl -L `latest_release linux-amd64-filebrowser.tar.gz` | tar -zx filebrowser
    config_setup
    ;;
start)
    exec ./filebrowser
    ;;
esac

#!/bin/sh

ACTION="$1"
WORKDIR="$2"
SRCDIR="$3"

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

filebrowser_config_setup () {
    ./filebrowser config init
    ./filebrowser users add admin super-secure-pw --perm.admin
    ./filebrowser config set -a 0.0.0.0
    ./filebrowser config set -b '/filebrowser'
    ./filebrowser config set -r './root'
}

rclone_mount_setup () {
    ln -s
}

case "$1" in
bringup)
    # Get the latest release of Filebrowser if not already done
    release_url=`latest_release linux-amd64-filebrowser.tar.gz`
    if [ ! -f ./release_url ] || [ "`cat release_url`" != "$release_url" ]; then
        echo "$release_url" > ./release_url
        curl -L "$release_url" | tar -zx filebrowser
    fi

    # Setup the configuration if not already done
    [ -f filebrowser.db ] || filebrowser_config_setup
    ;;
start)
    exec ./filebrowser
    ;;
esac

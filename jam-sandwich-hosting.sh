#!/bin/sh

# Command-line arguments
SERVICE=$1
ACTION=$2

# Information about the service. Set by parse_config
S_NAME=""
S_SOURCE=""
S_PORTMAP=""
S_OPTIONS=""


if [ -z $SERVICE ] || [ -z $ACTION ]; then
    echo "Usage: ${0} <service> <action>"
    exit 1
fi

parse_config () {
    while read name val; do
        case $name in
        NAME) S_NAME=$val;;
        SOURCE) S_SOURCE=$val;;
        PORTMAP) S_PORTMAP=$val;;
        OPTIONS) S_OPTIONS=$val;;
        '#') ;;
        *)
            echo "Invalid line: " $name $val
            exit 1
            ;;
        esac
    done < services/$SERVICE
}

#echo $S_NAME , $S_SOURCE , $S_PORTMAP , $S_OPTIONS

bringup () {
    set -x
    podman build --tag "jamsandwich_img_${SERVICE}" $S_SOURCE
    set +x
}

start () {
    set -x
    podman run --rm -d \
        --name "jamsandwich_con_${SERVICE}" \
        --mount type=bind,source=persist/$SERVICE,destination=/persist \
        -p $S_PORTMAP \
        "jamsandwich_img_${SERVICE}" $S_OPTIONS
    set +x
}

parse_config $SERVICE

case $ACTION in
bringup) bringup;;
start) start;;
stop) stop;;
*)
    echo "Invalid action: ${ACTION}"
    exit 1
    ;;
esac

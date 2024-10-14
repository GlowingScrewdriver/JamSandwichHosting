#!/bin/sh -e

ACTION="$1"
SERVICE="$2"

S_DIR="services/${SERVICE}"
PERSIST_DIR="persist/${SERVICE}"


case "$ACTION" in
bringup)
    mkdir -p "$PERSIST_DIR"
    sh -e "${S_DIR}/functions.sh" bringup "$PERSIST_DIR"
    ;;
start)
    sh -e "${S_DIR}/functions.sh" start "$PERSIST_DIR" &
    echo "${SERVICE} $!" >> pid
    ;;
stop)
    pat="${SERVICE} "
    PID=`sed -ne "s/${pat}//p" pid`
    kill $PID
    ;;
*)
    echo "Invalid action: \`${ACTION}\`"
    exit 1
    ;;
esac

#! /bin/bash

usage() {
    echo "WIP"
    echo "Usage: $0 outlet state"
    echo "Arguments:"
    echo "   outlet     Outlet # 0-7"
    echo "   state      0 for off, 1 for on, empty to get state"
    exit
}

if [[ $# < 1 ]]; then
    usage
fi

IP="10.102.16.27"
USER="autobuild:"

if [[ $# < 2 ]]; then
    echo Getting state of outlet $1
    curl -k --digest -u $USER -H "Accept:application/json" "http://10.102.16.27/restapi/relay/outlets/$1/state/"
    echo
    exit
fi

if [[ $2 == 0 ]]; then
    echo Turning outlet $1 off
    curl --digest -u $USER -X PUT -H "X-CSRF: x" --data "value=false" "http://10.102.16.27/restapi/relay/outlets/$1/state/"
elif [[ $2 == 1 ]]; then
    echo Turning outlet $1 on
    curl --digest -u $USER -X PUT -H "X-CSRF: x" --data "value=true" "http://10.102.16.27/restapi/relay/outlets/$1/state/"
else
    usage
fi

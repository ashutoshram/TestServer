#!/bin/bash

usage() {
    echo "Usage:  $0 [path to mamba_video.mvcmd]"
    exit
}

if [[ $# < 1 ]]; then
    usage
fi

# startingFW=$(mambaFwUpdater/mambaLinuxUpdater/checkMambaFW)
mambaFwUpdater/mambaLinuxUpdater/checkMambaFW
# echo $startingFW
echo
mambaFwUpdater/mambaLinuxUpdater/mambaUpdater main $1
echo
echo "Updating Mamba with new FW..."
echo
sleep 3

mambaFwUpdater/mambaLinuxUpdater/rebootMamba
echo
echo "Rebooting Mamba..."
echo
sleep 10
# updatedFW=$(mambaFwUpdater/mambaLinuxUpdater/checkMambaFW)
# echo $updatedFW
mambaFwUpdater/mambaLinuxUpdater/checkMambaFW
echo

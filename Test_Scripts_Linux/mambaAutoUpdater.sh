#!/bin/bash
startingFW=$(mambaFwUpdater/mambaLinuxUpdater/checkMambaFW)
echo $startingFW
mambaFwUpdater/mambaLinuxUpdater/mambaUpdater main ~/MX/newport/mamba_video/mvbuild/ma2085/mamba_video.mvcmd
sleep 3
mambaFwUpdater/mambaLinuxUpdater/rebootMamba
sleep 10
updatedFW=$(mambaFwUpdater/mambaLinuxUpdater/checkMambaFW)
echo $updatedFW

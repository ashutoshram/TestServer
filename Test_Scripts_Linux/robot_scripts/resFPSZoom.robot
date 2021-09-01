*** Settings ***
Documentation     Test cases for fps at different resolutions and zoom levels.
Test Template     Evaluate
Library           resFPSZoomRobot.py

*** Variables ***
${cam}          p50
${format}       NV12

*** Test Cases ***      Expression                          Expected
1080p                   ${cam} ${format} 1920 1080 30       1

720p                    ${cam} ${format} 1280 720 30        1

540p                    ${cam} ${format} 960 540 30         1

360p                    ${cam} ${format} 640 360 30         1

*** Keywords ***
Evaluate
    [Arguments]    ${expression}    ${expected}
    Eval res       ${expression}
    Result should be    ${expected}

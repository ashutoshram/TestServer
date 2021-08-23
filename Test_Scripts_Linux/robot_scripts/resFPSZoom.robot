*** Settings ***
Documentation     Test cases for fps at different resolutions and zoom levels.
...
Test Template     Evaluate
Library           resFPSZoomRobot.py

*** Test Cases ***      Expression              Expected
1080p                   NV12 1920 1080 30       1

720p                    NV12 1280 720 30        1

540p                    NV12 960 540 30         1

360p                    NV12 640 360 30         1

*** Keywords ***
Evaluate
    [Arguments]    ${expression}    ${expected}
    Eval res       ${expression}
    Result should be    ${expected}

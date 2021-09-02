*** Settings ***
Documentation     Test cases for camera property controls.
...
Test Template     Evaluate
Library           camPropRobot.py

*** Variables ***
${cam}          p50
${format}       NV12

*** Test Cases ***      Expression                                       Expected
brightness              ${cam} ${format} brightness                      1

contrast                ${cam} ${format} contrast                        1

saturation              ${cam} ${format} saturation                      1

sharpness               ${cam} ${format} sharpness                       1

white balance           ${cam} ${format} white_balance_temperature       1

*** Keywords ***
Evaluate
    [Arguments]    ${expression}    ${expected}
    Eval cam       ${expression}
    Result should be    ${expected}

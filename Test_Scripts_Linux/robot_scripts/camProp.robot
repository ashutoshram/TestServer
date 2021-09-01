*** Settings ***
Documentation     Test cases for camera property controls.
...
Test Template     Evaluate
Library           camPropRobot.py

*** Variables ***
${cam}          p50

*** Test Cases ***      Expression                             Expected
brightness              ${cam} brightness                      1

contrast                ${cam} contrast                        1

saturation              ${cam} saturation                      1

sharpness               ${cam} sharpness                       1

white balance           ${cam} white_balance_temperature       1

*** Keywords ***
Evaluate
    [Arguments]    ${expression}    ${expected}
    Eval cam       ${expression}
    Result should be    ${expected}

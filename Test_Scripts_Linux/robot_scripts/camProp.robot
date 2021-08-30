*** Settings ***
Documentation     Test cases for camera property controls.
...
Test Template     Evaluate
Library           camPropRobot.py

*** Test Cases ***      Expression                      Expected
brightness              brightness                      1

contrast                contrast                        1

saturation              saturation                      1

sharpness               sharpness                       1

white balance           white_balance_temperature       1

*** Keywords ***
Evaluate
    [Arguments]    ${expression}    ${expected}
    Eval cam       ${expression}
    Result should be    ${expected}

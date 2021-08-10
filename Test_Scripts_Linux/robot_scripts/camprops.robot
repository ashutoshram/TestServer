*** Settings ***
Documentation     Example test cases using the data-driven testing approach.
...
...               The _data-driven_ style works well when you need to repeat
...               the same workflow multiple times.
...
...               Tests use ``Calculate`` keyword created in this file, that in
...               turn uses keywords in ``CalculatorLibrary.py``. An exception
...               is the last test that has a custom _template keyword_.
...
...               Notice that one of these tests fails on purpose to show how
...               failures look like.
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

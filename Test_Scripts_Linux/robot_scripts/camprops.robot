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
Test Template     Calculate
Library           CalculatorLibrary.py

*** Test Cases ***  Expression                                      Expected
brightness          {'brightness': [0, 128, 255, 110]}              1

contrast            {'contrast': [0, 95, 191, 150]}                 1

saturation          {'saturation': [128, 136, 160, 176, 155, 143]}  1

sharpness           {'sharpness': [0, 110, 128, 255, 193, 121]}     1

white balance       {'white_balance_temperature': [0, 6500, 5000]}  1

*** Keywords ***
Calculate
    [Arguments]    ${expression}    ${expected}
    Push buttons    C${expression}=
    Result should be    ${expected}

Calculation should fail
    [Arguments]    ${expression}    ${expected}
    ${error} =    Should cause error    C${expression}=
    Should be equal    ${expected}    ${error}    # Using `BuiltIn` keyword

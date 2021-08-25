*** Settings ***
Documentation     Test cases for resolution switching.
...
Test Template     Evaluate
Library           resSwitchRobot.py

*** Test Cases ***      Expression                        Expected
1080p                   p50 MJPG 1920x1080 1280x720 30 30     1
                        # p50 MJPG 1920x1080 1280x720 30 15     1
                        # p50 MJPG 1920x1080 1280x720 15 15     1
                        # p50 MJPG 1920x1080 1280x720 15 30     1
                        # p50 MJPG 1920x1080 960x540 30 30      1
                        # p50 MJPG 1920x1080 960x540 30 15      1
                        # p50 MJPG 1920x1080 960x540 15 15      1
                        # p50 MJPG 1920x1080 960x540 15 30      1
                        # p50 MJPG 1920x1080 640x360 30 30      1
                        # p50 MJPG 1920x1080 640x360 30 15      1
                        # p50 MJPG 1920x1080 640x360 15 15      1
                        # p50 MJPG 1920x1080 640x360 15 30      1

720p                    p50 MJPG 1280x720 1920x1080 30 30     1
                        # p50 MJPG 1280x720 1920x1080 30 15     1
                        # p50 MJPG 1280x720 1920x1080 15 15     1
                        # p50 MJPG 1280x720 1920x1080 15 30     1
                        # p50 MJPG 1280x720 960x540 30 30       1
                        # p50 MJPG 1280x720 960x540 30 15       1
                        # p50 MJPG 1280x720 960x540 15 15       1
                        # p50 MJPG 1280x720 960x540 15 30       1
                        # p50 MJPG 1280x720 640x360 30 30       1
                        # p50 MJPG 1280x720 640x360 30 15       1
                        # p50 MJPG 1280x720 640x360 15 15       1
                        # p50 MJPG 1280x720 640x360 15 30       1

540p                    p50 MJPG 960x540 1920x1080 30 30      1
                        # p50 MJPG 960x540 1920x1080 30 15      1
                        # p50 MJPG 960x540 1920x1080 15 15      1
                        # p50 MJPG 960x540 1920x1080 15 30      1
                        # p50 MJPG 960x540 1280x720 30 30       1
                        # p50 MJPG 960x540 1280x720 30 15       1
                        # p50 MJPG 960x540 1280x720 15 15       1
                        # p50 MJPG 960x540 1280x720 15 30       1
                        # p50 MJPG 960x540 640x360 30 30        1
                        # p50 MJPG 960x540 640x360 30 15        1
                        # p50 MJPG 960x540 640x360 15 15        1
                        # p50 MJPG 960x540 640x360 15 30        1

360p                    p50 MJPG 640x360 1920x1080 30 30      1
                        # p50 MJPG 640x360 1920x1080 30 15      1
                        # p50 MJPG 640x360 1920x1080 15 15      1
                        # p50 MJPG 640x360 1920x1080 15 30      1
                        # p50 MJPG 640x360 1280x720 30 30       1
                        # p50 MJPG 640x360 1280x720 30 15       1
                        # p50 MJPG 640x360 1280x720 15 15       1
                        # p50 MJPG 640x360 1280x720 15 30       1
                        # p50 MJPG 640x360 960x540 30 30        1
                        # p50 MJPG 640x360 960x540 30 15        1
                        # p50 MJPG 640x360 960x540 15 15        1
                        # p50 MJPG 640x360 960x540 15 30        1

*** Keywords ***
Evaluate
    [Arguments]    ${expression}    ${expected}
    Eval switch       ${expression}
    Result should be    ${expected}

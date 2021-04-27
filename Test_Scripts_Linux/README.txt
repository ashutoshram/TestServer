Current working scripts on Linux:

CamPropControls.py
ResolutionFPS_cv2.py
ResolutionSwitch.py

Before running these tests, make sure you have python 3.6+ running and the following files in the same directory:

AbstractTestClass.py
requirements.txt

Run the command to install dependencies (opencv and numpy): pip3 install -r requirements.txt

To run the scripts:

============================================================================================================================================================================================================================

Run with flag -d True to enable writing output messages to terminal as well (set to False/disabled by default)
python3 CamPropControls.py -d True

This will generate folder CamPropControls and save log files that contain results for: brightness, contrast, saturation, sharpness, and white_balance_temperature.
The script tests to see if the device is able to get and set camera controls. To add/change the values you want to test, edit the cam_props dictionary (line 26).
A report will be generated at the end of each log file, where 1 denotes a test PASS and a -1 denotes FAIL.

============================================================================================================================================================================================================================

*NOTE: ResolutionFPS_cv2.py will need sudo permissions to reboot device in case of freeze/crash. 
Please run from root terminal (or using sudo python3) for best results (otherwise you will need to enter your password in case of device failure).

Flag -d True to enable writing output messages to terminal as well (set to False/disabled by default)
Flag -t filename.json to run the script with test cases outlined in a json file (res_fps.json by default, use that file format to create your own test cases)
Flag -z filename.json to run the script with zoom levels outlined in a json file (zoom.json by default, use that file format to create your own test cases)
Flag -p True if you are running it on the devkit + Jenkins server in order to power cycle using the network power strip (set to False by default)
Flag -v *device_name* to specify the device you want to test (set to Jabra PanaCast 50 by default)

python3 ResolutionFPS_cv2.py -d True -f res_fps_p50.json -z zoom.json -v "Jabra PanaCast 50"

This will genereate folder resolutionfps and save the corresponding log files to it.
The script tests to see if the device is able to stream video at each framerate and each resolution.
A report will be generated at the end of each log file, where:
[1] denotes a test PASS (framerate stable at that resolution), 
[0] denotes a SOFT FAIL (won't cause resolution drop in Teams), 
[-1] denotes FAIL (freeze/crash or will cause resolution drop in Teams).
By default, the threshold to pass the test is for the average framerate to be within 3 fps of the actual setting.

Formatting for ResolutionFPS_cv2.py logs:

[start date/time of test]

Panacast device found:  [device number]
=======================================================
Parameters:             [format] [resolution] [fps]
=======================================================
Testing:                [format] [resolution] [fps] [zoom]

Video format set to:    [format] ([video codec])
Resolution set to:      [width] x [height]
Setting zoom level to:  [zoom]
Setting framerate to:   [fps]
Current framerate:      [fps set by opencv]

Test duration:          [time in seconds]
Total frames grabbed:   [total expected frames] 
Total frames delayed:   [frames that arrived outside of jitter limit]    
Total frames dropped:   [invalid frames]    
Initial average fps:    [fps for initial 30 seconds]
Actual average fps:     [fps after initial 30 seconds]

============================================================================================================================================================================================================================

*NOTE: ResolutionSwitch.py will need sudo permissions to reboot device in case of freeze/crash. 
Please run from root terminal (or using sudo python3) for best results (otherwise you will need to enter your password in case of device failure).

Flag -d True to enable writing output messages to terminal as well (set to False/disabled by default)
Flag -f True to enable live video preview (set to False/disabled by default)
Flag -p True if you are running it on the devkit + Jenkins server in order to power cycle using the network power strip (set to False by default)
Flag -t filename.json to run the script with test cases outlined in a json file (res_switch.json by default, use that file format to create your own test cases)
Flag -v *device_name* to specify the device you want to test (set to Jabra PanaCast 50 by default)

python3 ResolutionSwitch.py -f True -t res_switch_p50.json -v "Jabra PanaCast 50"

This will genereate folder resolutionswitch and save the corresponding log files to it.
The script tests the framerate when switching between resolutions, taking measurements every 5 seconds.

Formatting for ResolutionSwitch.py logs:

=======================================================

[start date/time of test]

PanaCast device found:  [device number]

=======================================================
[start resolution] -> [target resolution]
Time to switch (ms):   [time in ms]

Test duration (sec):   [time in sec]
Total frames grabbed:  [frame count] 
Current average fps:   [fps]

Test duration (sec):   [time in sec]
Total frames grabbed:  [frame count] 
Current average fps:   [fps]

Test duration (sec):   [time in sec]
Total frames grabbed:  [frame count] 
Current average fps:   [fps]

Test duration (sec):   [time in sec]
Total frames grabbed:  [frame count] 
Current average fps:   [fps]

Test duration (sec):   [time in sec]
Total frames grabbed:  [frame count] 
Current average fps:   [fps]

Test duration (sec):   [time in sec]
Total frames grabbed:  [frame count] 
Current average fps:   [fps]

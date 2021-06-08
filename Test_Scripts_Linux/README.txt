Instructions for running on Jenkins Server:

PanaCast 50:
Raw tests:
python3 ResolutionFPS_cv2.py -d True -p True -t res_fps_p50.json
python3 ResolutionSwitch.py -d True -p True -t res_switch_p50.json

MJPG tests:
python3 ResolutionFPS_cv2.py -d True -p True -t res_fps_mjpg.json
python3 ResolutionSwitch.py -d True -p True -t res_switch_mjpg.json

Test results will be saved in:
[year-month-date]_failed_resolutionfps_p50.log
[year-month-date]_resolutionfps_p50.log
[year-month-date]_failed_resolutionswitch_p50.log
[year-month-date]_resolutionswitch_p50.log

PanaCast 20:
To update the device run: ./mambaAutoUpdater.sh [path to mamba_video.mvcmd]
This script calls the following executables in mambaFwUpdater/mambaLinuxUpdater: checkMambaFW, mambaUpdater, and rebootMamba
mamba_video.mvcmd should be found in ../newport/mamba_video/mvbuild/ma2085

Raw tests:
python3 ResolutionFPS_cv2.py -d True -p True -t res_fps_p20.json -v "Jabra PanaCast 20"
python3 ResolutionSwitch.py -d True -p True -t res_switch_p20.json -v "Jabra PanaCast 20"

Test results will be saved in:
[year-month-date]_failed_resolutionfps_p20.log
[year-month-date]_resolutionfps_p20.log

============================================================================================================================================================================================================================

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

Required files: CamPropControls.py, proptest.py, frame.py, logprint.py
CamPropControls will call functions from proptest, frame, and logprint.
Run with flag -d True to enable writing output messages to terminal as well (set to False/disabled by default)
python3 CamPropControls.py -d True

This will generate folder CamPropControls and save log files under directory CamPropControls that contain results for: brightness, contrast, saturation, sharpness, and white_balance_temperature.
The script tests to see if the device is able to get and set camera controls, and then analyzes frames to verify. To add/change the values you want to test, edit the cam_props dictionary (line 23-27).
A report will be generated at the end of each log file, where:
[1] denotes a test PASS (frames change in value accordingly), 
[-1] denotes FAIL (unable to set value or frames don't change as expected).

Formatting for CamPropControls.py logs:

[start date/time of test]

Panacast device found:  [device number]

setting [property] to: [value]
PASS: Successful [property] get/set
setting [property] to: [value]
PASS: Successful [property] get/set
setting [property] to: [value]
PASS: Successful [property] get/set
setting [property] to: [value]
PASS: Successful [property] get/set

[property]:             [value]    
[result]:               [result value]

[property]:             [value]  
[result]:               [result value]

[property]:             [value]  
[result]:               [result value]

[property]:             [value] 
[result]:               [result value]

============================================================================================================================================================================================================================

*NOTE: ResolutionFPS_cv2.py will need sudo permissions to reboot device in case of freeze/crash. 
Please run from root terminal (or using sudo python3) for best results (otherwise you will need to enter your password in case of device failure).
Store .json test case files in the config/ directory

Flag -d True to enable writing output messages to terminal as well (set to False/disabled by default)
Flag -f True to enable live video preview (set to False/disabled by default)
Flag -p True if you are running it on the devkit + Jenkins server in order to power cycle using the network power strip (set to False by default)
Flag -t filename.json to run the script with test cases outlined in a json file (res_fps.json by default, use that file format to create your own test cases)
Flag -v *device_name* to specify the device you want to test (set to Jabra PanaCast 50 by default)
Flag -z filename.json to run the script with zoom levels outlined in a json file (zoom.json by default, use that file format to create your own test cases)

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
Store .json test case files in the config/ directory

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

Current working scripts on Linux:

    LinuxTests.py
    ResolutionFPS_cv2.py

Before running these tests, make sure you have python 3.6+ running and the following files in the same directory:

    AbstractTestClass.py
    requirements.txt

Run the command to install dependencies (opencv and numpy): pip3 install -r requirements.txt

To run the scripts:

    Run with flag -d True to enable writing output messages to terminal as well (set to False/disabled by default)
    python3 LinuxTests.py -d True

    This will generate folders: brightness, contrast, saturation, sharpness, and white_balance_temperature and saves the corresponding log files to each of them.
    The script tests to see if the device is able to get and set camera controls. To add/change the values you want to test, edit the cam_props dictionary (line 26).
    A report will be generated at the end of each log file, where 0 denotes a test PASS and a -1 denotes FAIL.

    *NOTE: ResolutionFPS_cv2.py will need sudo permissions to reboot device in case of freeze/crash. 
           Please run from root terminal (or using sudo python3) for best results (otherwise you will need to enter your password in case of device failure).
    
    Run with flag -d True to enable writing output messages to terminal as well (set to False/disabled by default)
    sudo python3 ResolutionFPS_cv2.py -d True

    This will genereate folder resolutionfps and save the corresponding log files to it.
    The script tests to see if the device is able to stream video at each framerate and each resolution.
    A report will be generated at the end of each log file, where 0 denotes a test PASS (framerate stable at that resolution) and a -1 denotes FAIL.
    By default, the threshold to pass the test is for the average framerate to be within 3 fps of the actual setting.

Formatting for ResolutionFPS_cv2.py logs:
NV12 (video format) 540p (resolution) 30 (framerate) 45 (zoom level)

Current working scripts on Linux:

    LinuxTests.py
    ResolutionFPS_cv2.py

Before running these tests, make sure you have python 3.6+ running and the following files in the same directory:

    AbstractTestClass.py
    requirements.txt

Run the command to install dependencies (opencv and numpy): pip3 install -r requirements.txt

To run the scripts:

    python3 LinuxTests.py

    This will generate folders: brightness, contrast, saturation, sharpness, and white_balance_temperature and saves the corresponding log files to each of them.
    The script tests to see if the device is able to get and set camera controls. To add/change the values you want to test, edit the cam_props dictionary (line 26).
    A report will be generated at the end of each log file, where 0 denotes a test PASS and a -1 denotes FAIL.

    python3 ResolutionFPS_cv2.py

    This will genereate folder resolutionfps and save the corresponding log files to it.
    The script tests to see if the device is able to stream video at each framerate and each resolution. To add/change the values you want to test, edit the fps_params dictionary (line 182).
    A report will be generated at the end of each log file, where 0 denotes a test PASS (framerate stable at that resolution) and a -1 denotes FAIL.
    By default, the threshold to pass the test is for the average framerate to be within 2 fps of the actual setting. To change that threshold, edit the variables diff5 and diff10 (line 165).

    For both scripts, set the variable debug=True if you want messages to be printed to terminal and set debug=False if you want it to only be saved in the log files.

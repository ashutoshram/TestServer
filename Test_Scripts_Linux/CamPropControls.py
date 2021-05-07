import cv2
import subprocess
import os
import re
import time
import datetime
import json
import argparse
import subprocess
import logprint
import proptest
import frame

ap = argparse.ArgumentParser()
ap.add_argument("-d","--debug", type=bool, default=False, help="Set to True to disable msgs to terminal")
ap.add_argument("-v","--video", type=str, default="Jabra PanaCast 50", help="Specify which camera to test")
args = vars(ap.parse_args())
debug = args["debug"]
device_name = args["video"]

current = datetime.date.today()
path = os.getcwd()

cam_props = {'brightness': [0, 128, 255, 110],
             'contrast': [0, 95, 191, 150],
             'saturation': [128, 136, 160, 176, 155, 143],
             'sharpness': [0, 110, 128, 255, 193, 121],
             'white_balance_temperature': [0, 6500, 5000]}

# set up camera stream
try:
    cam = subprocess.check_output('v4l2-ctl --list-devices 2>/dev/null | grep "{}" -A 1 | grep video'.format(device_name), shell=True, stderr=subprocess.STDOUT)
    cam = cam.decode("utf-8")
    device_num = int(re.search(r'\d+', cam).group())
    device = 'v4l2-ctl -d /dev/video{}'.format(device_num)
except subprocess.CalledProcessError as e:
    raise RuntimeError("Command '{}' returned with error (code {}): {}".format(e.cmd, e.returncode, e.output))

# iterate thru cam_props dict and test each value of each cam prop
cap = cv2.VideoCapture(device_num)
for prop in cam_props:
    # create log file for the current cam prop
    filename = "{}_CamPropControls.log".format(current)
    file_path = os.path.join(path+"/CamPropControls", filename)

    # create directory for log files if it doesn't already exist
    if not os.path.exists(path+"/CamPropControls"):
        os.makedirs(path+"/CamPropControls")
    log_file = open(file_path, "a")

    timestamp = datetime.datetime.now()
    logprint.send("{}\n\nPanacast device found:  {}\n".format(timestamp, device_num), debug, log_file)

    ctrl = cam_props[prop]
    basic = {}

    cap.open(device_num)
    for c in ctrl:
        basic[c] = proptest.get_set(device, prop, c, debug, log_file)

    if prop == "brightness":
        values = frame.brightness(device, cap, ctrl, debug, log_file)
        advanced = proptest.eval_results(ctrl, values, debug, log_file)
    elif prop == "contrast":
        values = frame.contrast(device, cap, ctrl, debug, log_file)
        advanced = proptest.eval_results(ctrl, values, debug, log_file)
    elif prop == "saturation":
        values = frame.saturation(device, cap, ctrl, debug, log_file)
        advanced = proptest.eval_results(ctrl, values, debug, log_file)
    elif prop == "sharpness":
        pass # TODO: implement sharpness() and sharpness_eval()
    elif prop == "white_balance":
        pass # TODO: implement white_balance() and white_balance_eval()
    
    logprint.send("\nGenerating report...\n", debug, log_file)
    report = json.dumps(advanced, indent=2)
    logprint.send("{}\n".format(report), debug, log_file)
    logprint.send("Exiting {} test now...\n".format(prop), debug, log_file)
    logprint.send(55*"="+"\n", debug, log_file)
    advanced.clear()

cap.release()
log_file.close()

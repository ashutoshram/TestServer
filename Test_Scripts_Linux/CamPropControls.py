import cv2
import subprocess
import os
import re
import time
import datetime
import json
import argparse
import subprocess
import log_print

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
for prop in cam_props:
    # create log file for the current cam prop
    filename = "{}_CamPropControls.log".format(current)
    file_path = os.path.join(path+"/CamPropControls", filename)

    # create directory for log files if it doesn't already exist
    if not os.path.exists(path+"/CamPropControls"):
        os.makedirs(path+"/CamPropControls")
    log_file = open(file_path, "a")

    timestamp = datetime.datetime.now()
    # log_print("{}\n".format(timestamp))
    log_print.send("{}\n\nPanacast device found:  {}\n".format(timestamp, device_num), debug, log_file)

    ctrl = cam_props[prop]
    err_code = {}

    for val in ctrl:
        # log_print("{}: {}".format(prop, val))
        subprocess.call(['{} -c {}={}'.format(device, prop, str(val))], shell=True)
        s = subprocess.check_output(['{} -C {}'.format(device, prop)], shell=True)
        s = s.decode('UTF-8')
        value = re.match("(.*): (\d+)", s)
        if value.group(2) != str(val):
            log_print.send("FAIL: {} get/set not working as intended".format(prop), debug, log_file)
            err_code[val] = -1
        else:
            log_print.send("{} set to: {}".format(prop, value.group(2)), debug, log_file)
            log_print.send("PASS: Successful {} test conducted".format(prop), debug, log_file)
            err_code[val] = 1
    
    log_print.send("\nGenerating report...\n", debug, log_file)
    # report = p.pformat(err_code)
    report = json.dumps(err_code, indent=2)
    log_print.send("{}\n".format(report), debug, log_file)
    log_print.send("Exiting {} test now...\n".format(prop), debug, log_file)
    log_print.send(55*"="+"\n", debug, log_file)

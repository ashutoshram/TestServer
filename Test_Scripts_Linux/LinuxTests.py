import cv2
import subprocess
import os
import re
import time
from datetime import date
import datetime
import pprint as p
import json

current = date.today()
path = os.getcwd()
debug = True

# print to file (and optionally terminal)
def log_print(args):
    msg = args + "\n"
    try:
        log_file.write(msg)
    except Exception as e:
        print(e)

    if debug is True: 
        print(args)

cam_props = {'brightness': [0, 128, 255],
             'contrast': [0, 95, 191],
             'saturation': [128, 136, 160, 176, 155],
             'sharpness': [0, 110, 128, 255, 193],
             'white_balance_temperature': [0, 5000, 6500]}

err_code = {}

# set up camera stream
for k in range(4):
    cam = cv2.VideoCapture(k)
    if cam.isOpened():
        device_num = k
        break

device = 'v4l2-ctl -d /dev/video{}'.format(device_num)

# iterate thru cam_props dict and test each value of each cam prop
for prop in cam_props:
    # create log file for the current cam prop
    filename = "{}_{}.log".format(current, prop)
    file_path = os.path.join(path+"/{}".format(prop), filename)

    # create directory for long and .png files if it doesn't already exist
    if not os.path.exists(path+"/{}".format(prop)):
        os.makedirs(path+"/{}".format(prop))
    log_file = open(file_path, "a")

    timestamp = datetime.datetime.now()
    log_print("{}\n".format(timestamp))

    ctrl = cam_props[prop]

    for val in ctrl:
        # log_print("{}: {}".format(prop, val))
        subprocess.call(['{} -c {}={}'.format(device, prop, str(val))], shell=True)
        s = subprocess.check_output(['{} -C {}'.format(device, prop)], shell=True)
        s = s.decode('UTF-8')
        value = re.match("(.*): (\d+)", s)
        if value.group(2) != str(val):
            log_print("FAIL: {} get/set not working as intended".format(prop))
            err_code[val] = -1
        else:
            log_print("{} set to: {}".format(prop, value.group(2)))
            log_print("PASS: Successful {} test conducted".format(prop))
            err_code[val] = 0
    
    log_print("\nGenerating report...\n")
    # report = p.pformat(err_code)
    report = json.dumps(err_code, indent=2)
    log_print("{}\n".format(report))
    log_print("Exiting {} test now...\n".format(prop))
    log_print(55*"="+"\n")

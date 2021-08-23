import cv2
import os, sys, subprocess
import json, re
import argparse
import numpy as np
import pprint as p
import time
from datetime import date, datetime

current = date.today()
path = os.getcwd()
cap = None
debug = True
device = None
device_name = "Jabra PanaCast 50"
device_num = 0
log_file = None
power_cycle = False
reboots_hard = 0
reboots_soft = 0
result = -1
err_code = {}
failures = {}

cam_props = {'brightness': [0, 128, 255, 110],
             'contrast': [0, 95, 191, 150],
             'saturation': [128, 136, 160, 176, 155, 143],
             'sharpness': [0, 110, 128, 255, 193, 121],
             'white_balance_temperature': [0, 6500, 5000]}

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

def get_device():
    global cap
    global device
    global device_num

    # grab reenumerated device
    try:
        cam = subprocess.check_output('v4l2-ctl --list-devices 2>/dev/null | grep "{}" -A 1 | grep video'.format(device_name), shell=True, stderr=subprocess.STDOUT)
    except:
        return False

    cam = cam.decode("utf-8")
    device_num = int(re.search(r'\d+', cam).group())
    device = 'v4l2-ctl -d /dev/video{}'.format(device_num)
    cap = cv2.VideoCapture(device_num)

    if cap.isOpened():
        log_print("Device number:  {}\n".format(device_num))
        cap.open(device_num)
        return True
    else:
        return False

def reboot_device():
    global device_num
    global reboots_hard
    global reboots_soft
    switch = 0

    log_print("Rebooting...")
    # reboot by resetting USB if testing P20
    if device_name == "Jabra PanaCast 20":
        subprocess.check_call(['./mambaFwUpdater/mambaLinuxUpdater/rebootMamba'])
        time.sleep(10)
        if not get_device():
            log_print("Failed to get device after reboot, exiting test :(")
            sys.exit(0)

    # reboot P50 by resetting USB, adb reboot, or network power
    else:
        os.system("adb shell /usr/bin/resethub")
        time.sleep(15)
        reboots_soft += 1
        if not get_device():
            if power_cycle is True:
                subprocess.check_call(['./power_switch.sh', '{}'.format(switch), '0'])
                time.sleep(3)
                subprocess.check_call(['./power_switch.sh', '{}'.format(switch), '1'])
            else:
                os.system("sudo adb kill-server")
                os.system("sudo adb devices")
                os.system("adb reboot")
            
            time.sleep(50)
            reboots_hard += 1
            log_print("Soft reboot count: {}".format(reboots_soft))
            log_print("Hard reboot count: {}".format(reboots_hard))
            if not get_device():
                log_print("Unable to recover device, exiting test. Please check physical device\n")
                sys.exit(0)

    if reboots_hard > 5:
        log_print("More than 5 reboots_hard, exiting test. Please check physical device\n")
        sys.exit(0)

# basic get/set test using v4l2
def get_set(device, prop, val):
    subprocess.call(['{} -c {}={}'.format(device, prop, str(val))], shell=True)
    s = subprocess.check_output(['{} -C {}'.format(device, prop)], shell=True)
    s = s.decode('UTF-8')
    value = re.match("(.*): (\d+)", s)
    log_print("setting {} to: {}".format(prop, value.group(2)))

    if value.group(2) != str(val):
        log_print("FAIL: {} get/set not working as intended".format(prop))
        return -1
    else:
        log_print("PASS: Successful {} get/set".format(prop))
        return 1

def eval_results(ctrl, values):
    results = {}

    for c, v in zip(range(len(ctrl)), range(len(values))):
        if c == len(ctrl) - 1 or v == len(values) - 1:
            break 
        if (ctrl[c] < ctrl[c + 1] and values[v] < values[v + 1]) or (ctrl[c] > ctrl[c + 1] and values[v] > values[v + 1]):
            results[ctrl[c]] = 1
            results[ctrl[c + 1]] = 1
        else:
            results[ctrl[c]] = -1
            results[ctrl[c + 1]] = -1
    
    report = p.pformat(results, width=20)
    log_print(report+"\n")
    fail = -1
    if fail in results.values():
        return -1
    else:
        return 1

# evaluate the luma for each specified brightness value, return list of results
def brightness(raw_frames):
    results = []
    for frame in raw_frames:      
        # convert to grayscale and calculate luma
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        luma = np.average(f)
        log_print("Luma:        {:<5}".format(luma))
        results.append(luma)

    return results

# evaluate otsu threshold for each contrast value, return list of results
def contrast(raw_frames):
    results = []
    for frame in raw_frames: 
        # convert to grayscale and calculate otsu
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cont = f.std()
        log_print("Contrast:  {}".format(cont))
        results.append(cont)
    
    return results

# evaluate hsv for each saturation value, return list of results
def saturation(raw_frames):
    results = []
    for frame in raw_frames:      
        # convert to HSV and calculate saturation average
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        sat_avg = np.average(s)
        log_print("Saturation (HSV) avg:  {}".format(sat_avg))
        results.append(sat_avg)
    
    return results

def sharpness(raw_frames):
    results = []
    for frame in raw_frames: 
        # convert to grayscale and calculate lapacian variance
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(f, cv2.CV_64F).var()
        log_print("Laplacian variance:  {}".format(variance))
        results.append(variance)
    
    return results

# didn't finish yet lol
def white_balance(raw_frames):
    return raw_frames

def get_frames(device, cap, prop, ctrl):
    frames = []
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    for c in ctrl:
        log_print("{}:            {:<5}".format(prop, str(c)))
        subprocess.call(['{} -c {}={}'.format(device, prop, str(c))], shell=True)
        t_end = time.time() + 3
        while True:
            ret, frame = cap.read()
            if time.time() > t_end and ret is True:
                # white balance still in progress
                if prop == "white_balance_temperature":
                    frames.append(c)
                else:
                    frames.append(frame)
                break

    log_print("\n")
    return frames

def eval_cam(prop):
    global log_file
    global result

    # create directory for log and .png files if it doesn't already exist
    if device_name == "Jabra PanaCast 20":
        log_name = "p20"
    elif device_name == "Jabra PanaCast 50":
        log_name = "p50"

    # create log file for the current cam prop
    filename = "{}_{}_{}.log".format(current, prop, log_name)
    file_path = os.path.join(path+"/CamPropControls", filename)
    # create directory for log files if it doesn't already exist
    if not os.path.exists(path+"/CamPropControls"):
        os.makedirs(path+"/CamPropControls")
    log_file = open(file_path, "a")

    # set up camera stream
    if not get_device():
        log_print("Device not found, please check if it is attached.")
        sys.exit(0)

    # iterate thru cam_props dict and test each value of each cam prop
    timestamp = datetime.now()
    log_print(55*"=")
    log_print("\n{}\n".format(timestamp))
    
    ctrl = cam_props[prop]
    basic = {}
    cap.open(device_num)

    # set auto wb off before starting
    if prop == "white_balance_temperature":
        subprocess.call(['{} -c white_balance_temperature_auto=0'.format(device)], shell=True)

    for c in ctrl:
        basic[c] = get_set(device, prop, c)
    log_print("\n")
    
    raw_frames = get_frames(device, cap, prop, ctrl)
    if prop == "brightness":
        values = brightness(raw_frames)
        result = eval_results(ctrl, values)
    elif prop == "contrast":
        values = contrast(raw_frames)
        result = eval_results(ctrl, values)
    elif prop == "saturation":
        values = saturation(raw_frames)
        result = eval_results(ctrl, values)
    elif prop == "sharpness":
        values = sharpness(raw_frames)
        result = eval_results(ctrl, values)
    elif prop == "white_balance_temperature":
        values = white_balance(raw_frames)
        result = eval_results(ctrl, values)

    log_print("\nGenerating report...\n")
    log_print("Exiting {} test now...\n".format(prop))
 
    log_file.close()
    cap.release()

def result_should_be(expected):
    if result != int(expected):
        raise AssertionError("{} != {}".format(result, expected))

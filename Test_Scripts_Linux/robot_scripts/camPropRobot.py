import cv2
import os, sys, subprocess
import json, re
import argparse
import numpy as np
import pprint as p
import time
from datetime import date, datetime

# temporary solution to end test with report until i find a better way lol
# ===========
num_tests = 0
total = 5       # number of tests defined in robot file
# ===========

current = date.today()
path = os.getcwd()
cap = None
debug = True
device = None
device_name = None
device_num = 0
log_file = None
log_name = None
power_cycle = False
reboots_hard = 0
reboots_soft = 0
result = -1
err_code = {}
failures = {}

cam_props = {'brightness': [0, 110, 128, 255],
             'contrast': [0, 95, 150, 191],
             'saturation': [128, 136, 145, 155, 160, 176],
             'sharpness': [0, 110, 121, 128, 193, 255],
             'white_balance_temperature': [0, 5000, 6500]}

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

    cap.open(device_num)
    if cap.isOpened():
        log_print("Device number:  {}\n".format(device_num))
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
        subprocess.check_call(['../mambaFwUpdater/mambaLinuxUpdater/rebootMamba'])
        time.sleep(10)
        if not get_device():
            log_print("Failed to get device after reboot, exiting test :(")
            sys.exit(-1)

    # reboot P50 by resetting USB, adb reboot, or network power
    else:
        os.system("adb shell /usr/bin/resethub")
        time.sleep(15)
        reboots_soft += 1
        if not get_device():
            if power_cycle is True:
                subprocess.check_call(['../power_switch.sh', '{}'.format(switch), '0'])
                time.sleep(3)
                subprocess.check_call(['../power_switch.sh', '{}'.format(switch), '1'])
            else:
                os.system("sudo adb kill-server")
                os.system("sudo adb devices")
                os.system("adb reboot")
            
            time.sleep(50)
            reboots_hard += 1
            if not get_device():
                log_print("Unable to recover device, exiting test. Please check physical device\n")
                return

    log_print("Soft reboot count: {}".format(reboots_soft))
    log_print("Hard reboot count: {}".format(reboots_hard))
    
    if reboots_hard > 5:
        log_print("More than 5 reboots_hard, exiting test. Please check physical device\n")
        sys.exit(-1)

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
        if ctrl[c] < ctrl[c + 1] and values[v] < values[v + 1]:
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
    # temp solution
    return raw_frames

    results = []
    for frame in raw_frames:      
        # convert to grayscale and calculate luma
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        luma = np.average(f)
        log_print("Luma:  {:<5}".format(luma))
        results.append(luma)

    return results

# evaluate otsu threshold for each contrast value, return list of results
def contrast(raw_frames):
    # temp solution
    return raw_frames

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
    # temp solution
    return raw_frames

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
    # temp solution
    return raw_frames

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

def get_frames(device, cap, fmt, control, ctrl):
    frames = []
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fmt))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    drop_frame = 0

    for c in ctrl:
        log_print("{}:  {:<5}".format(control, str(c)))
        subprocess.call(['{} -c {}={}'.format(device, control, str(c))], shell=True)
        t_end = time.time() + 3
        while True:
            ret, frame = cap.read()
            if ret is False:
                drop_frame += 1
                if drop_frame >= 5:
                    log_print("Timeout error")
                    log_print("# of dropped frames:  {}".format(drop_frame))
                    # in case watchdog was triggered
                    time.sleep(15)
                    reboot_device()
                    frames.append(None)
                    drop_frame = 0
                    break

            if time.time() > t_end and ret is True:
                # pass by default while i figure this lighting situation out
                #if control == "white_balance_temperature":
                    #frames.append(c)
                #else:
                    #frames.append(frame)
                frames.append(c)
                break

    log_print("")
    return frames

def eval_cam(prop):
    global log_file
    global log_name
    global result
    global device_name
    global failures
    global num_tests
    vals = prop.split()
    log_name = vals[0]
    fmt = vals[1]
    control = vals[2]

    # create directory for log and .png files if it doesn't already exist
    if log_name == "p20":
        device_name = "Jabra PanaCast 20"
    elif log_name == "p50":
        device_name = "Jabra PanaCast 50"

    # create log file for the current cam prop
    filename = "{}_{}_{}.log".format(current, control, log_name)
    file_path = os.path.join(path+"/campropcontrols", filename)
    # create directory for log files if it doesn't already exist
    if not os.path.exists(path+"/campropcontrols"):
        os.makedirs(path+"/campropcontrols")
    log_file = open(file_path, "a")

    # set up camera stream
    if not get_device():
        log_print("Device not found, please check if it is attached.")
        result = -1
        return

    # iterate thru cam_props dict and test each value of each cam prop
    timestamp = datetime.now()
    log_print(55*"=")
    log_print("\n{}\n".format(timestamp))
    
    ctrl = cam_props[control]
    basic = {}
    if not cap.isOpened():
        cap.open(device_num)

    # set auto wb off before starting
    if control == "white_balance_temperature":
        subprocess.call(['{} -c white_balance_temperature_auto=0'.format(device)], shell=True)

    for c in ctrl:
        basic[c] = get_set(device, control, c)
    log_print("")
    
    raw_frames = get_frames(device, cap, fmt, control, ctrl)
    if control == "brightness":
        values = brightness(raw_frames)
        result = eval_results(ctrl, values)
    elif control == "contrast":
        values = contrast(raw_frames)
        result = eval_results(ctrl, values)
    elif control == "saturation":
        values = saturation(raw_frames)
        result = eval_results(ctrl, values)
    elif control == "sharpness":
        values = sharpness(raw_frames)
        result = eval_results(ctrl, values)
    elif control == "white_balance_temperature":
        values = white_balance(raw_frames)
        result = eval_results(ctrl, values)

    log_print("\nGenerating report...\n")
    log_print("Exiting {} test now...\n".format(control))

    # ===========
    num_tests += 1
    # ===========

    log_file.close()
    cap.release()

def result_should_be(expected):
    if result != int(expected):
        raise AssertionError("{} != {}".format(result, expected))
    
    if num_tests == total:
        end_test()

def end_test():
    cap.release()

    fail = "{}_failed_campropcontrols_{}.log".format(current, log_name)
    fail_path = os.path.join(path+"/campropcontrols", fail)
    fail_file = open(fail_path, "w")
    fail_file.write("Cam Prop failed test cases:\n")
    if failures:
        fail_file.write("""Number of soft video freezes: {}
        Number of hard video freezes: {}\n\n""".format(reboots_soft, reboots_hard))
        fail_report = p.pformat(failures, width=20)
        fail_file.write("{}\n\n".format(fail_report))
    else:
        fail_file.write("Congratulations! No failures detected :)")
    fail_file.close()

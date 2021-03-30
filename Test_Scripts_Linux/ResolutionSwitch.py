import numpy as np
import cv2
import time
import os
import subprocess
import argparse
import json
import re
import pprint as p
from datetime import date, datetime

ap = argparse.ArgumentParser()
ap.add_argument("-d","--debug", type=bool, default=False, help="Set to True to disable msgs to terminal")
ap.add_argument("-f","--frame", type=bool, default=False, help="Set to True to enable live view")
ap.add_argument("-p","--power", type=bool, default=False, help="Set to true when running on the Jenkins server")
ap.add_argument("-t","--test", type=str, default="res_switch.json", help="Specify .json file to load test cases")
ap.add_argument("-v","--video", type=str, default="Jabra PanaCast 50", help="Specify which camera to test")
args = vars(ap.parse_args())
debug = args["debug"]
live_view = args["frame"]
test_file = args["test"]
power_cycle = args["power"]
device_name = args["video"]

input_tests = open(test_file)
json_str = input_tests.read()
test_cases = json.loads(json_str)

global cap
global reboots
current = date.today()
path = os.getcwd()
device_num = 0
reboots = 0
err_code = {}

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

filename = "{}_resolutionswitch.log".format(current)
file_path = os.path.join(path+"/resolutionswitch", filename)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"/resolutionswitch"):
    os.makedirs(path+"/resolutionswitch")

log_file = open(file_path, "a")
timestamp = datetime.now()
log_print(55*"=")
log_print("\n{}\n".format(timestamp))

def reboot_device():
    print("Panacast device error")
    if power_cycle is True:
        subprocess.check_call(['./power_switch.sh', '0', '0'])
        time.sleep(3)
        subprocess.check_call(['./power_switch.sh', '0', '1'])
    else:
        os.system("sudo adb kill-server")
        os.system("sudo adb devices")
        os.system("adb reboot")

    print("Rebooting...")
    time.sleep(55)
    global device_num
    global reboots
    reboots += 1

    # grab reenumerated device
    while True:       
        device = subprocess.check_output('v4l2-ctl --list-devices 2>/dev/null | grep "{}" -A 1 | grep video'.format(device_name), shell=True)
        device = device.decode("utf-8")
        device_num = int(re.search(r'\d+', device).group())
        cap = cv2.VideoCapture(device_num)
        if cap.isOpened():
            log_print("Device back online:  {}\n".format(device_num))
            break
        else:
            time.sleep(5)

def test_fps(width, height, target_res, frame_count):
    start_frame, test_frame, total_frame, drop_frame = (0 for x in range(4))
    all_fps = []
    global err_code
    # set initial resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    retval, frame = cap.read()
    switch_start = time.time()

    for target in target_res:
        if target[0] == width and target[1] == height:
            continue
        else:
            test_type = "{}x{} -> {}x{}".format(width, height, target[0], target[1])
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, target[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target[1])
            # check when frame is available to grab after switching resolutions
            while True:
                retval, frame = cap.read()
                w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                if retval is True and w == target[0] and h == target[1]:
                    switch_end = time.time()
                    switch_time = switch_end - switch_start
                    break

        log_print(55*"=")
        log_print(test_type)
        log_print("Time to switch (ms):   {}\n".format(switch_time * 1000))
        test_start, test_time = (time.time() for x in range(2))
        # grab frames for 30 seconds (900 frames)
        for i in range(0, frame_count):
            retval, frame = cap.read()
            if retval is False:
                drop_frame += 1
                log_print("Frame #{} dropped!".format(drop_frame))
                if time.time() > test_start + 30:
                    log_print("Timeout error")
                    reboot_device()
            else:
                test_frame += 1
                if live_view is True:
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            
            # check framerate every five seconds
            if test_frame % 150 == 0:
                test_end = time.time()
                current = test_end - test_time
                time_elapsed = test_end - test_start
                log_print("Test duration (sec):   {:>2}".format(time_elapsed))
                log_print("Total frames grabbed:  {:<5}".format(test_frame))

                fps = float(test_frame / current)
                log_print("Current average fps:   {:<5}\n".format(fps))
                all_fps.append(fps)
                test_time = time.time()
                test_frame = 0
        
        # write pass/fail report to dict
        avg_fps = sum(all_fps) / len(all_fps)
        if switch_time < 1.4:
            if avg_fps >= 29:
                err_code[test_type] = 1
            elif avg_fps < 29 and avg_fps >= 27:
                err_code[test_type] = 0
            else:
                err_code[test_type] = -1
        else:
            err_code[test_type] = -1

        # reset to starting resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        switch_start = time.time()

if __name__ == "__main__":
    # set up camera stream        
    device = subprocess.check_output('v4l2-ctl --list-devices 2>/dev/null | grep "{}" -A 1 | grep video'.format(device_name), shell=True)
    device = device.decode("utf-8")
    device_num = int(re.search(r'\d+', device).group())
    cap = cv2.VideoCapture(device_num)

    if device_num is None:
        log_print("PanaCast device not found. Please make sure the device is properly connected and try again")
        sys.exit(1)
    if cap.isOpened():
        log_print("PanaCast device found:  {}\n".format(device_num))
    # cylce through all test cases provided by json file
    frame_count = 900
    for fmt in test_cases:
        codec = test_cases[fmt]
        start_res = codec['start']
        target_res = codec['target']
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fmt))
        for start in start_res:
            width = start[0]
            height = start[1]
            test_fps(width, height, target_res, frame_count)
    
    log_print("\nGenerating report...")
    log_print("Number of video crashes/freezes (that required reboots): {}".format(reboots))
    report = p.pformat(err_code)
    log_print("{}\n".format(report))
    log_file.close()

    cap.release()
    cv2.destroyAllWindows()

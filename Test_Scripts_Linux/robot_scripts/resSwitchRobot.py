import numpy as np
import cv2
import time
import os
import sys
import subprocess
import argparse
import json
import re
import pprint as p
from datetime import date, datetime

# temporary solution to end test with report until i find a better way lol
# ===========
num_tests = 0
total = 48 # number of tests defined in robot file
# ===========

current = date.today()
path = os.getcwd()
cap = None
debug = True
device_name = "Jabra PanaCast 50"
device_num = 0
log_file = None
log_name = None
power_cycle = False
reboots_hard = 0
reboots_soft = 0
result = -1
failures = {}

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

def report_results(results):
    log_print("\nGenerating report...")
    log_print("Number of soft video freezes: {}".format(reboots_soft))
    log_print("Number of hard video freezes: {}".format(reboots_hard))
    report = p.pformat(results, width=20)
    log_print("{}\n".format(report))
    log_file.close()

    fail = -1
    if fail in results.values():
        return -1
    else:
        return 1

def get_device():
    global cap
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
        log_print("Device online:  {}\n".format(device_num))
        return True
    else:
        return False

def reboot_device(fmt, codec):
    global device_num
    global reboots_hard
    global reboots_soft
    switch = 0

    log_print("Rebooting...")
    if fmt == "MJPG":
        switch = 1
    # reboot by resetting USB if testing P20
    if device_name == "Jabra PanaCast 20":
        subprocess.check_call(['./mambaFwUpdater/mambaLinuxUpdater/rebootMamba'])
        time.sleep(10)
        reboots_hard += 1
        if not get_device():
            log_print("Failed to get device after reboot, exiting test :(")
            sys.exit(0)
    # reboot P50 by resetting USB, adb reboot, or network power
    else:
        if fmt == codec:
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
            if not get_device():
                log_print("Unable to recover device, exiting test. Please check physical device\n")
                report_results()
                return
                
    log_print("Soft reboot count: {}".format(reboots_soft))
    log_print("Hard reboot count: {}".format(reboots_hard))

    if reboots_hard > 5:
        log_print("More than 5 reboots_hard, exiting test. Please check physical device\n")
        report_results()
        sys.exit(0)

def check_frame(check_width, check_height, fmt, codec):
    check_start = time.time()
    retval = False
    frame = None
    while True:
        try:
            retval, frame = cap.read()
        except:
            log_print("failed to grab frames")
            reboot_device(fmt, codec)
            continue
        
        # check if frame is successfully grabbed
        if retval is not False or frame is not None:
            h, w = frame.shape[:2]
            if w == check_width and h == check_height:
                return True
        else:
            # if device isn't sending frames, try rebooting
            check_current = time.time()
            if check_current - check_start > 5:
                return False
            continue


def test_fps(fmt, s_w, s_h, t_w, t_h, s_fps, t_fps):
    start_frame, test_frame, total_frame, drop_frame = (0 for x in range(4))
    all_fps = []
    global cap
    global err_code

    # convert video codec number to format and check if set correctly
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fmt))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

    if codec != fmt:
        log_print("Unable to set video format to {}.".format(fmt))
        reboot_device(fmt, codec)
        return -1
    else:
        log_print("Video format set to:   {} ({})".format(codec, fourcc))

    # set start res/fps
    cap.set(cv2.CAP_PROP_FPS, s_fps)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, s_w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, s_h)
    # print("set start")
    
    # set target res/fps
    cap.set(cv2.CAP_PROP_FPS, t_fps)
    switch_start = time.time()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, t_w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, t_h)
    # print("set target")

    # calculate switch time
    if check_frame(t_w, t_h, fmt, codec):
        switch_end = time.time()
    else:
        log_print("Unable to switch resolution")
        reboot_device(fmt, codec)
        return -1

    switch_time = switch_end - switch_start

    # log_print("Time to switch (ms):   {}\n".format(switch_time * 1000))
    test_start, test_time = (time.time() for x in range(2))
    
    # grab frames for 25 seconds
    # frame_count = 3
    frame_count = t_fps * 25
    for i in range(0, frame_count):
        retval, frame = cap.read()
        # reboot device in event of frame drop/error
        if retval is False:
            drop_frame += 1
            if drop_frame >= 5:
                log_print("Timeout error")
                log_print("# of dropped frames: {}".format(drop_frame))
                # in case watchdog was triggered
                time.sleep(15)
                reboot_device(fmt, codec)
                drop_frame = 0
                return -1   
        else:
            test_frame += 1

        # check framerate every five seconds
        if test_frame % (frame_count / 5) == 0:
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
    try:
        avg_fps = sum(all_fps) / len(all_fps)
    except:
        avg_fps = 0
    # if switch_time * 1000 < 1500:
    if avg_fps >= t_fps - 1:
        log_print("PASS\n")
        return 1
    elif avg_fps < t_fps - 2 and avg_fps >= t_fps - 3:
        log_print("SOFT FAIL\n")
        return 0
    else:
        log_print("HARD FAIL\n")
        return -1
    # else:
    #     err_code[test_type] = -1
    #     log_print("HARD FAIL\n")

    all_fps.clear()
    # time.sleep(1)

def eval_switch(prop):
    global device_name
    global log_file
    global log_name
    global result
    global failures
    global num_tests
    err_code = {}
    vals = prop.split()
    log_name = vals[0]
    fmt = vals[1]
    start_res = vals[2].split('x')
    target_res = vals[3].split('x')
    start_fps = int(vals[4])
    target_fps = int(vals[5])
    
    # create directory for log and .png files if it doesn't already exist
    if log_name == "p20":
        device_name = "Jabra PanaCast 20"
    elif log_name == "p50":
        device_name = "Jabra PanaCast 50"

    # create log file for current res switch test
    filename = "{}_{}p_{}.log".format(current, start_res[1], log_name)
    file_path = os.path.join(path+"/resolutionswitch", filename)

    if not os.path.exists(path+"/resolutionswitch"):
        os.makedirs(path+"/resolutionswitch")
    log_file = open(file_path, "a")

    timestamp = datetime.now()
    log_print(55*"=")
    log_print("\n{}\n".format(timestamp))

    # set up camera stream
    if not get_device():
        log_print("Device not found, please check if it is attached.")
        result = -1
        return

    # cycle through all test cases provided by json file
    if not cap.isOpened():
        cap.open(device_num)
    start_w = int(start_res[0])
    start_h = int(start_res[1])
    target_w = int(target_res[0])
    target_h = int(target_res[1])
    
    test_type = "{} {}x{} [{} fps] -> {}x{} [{} fps]".format(fmt, start_w, start_h, start_fps, target_w, target_h, target_fps)
    log_print(55*"=")
    log_print("{}\n".format(test_type))
    err_code[test_type] = test_fps(fmt, start_w, start_h, target_w, target_h, start_fps, target_fps)
    if err_code.get(test_type) == -1:
        failures[test_type] = -1
    
    result = report_results(err_code)

    # ===========
    num_tests += 1
    # ===========

def result_should_be(expected):
    if result != int(expected):
        raise AssertionError("{} != {}".format(result, expected))
    
    if num_tests == total:
        end_test()

def end_test():
    cap.release()

    fail = "{}_failed_resolutionswitch_{}.log".format(current, log_name)
    fail_path = os.path.join(path+"/resolutionswitch", fail)
    fail_file = open(fail_path, "w")
    fail_file.write("Resolution Switch failed test cases:")
    if failures:
        fail_file.write("""Number of soft video freezes: {}
        Number of hard video freezes: {}\n\n""".format(reboots_soft, reboots_hard))
        fail_report = p.pformat(failures, width=20)
        fail_file.write("{}\n\n".format(fail_report))
    else:
        fail_file.write("Congratulations! No failures detected :)")
    fail_file.close()

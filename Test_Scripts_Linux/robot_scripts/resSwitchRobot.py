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

current = date.today()
path = os.getcwd()
cap = None
debug = True
device_name = "Jabra PanaCast 50"
device_num = 0
log_file = None
power_cycle = False
reboots_hard = 0
reboots_soft = 0
err_code = {}
result = -1

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

def report_results():
    log_print("\nGenerating report...")
    log_print("Number of soft video freezes: {}".format(reboots_soft))
    log_print("Number of hard video freezes: {}".format(reboots_hard))
    report = p.pformat(err_code, width=20)
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

    if cap.isOpened():
        log_print("Device back online:  {}\n".format(device_num))
        cap.open(device_num)
        return True
    else:
        return False

def reboot_device(fmt):
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
                report_results()
                sys.exit(0)

    if reboots_hard > 5:
        log_print("More than 5 reboots_hard, exiting test. Please check physical device\n")
        report_results()
        sys.exit(0)

def check_frame(check_width, check_height, fmt):
    check_start = time.time()
    retval = False
    frame = None
    while True:
        try:
            retval, frame = cap.read()
        except:
            log_print("failed to grab frames")
            reboot_device(fmt)
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
    global failures

    test_type = "{} {}x{} [{} fps] -> {}x{} [{} fps]".format(fmt, s_w, s_h, t_w, t_h, s_fps, t_fps)
    log_print(55*"=")
    log_print("{}\n".format(test_type))

    # convert video codec number to format and check if set correctly
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fmt))
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])

    if codec != fmt:
        log_print("Unable to set video format to {}.".format(fmt))
        reboot_device(fmt)
        err_code[test_type] = -1
        continue
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
    if check_frame(t_w, t_h, fmt):
        switch_end = time.time()
    else:
        log_print("Unable to switch resolution")
        err_code[test_type] = -1
        reboot_device(fmt)
        continue

    switch_time = switch_end - switch_start

    # log_print("Time to switch (ms):   {}\n".format(switch_time * 1000))
    test_start, test_time = (time.time() for x in range(2))
    
    # grab frames for 30 seconds
    # frame_count = 3
    frame_count = t_fps * 30
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
                reboot_device(fmt)
                err_code[test_type] = -1
                drop_frame = 0
                return     
        else:
            test_frame += 1

        # check framerate every five seconds
        if test_frame % (frame_count / 6) == 0:
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
        err_code[test_type] = 1
        log_print("PASS\n")
    elif avg_fps < t_fps - 1 and avg_fps >= t_fps - 3:
        err_code[test_type] = 0
        log_print("SOFT FAIL\n")
    else:
        err_code[test_type] = -1
        log_print("HARD FAIL\n")
    # else:
    #     err_code[test_type] = -1
    #     log_print("HARD FAIL\n")

    all_fps.clear()
    # time.sleep(1)

def eval_switch(prop):
    global log_file
    global result
    vals = prop.split()
    fmt = vals[0]
    start_res = vals[1].split('x')
    target_res = vals[2].split('x')
    start_fps = int(vals[3])
    target_fps = int(vals[4])
    
    # create directory for log and .png files if it doesn't already exist
    if device_name == "Jabra PanaCast 20":
        log_name = "p20"
    elif device_name == "Jabra PanaCast 50":
        log_name = "p50"

    # create log file for current res switch test
    filename = "{}_{}p-{}p_{}.log".format(current, start_res[1], target_res[1], log_name)
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
        sys.exit(0)

    # cycle through all test cases provided by json file
    cap.open(device_num)
    start_w = int(start_res[0])
    start_h = int(start_res[1])
    target_w = int(target_res[0])
    target_h = int(target_res[1])
    test_fps(fmt, start_w, start_h, target_w, target_h, start_fps, target_fps)
    
    report_results()
    cap.release()
    cv2.destroyAllWindows()

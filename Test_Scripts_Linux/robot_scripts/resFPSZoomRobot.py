import os
import time
import platform
import numpy as np
import sys
import cv2
from queue import Queue
from datetime import date, datetime
import pprint as p
import json
import subprocess
import argparse
import re

current = date.today()
path = os.getcwd()
cap = None
debug = True
device = None
device_name = None
device_num = 0
log_file = None
power_cycle = False
reboots_hard = 0
reboots_soft = 0
result = -1
zoom_file = "config/zoom.json"

input_zooms = open(zoom_file)
json_str = input_zooms.read()
zoom_levels = json.loads(json_str)

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
            reboots_soft += 1
            time.sleep(20)
        if not get_device():
            if power_cycle is True:
                subprocess.check_call(['./power_switch.sh', '{}'.format(switch), '0'])
                time.sleep(3)
                subprocess.check_call(['./power_switch.sh', '{}'.format(switch), '1'])
            else:
                os.system("sudo adb kill-server")
                os.system("sudo adb devices")
                os.system("adb reboot")
            
            time.sleep(55)
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

def test_fps(fmt, x, y, framerate, zoom):
    global device_num
    
    # set video format
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fmt))
    # convert video codec number to format and check if set correctly
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
    log_print("Video format set to:    {} ({})".format(codec, fourcc))
    # make sure format is set correctly
    if codec != fmt:
        log_print("Unable to set video format correctly.")
        reboot_device(fmt, codec)
        return -1

    # set resolution and check if set correctly
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, x)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, y)    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    log_print("Resolution set to:      {} x {}".format(width, height))

    # set zoom level
    # device = 'v4l2-ctl -d /dev/video{}'.format(device_num)
    log_print("Setting zoom level to:  {}".format(zoom))
    subprocess.call(['{} -c zoom_absolute={}'.format(device, str(zoom))], shell=True)

    # set the fps
    log_print("Setting framerate to:   {}".format(framerate))
    cap.set(cv2.CAP_PROP_FPS, framerate)
    current_fps = cap.get(cv2.CAP_PROP_FPS)
    log_print("Current framerate:      {}\n".format(current_fps))

    # check if device is responding to get/set commands and try rebooting if it isn't
    if width == 0 and height == 0 and current_fps == 0:
        log_print("Device not responding to get/set commands")
        reboot_device(fmt, codec)

    # set number of frames to be counted
    frames = framerate*20
    prev_frame = 0
    fps_list, jitters = ([] for x in range(2))
    drops, count, initial_frames, initial_elapsed = (0 for x in range(4))

    # calculate fps
    start = time.time()
    # default initial value
    initial_elapsed = 30
    for i in range(0, frames):
        try:
            retval, frame = cap.read()
            current_frame = cap.get(cv2.CAP_PROP_POS_MSEC)
            if prev_frame == 0:
                prev_frame = current_frame
            diff = current_frame - prev_frame
            prev_frame = current_frame
            # save jitter between current and previous frame to average later
            jitters.append(abs(diff - (1000/framerate)))

            if retval is False:
                drops += 1
                if drops >= 5:
                    log_print("# of dropped frames: {}".format(drops))
                    raise cv2.error("Timeout error")
                continue
            else:
                count += 1
            # 2/3 frames - 1 to get the first 20 seconds
            if i == (((frames * 2) / 3) - 1):
                initial_frames = count
                initial_end = time.time()
                initial_elapsed = initial_end - start

        except cv2.error as e:
            log_print("{}".format(e))
            reboot_device(fmt, codec)
            log_print("FREEZE FAIL\n")
            return -1
    
    end = time.time()
    total_elapsed = end - start
    elapsed = total_elapsed - initial_elapsed
    actual_frames = count
    avg_jitter = sum(jitters) / len(jitters)

    log_print("Test duration (s):      {:<5}".format(total_elapsed))
    log_print("Total frames grabbed:   {:<5}".format(count))
    log_print("Total frames dropped:   {:<5}".format(drops))
    log_print("Average jitter (ms):    {:<5}".format(avg_jitter))

    initial_fps = float(initial_frames / initial_elapsed)
    fps_list.append(initial_fps)
    log_print("Initial average fps:    {:<5}".format(initial_fps))

    fps = float((actual_frames-initial_frames) / elapsed)
    fps_list.append(fps)
    log_print("Actual average fps:     {:<5}\n".format(fps))
    
    diff = abs(float(framerate) - float(fps_list[1]))
        
    # success
    if diff <= 1:
        log_print("PASS\n")
        return 1
    # soft failure
    elif diff <= 3 and diff > 1:
        log_print("SOFT FAIL\n")
        return 0
    # hard failure
    else:
        log_print("HARD FAIL\n")
        return -1

def eval_res(prop):
    global device_name
    global log_file
    global result
    err_code = {}
    vals = prop.split()
    log_name = vals[0]
    fmt = vals[1]
    x = int(vals[2])
    y = int(vals[3])
    fps = int(vals[4])
    type = "raw"

    # create directory for log and .png files if it doesn't already exist
    if log_name == "p20":
        device_name = "Jabra PanaCast 20"
    elif log_name == "p50":
        device_name = "Jabra PanaCast 50"
    
    if fmt == "NV12" or fmt == "YUYV":
        type = "raw"
    elif fmt == "MJPG":
        type = "mjpg"

    # create log file for current res fps zoom
    filename = "{}_{}p_{}-{}.log".format(current, y, log_name, type)
    log_path = os.path.join(path+"/resolutionfps", filename)

    # create directory for log files if it already doesn't exist
    if not os.path.exists(path+"/resolutionfps"):
        os.makedirs(path+"/resolutionfps")
    log_file = open(log_path, "a")

    # set up camera stream
    if not get_device():
        log_print("Device not found, please check if it is attached")
        result = -1
        return
    
    timestamp = datetime.now()
    log_print(55*"=")
    log_print("\n{}\n".format(timestamp))

    cap.open(device_num)
    log_print(55*"=")
    log_print("Parameters: {} {}p {}fps".format(fmt, y, fps))
    
    for z in zoom_levels["ZOOM"]:
        log_print(55*"=")
        log_print("Testing: {} {}p {}fps zoom {}\n".format(fmt, y, fps, z))
        test_type = "{} {}p {}fps zoom {}".format(fmt, y, fps, z)
        err_code[test_type] = test_fps(fmt, x, y, fps, z)

    result = report_results(err_code)
    cap.release()

def result_should_be(expected):
    if result != int(expected):
        raise AssertionError("{} != {}".format(result, expected))

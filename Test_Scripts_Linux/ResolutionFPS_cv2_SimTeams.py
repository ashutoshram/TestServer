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
import random
import math

ap = argparse.ArgumentParser()
ap.add_argument("-d","--debug", type=bool, default=True, help="Set to True to disable msgs to terminal")
ap.add_argument("-f","--frame", type=bool, default=True, help="Set to True to enable live view")
ap.add_argument("-p","--power", type=bool, default=False, help="Set to true when running on the Jenkins server")
ap.add_argument("-t","--test", type=str, default="res_fps_p50.json", help="Specify .json file to load test cases")
ap.add_argument("-v","--video", type=str, default="Jabra PanaCast 50", help="Specify which camera to test")
ap.add_argument("-z","--zoom", type=str, default="zoom.json", help="Specify .json file to load zoom values")
ap.add_argument("-P","--pan", type=str, default="pan.json", help="Specify .json file to load pan values")
ap.add_argument("-T","--tilt", type=str, default="tilt.json", help="Specify .json file to load tilt values")
args = vars(ap.parse_args())
debug = args["debug"]
live_view = args["frame"]
test_file = "config/" + args["test"]
zoom_file = "config/" + args["zoom"]
pan_file = "config/" + args["pan"]
tilt_file = "config/" + args["tilt"]
power_cycle = args["power"]
device_name = args["video"]

input_tests = open(test_file)
json_str = input_tests.read()
test_cases = json.loads(json_str)

input_zooms = open(zoom_file)
json_str = input_zooms.read()
zoom_levels = json.loads(json_str)
zoom_levels = zoom_levels["ZOOM"]

input_pan = open(pan_file)
json_str = input_pan.read()
pan_levels = json.loads(json_str)
pan_levels = pan_levels["PAN"]

input_tilt = open(tilt_file)
json_str = input_tilt.read()
tilt_levels = json.loads(json_str)
tilt_levels = tilt_levels["TILT"]

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

    fail_file.write("""ResolutionFPS test cases that resulted in soft failures or hard failures. Please refer to resolutionfps.log for more details on each case.
    [-1] denotes hard failure (large fps dip or freeze)
    [0] denotes soft failure (small fps dip)
    Number of soft video freezes: {}
    Number of hard video freezes: {}\n\n""".format(reboots_soft, reboots_hard))
    fail_report = p.pformat(failures, width=20)
    fail_file.write("{}\n\n".format(fail_report))
    fail_file.close()

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
        log_print("Device number:  {}\n".format(device_num))
        cap.open(device_num)
        return True
    else:
        return False

def reboot_device(fmt, codec):
    global device_num
    global reboots_hard
    global reboots_soft
    global reboots_temp
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
        if fmt == codec and reboots_temp <= 2:
            os.system("adb shell /usr/bin/resethub")
            reboots_soft += 1
            reboots_temp += 1
            time.sleep(20)
        if not get_device():
            if power_cycle is True:
                subprocess.check_call(['./power_switch.sh', '{}'.format(switch), '0'])
                time.sleep(3)
                subprocess.check_call(['./power_switch.sh', '{}'.format(switch), '1'])
            else:
                os.system("adb devices")
                os.system("sudo adb kill-server")
                os.system("sudo adb devices")
                os.system("adb reboot")

            time.sleep(55)
            reboots_hard += 1
            reboots_temp = 0
            if not get_device():
                log_print("Unable to recover device, exiting test. Please check physical device\n")
                report_results()
                sys.exit(0)


    log_print("Soft reboot count: {}".format(reboots_soft))
    log_print("Hard reboot count: {}".format(reboots_hard))
    if reboots_hard > 5:
        log_print("More than 5 reboots_hard, exiting test. Please check physical device\n")
        report_results()
        sys.exit(0)

def test_fps(fmt, resolution, framerate):
    # check if camera stream exists
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
        print("Unable to set video format correctly.")
        # reboot_device(fmt, codec)
        return -1

    # set resolution and check if set correctly
    if resolution == '4k':
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    elif resolution == '1200p':
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4800)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
    elif resolution == '1080p':
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    elif resolution == '720p':
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    elif resolution == '540p':
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    elif resolution == '360p':
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    log_print("Resolution set to:      {} x {}".format(width, height))

    max_ptz_per_res = 5
    min_ptz_per_res = 0
    ptz_per_res = random.randint(min_ptz_per_res, max_ptz_per_res)
    ptz_counter = 0
    zoom_val = random.sample(zoom_levels, k = 1)[0]
    pan_val = random.sample(pan_levels, k = 1)[0]
    tilt_val = random.sample(tilt_levels, k = 1)[0]

    # set zoom level
    device = 'v4l2-ctl -d /dev/video{}'.format(device_num)
    log_print("Setting zoom level to:  {}".format(zoom_val))
    subprocess.call(['{} -c zoom_absolute={}'.format(device, str(zoom_val))], shell=True)
    log_print("Setting pan level to:   {}".format(pan_val))
    subprocess.call(['{} -c pan_absolute={}'.format(device, str(pan_val))], shell=True)
    log_print("Setting tilt level to:  {}".format(tilt_val))
    subprocess.call(['{} -c tilt_absolute={}'.format(device, str(tilt_val))], shell=True)
    log_print('')

    # open opencv capture device and set the fps
    log_print("Setting framerate to:   {}".format(framerate))
    cap.set(cv2.CAP_PROP_FPS, framerate)
    current_fps = cap.get(cv2.CAP_PROP_FPS)
    log_print("Current framerate:      {}\n".format(current_fps))

    # check if device is responding to get/set commands and try rebooting if it isn't
    if width == 0 and height == 0 and current_fps == 0:
        log_print("Device not responding to get/set commands")
        print("Device not responding to get/set commands")
        # reboot_device(fmt, codec)

    # set number of frames to be counted
    frames = math.ceil(framerate*(random.random())*0.2)+1
    prev_frame = 0
    fps_list, jitters = ([] for x in range(2))
    drops, count, initial_frames, initial_elapsed = (0 for x in range(4))

    # calculate fps
    start = time.time()
    # default initial value
    initial_elapsed = 30
    frames = max(frames, ptz_per_res-1)
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
                if live_view is True:
                    # switch channels for correct color output
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                count += 1
            # 2/3 frames - 1 to get the first 20 seconds
            if i == (((frames * 2) / 3) - 1):
                initial_frames = count
                initial_end = time.time()
                initial_elapsed = initial_end - start

            zoom_val = random.sample(zoom_levels, k = 1)[0]
            pan_val = random.sample(pan_levels, k = 1)[0]
            tilt_val = random.sample(tilt_levels, k = 1)[0]

            # set zoom level
            log_print("Setting zoom level to:  {}".format(zoom_val))
            subprocess.call(['{} -c zoom_absolute={}'.format(device, str(zoom_val))], shell=True)
            log_print("Setting pan level to:   {}".format(pan_val))
            subprocess.call(['{} -c pan_absolute={}'.format(device, str(pan_val))], shell=True)
            log_print("Setting tilt level to:  {}".format(tilt_val))
            subprocess.call(['{} -c tilt_absolute={}'.format(device, str(tilt_val))], shell=True)
            log_print('')

        except cv2.error as e:
            log_print("{}".format(e))
            # reboot_device(fmt, codec)
            log_print("FREEZE FAIL\n")
            print("FREEZE FAIL\n")
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

    diff = (float(framerate) - float(fps_list[1]))

    # success
    if diff <= 1:
        log_print("PASS\n")
        return 1
    # soft failure
    elif diff <= 3 and diff > 1:
        log_print("SOFT FAIL\n")
        return 1
    # hard failure
    else:
        log_print("HARD FAIL\n")
        return 1

current = date.today()
path = os.getcwd()
cap = None
device_num = 0
reboots_hard = 0
reboots_soft = 0
reboots_temp = 0
err_code = {}
failures = {}

# create directory for log and .png files if it doesn't already exist
if device_name == "Jabra PanaCast 20":
    log_name = "p20"
elif device_name == "Jabra PanaCast 50" or device_name == "Video Capture 2":
    log_name = "p50"

filename = "{}_resolutionfps_{}.log".format(current, log_name)
log_path = os.path.join(path+"/resolutionfps", filename)
fail = "{}_failed_resolutionfps_{}.log".format(current, log_name)
fail_path = os.path.join(path+"/resolutionfps", fail)
if not os.path.exists(path+"/resolutionfps"):
    os.makedirs(path+"/resolutionfps")

log_file = open(log_path, "a")
fail_file = open(fail_path, "a")
timestamp = datetime.now()
log_print(55*"=")
log_print("\n{}\n".format(timestamp))

if __name__ == "__main__":
    # set up camera stream
    if not get_device():
        log_print("Device not found, please check if it is attached")
        sys.exit(0)

    if not cap.isOpened():
        cap.open(device_num)
    cnt_test = 0
    for fmt in test_cases:
        res_dict = test_cases[fmt]
        res_keys = list(res_dict.keys())
        while(cnt_test == 0):
            resolution = random.sample(res_keys, k = 1)[0]
            print(resolution)
            framerate = res_dict[resolution]
            fps = random.sample(framerate, k = 1)[0]
            log_print(65*"=")
            log_print("Testing:                {} {} {}fps\n".format(fmt, resolution, fps))
            log_print(65*"=")
            test_type = "{} {} {}fps".format(fmt, resolution, fps)
            err_code[test_type] = test_fps(fmt, resolution, fps)

            if err_code[test_type] == 0 or err_code[test_type] == -1:
                failures[test_type] = err_code[test_type]
                cnt_test = int(input("Press 0 to conitnue, anything else end test ..."))

    report_results()
    cap.release()
    cv2.destroyAllWindows()

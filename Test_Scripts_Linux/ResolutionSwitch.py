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

ap = argparse.ArgumentParser()
ap.add_argument("-d","--debug", type=bool, default=False, help="Set to True to disable msgs to terminal")
ap.add_argument("-f","--frame", type=bool, default=False, help="Set to True to enable live view")
ap.add_argument("-p","--power", type=bool, default=False, help="Set to true when running on the Jenkins server")
ap.add_argument("-t","--test", type=str, default="res_switch_p50.json", help="Specify .json file to load test cases")
ap.add_argument("-v","--video", type=str, default="Jabra PanaCast 50", help="Specify which camera to test")
args = vars(ap.parse_args())
debug = args["debug"]
live_view = args["frame"]
test_file = "config/" + args["test"]
power_cycle = args["power"]
device_name = args["video"]

input_tests = open(test_file)
json_str = input_tests.read()
test_cases = json.loads(json_str)

current = date.today()
path = os.getcwd()
cap = None
device_num = 0
reboots = 0
err_code = {}
failures = {}

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

def report_results():
    log_print("\nGenerating report...")
    log_print("Number of video crashes/freezes: {}".format(reboots))
    report = p.pformat(err_code, width=20)
    log_print("{}\n".format(report))
    log_file.close()

    fail_file.write("""Resolution Switch test cases that resulted in soft failures or hard failures. Please refer to resolutionswitch.log for more details on each case.
    [-1] denotes hard failure (<27 fps, >1200ms switch time, or crash/freeze)
    [0] denotes soft failure (27-28.99 fps)
    Number of video crashes/freezes: {}\n\n""".format(reboots))
    fail_report = p.pformat(failures, width=20)
    fail_file.write("{}\n\n".format(fail_report))
    fail_file.close()

def get_device():
    global cap
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
    global reboots
    switch = 0

    log_print("Rebooting...")
    if fmt == "MJPG":
        switch = 1
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

    reboots += 1
    if reboots > 5:
        log_print("More than 5 reboots, exiting test. Please check physical device\n")
        report_results()
        sys.exit(0)

def check_frame(check_width, check_height, fmt):
    while True:
        try:
            retval, frame = cap.read()
            # check if frame is successfully grabbed
            if retval is not False or frame is not None:
                h, w = frame.shape[:2]
                if w == check_width and h == check_height:
                    return True
                else:
                    continue
        except:
            # in case watchdog was triggered
            time.sleep(15)
            return False

def test_fps(width, height, target_res, start_fps, target_fps, fmt):
    start_frame, test_frame, total_frame, drop_frame = (0 for x in range(4))
    all_fps = []
    global cap
    global err_code
    global failures

    for t_res in target_res:
        for s_fps in start_fps:
            for t_fps in target_fps:
                # label test case
                if t_res[0] == width and t_res[1] == height:
                    continue

                test_type = "{} {}x{} [{} fps] -> {}x{} [{} fps]".format(fmt, width, height, s_fps, t_res[0], t_res[1], t_fps)
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
                    log_print("Video format set to:  {} ({})".format(codec, fourcc))

                # set start res/fps
                cap.set(cv2.CAP_PROP_FPS, s_fps)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                # print("set start")
                
                # set target res/fps
                cap.set(cv2.CAP_PROP_FPS, t_fps)
                switch_start = time.time()
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, t_res[0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, t_res[1])
                # print("set target")

                # calculate switch time
                if check_frame(t_res[0], t_res[1], fmt):
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
                            break
                            
                    else:
                        if live_view is True:
                            cv2.imshow('frame', frame)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                        test_frame += 1
                        # print("Frame grabbed")
            
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
                # save copy of failed test cases
                if err_code[test_type] == 0 or err_code[test_type] == -1:
                    failures[test_type] = err_code[test_type]

                all_fps.clear()
                # time.sleep(1)

# create directory for log and .png files if it doesn't already exist
if device_name == "Jabra PanaCast 20":
    log_name = "p20"
elif device_name == "Jabra PanaCast 50":
    log_name = "p50"

filename = "{}_resolutionswitch_{}.log".format(current, log_name)
file_path = os.path.join(path+"/resolutionswitch", filename)
fail = "{}_failed_resolutionswitch_{}.log".format(current, log_name)
fail_path = os.path.join(path+"/resolutionswitch", fail)
if not os.path.exists(path+"/resolutionswitch"):
    os.makedirs(path+"/resolutionswitch")

log_file = open(file_path, "a")
fail_file = open(fail_path, "a")
timestamp = datetime.now()
log_print(55*"=")
log_print("\n{}\n".format(timestamp))

if __name__ == "__main__":
    # set up camera stream
    if not get_device():
        log_print("Device not found, please check if it is attached.")
        sys.exit(0)

    # cycle through all test cases provided by json file
    cap.open(device_num)
    for fmt in test_cases:
        codec = test_cases[fmt]
        start_res = codec['start res']
        target_res = codec['target res']
        start_fps = codec['start fps']
        target_fps = codec['target fps']
        for start in start_res:
            width = start[0]
            height = start[1]
            test_fps(width, height, target_res, start_fps, target_fps, fmt)
    
    report_results()
    cap.release()
    cv2.destroyAllWindows()

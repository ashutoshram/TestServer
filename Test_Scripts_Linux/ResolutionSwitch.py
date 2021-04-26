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
ap.add_argument("-t","--test", type=str, default="res_switch_p50.json", help="Specify .json file to load test cases")
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
failures = {}
err_code = {}

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

filename = "{}_resolutionswitch.log".format(current)
file_path = os.path.join(path+"/resolutionswitch", filename)
fail = "{}_failed_resolutionswitch.log".format(current)
fail_path = os.path.join(path+"/resolutionswitch", fail)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"/resolutionswitch"):
    os.makedirs(path+"/resolutionswitch")

log_file = open(file_path, "a")
fail_file = open(fail_path, "a")
timestamp = datetime.now()
log_print(55*"=")
log_print("\n{}\n".format(timestamp))

def reboot_device():
    print("Panacast device error")
    # reboot by resetting USB if testing P20
    if device_name == "Jabra PanaCast 20":
        device_info = subprocess.check_output('lsusb | grep "Jabra PanaCast 20"', shell==True)
        device_info = device_info.decode("utf-8")
        ids = re.search('Bus (\d+) Device (\d+)', device_info).group()
        ids = re.findall('(\d+)', ids)
        subprocess.check_call(['sudo', './usbreset', '/dev/bus/usb/{}/{}'.format(ids[0], ids[1])])
    else:
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
        try:
            cam = subprocess.check_output('v4l2-ctl --list-devices 2>/dev/null | grep "{}" -A 1 | grep video'.format(device_name), shell=True, stderr=subprocess.STDOUT)
            cam = cam.decode("utf-8")
            device_num = int(re.search(r'\d+', cam).group())
            device = 'v4l2-ctl -d /dev/video{}'.format(device_num)
            cap = cv2.VideoCapture(device_num)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Command '{}' returned with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        if cap.isOpened():
            log_print("Device back online:  {}\n".format(device_num))
            cap.open(device_num)
            break
        else:
            sys.exit(1)

def check_frame(check_width, check_height):
    while True:
        retval, frame = cap.read()
        h, w = frame.shape[:2]
        if retval is True and w == check_width and h == check_height:
            # print("Resolution set to:    {} x {}".format(w, h))
            return True

def test_fps(width, height, target_res, start_fps, target_fps, fmt):
    start_frame, test_frame, total_frame, drop_frame = (0 for x in range(4))
    all_fps = []
    global err_code
    global failures

    for t_res in target_res:
        for s_fps in start_fps:
            for t_fps in target_fps:
                # convert video codec number to format and check if set correctly
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fmt))
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
                log_print("Video format set to:    {} ({})".format(codec, fourcc))
                # make sure format is set correctly
                if codec != fmt:
                    log_print("Unable to set video format correctly.")
                    reboot_device()
                    return -1

                # set start res/fps
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                cap.set(cv2.CAP_PROP_FPS, s_fps)
                
                # set target res/fps
                if t_res[0] == width and t_res[1] == height:
                    continue
                test_type = "{} {}x{} [{} fps] -> {}x{} [{} fps]".format(fmt, width, height, s_fps, t_res[0], t_res[1], t_fps)
                switch_start = time.time()
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, t_res[0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, t_res[1])
                cap.set(cv2.CAP_PROP_FPS, t_fps)

                # calculate switch time
                if check_frame(t_res[0], t_res[1]):
                    switch_end = time.time()
                switch_time = switch_end - switch_start

                log_print(55*"=")
                log_print("{}\n".format(test_type))
                log_print("Time to switch (ms):   {}\n".format(switch_time * 1000))
                test_start, test_time = (time.time() for x in range(2))
                
                # grab frames for 30 seconds
                frame_count = t_fps * 30
                for i in range(0, frame_count):
                    retval, frame = cap.read()
                    # reboot device in event of frame drop/error
                    if retval is False:
                        drop_frame += 1
                        log_print("Frame #{} dropped!".format(drop_frame))
                        if time.time() > test_start + 10:
                            log_print("Timeout error")
                            reboot_device()
                    else:
                        if live_view is True:
                            cv2.imshow('frame', frame)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
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
                if switch_time * 1000 < 1500:
                    if avg_fps >= t_fps - 1:
                        err_code[test_type] = 1
                        log_print("PASS\n")
                    elif avg_fps < t_fps - 1 and avg_fps >= t_fps - 3:
                        err_code[test_type] = 0
                        log_print("SOFT FAIL\n")
                    else:
                        err_code[test_type] = -1
                        log_print("HARD FAIL\n")
                else:
                    err_code[test_type] = -1
                    log_print("HARD FAIL\n")
                # save copy of failed test cases
                if err_code[test_type] == 0 or err_code[test_type] == -1:
                    failures[test_type] = err_code[test_type]

                all_fps.clear()

if __name__ == "__main__":
    # set up camera stream 
    try:
        cam = subprocess.check_output('v4l2-ctl --list-devices 2>/dev/null | grep "{}" -A 1 | grep video'.format(device_name), shell=True, stderr=subprocess.STDOUT)
        cam = cam.decode("utf-8")
        device_num = int(re.search(r'\d+', cam).group())
        cap = cv2.VideoCapture(device_num)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Command '{}' returned with error (code {}): {}".format(e.cmd, e.returncode, e.output))
       
    if device_num is None:
        log_print("PanaCast device not found. Please make sure the device is properly connected and try again")
        sys.exit(1)
    if cap.isOpened():
        log_print("PanaCast device found:  {}\n".format(device_num))
    # cylce through all test cases provided by json file
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
    
    log_print("\nGenerating report...")
    log_print("Number of video crashes/freezes: {}".format(reboots))
    report = p.pformat(err_code)
    log_print("{}\n".format(report))
    log_file.close()

    fail_file.write("""Test cases that resulted in soft failures or hard failures. Please refer to resolutionswitch.log for more details on each case.
    [-1] denotes hard failure (<27 fps, >1200ms switch time, or crash/freeze)
    [0] denotes soft failure (27-28.99 fps)
    Number of video crashes/freezes: {}\n\n""".format(reboots))
    fail_report = p.pformat(failures)
    fail_file.write("{}\n\n".format(fail_report))
    fail_file.close()

    cap.release()
    cv2.destroyAllWindows()

import numpy as np
import cv2
import time
import os
import subprocess
import argparse
import re
from datetime import date, datetime

ap = argparse.ArgumentParser()
ap.add_argument("-f","--frame", type=bool, default=False, help="Set to True to enable live view")
args = vars(ap.parse_args())
live_view = args["frame"]

global cap
global reboots

debug = True

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

current = date.today()
path = os.getcwd()
device_num = 0
reboots = 0

filename = "{}_resolutionswitch.log".format(current)
file_path = os.path.join(path+"/resolutionswitch", filename)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"/resolutionswitch"):
    os.makedirs(path+"/resolutionswitch")

log_file = open(file_path, "a")
timestamp = datetime.now()
log_print(55*"=")
log_print("\n{}\n".format(timestamp))

def reboot_device(cap):
    print("Panacast device error")
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
        device = subprocess.check_output('v4l2-ctl --list-devices 2>/dev/null | grep "Jabra PanaCast 50" -A 1 | grep video', shell=True)
        device = device.decode("utf-8")
        device_num = int(re.search(r'\d+', device).group())
        cap = cv2.VideoCapture(device_num)
        if cap.isOpened():
            log_print("Device back online:  {}\n".format(device_num))
            break
        else:
            time.sleep(5)

if __name__ == "__main__":
    # set up camera stream        
    device = subprocess.check_output('v4l2-ctl --list-devices 2>/dev/null | grep "Jabra PanaCast 50" -A 1 | grep video', shell=True)
    device = device.decode("utf-8")
    device_num = int(re.search(r'\d+', device).group())
    cap = cv2.VideoCapture(device_num)

    if device_num is None:
        log_print("PanaCast device not found. Please make sure the device is properly connected and try again")
        sys.exit(1)
    if cap.isOpened():
        log_print("PanaCast device found:  {}".format(device_num))

    frame_count = 900
    resolution_set = [(1920, 1080), (1280,720), (1920,1080), (960, 540), (1920,1080), (640, 360), (1280, 720), (1920, 1080), (1280,720), (960, 540), (1280, 720), (640, 360), (960, 540), (1920, 1080), (960, 540), (1280, 720), (960, 540), (640, 360), (1920, 1080), (640, 360), (1280, 720)]
    #resolution_set_end = [(1920, 1080), (1280,720), (960, 540), (640, 360)]
    num_res = len(resolution_set)
    start_frame = 0
    test_frame = 0
    total_frame = 0

    format_ = 'NV12'
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*format_))

    i = 1
    full_start, half_start, test_start = (time.time() for x in range(3))

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_set[0][0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_set[0][1])
    log_print("Resolution set to %d x %d\n" % (resolution_set[0][0], resolution_set[0][1]))
    
    while(True):
        if start_frame == (frame_count*num_res)+frame_count-1:
            end = time.time()
            total_elapsed = end - full_start
            fps = float((start_frame) / total_elapsed)
            log_print("Test duration:          {:<5} s".format(total_elapsed))
            log_print("Total frames grabbed:   {:<5}".format(start_frame))
            log_print("Actual average fps:     {:<5}\n".format(fps))
            break

        # Capture frame-by-frame
        ret, frame = cap.read()
        start_frame += 1
        test_frame += 1
        total_frame += 1
        
        if live_view is True:
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # check framerate every five seconds
        if test_frame % 150 == 0:
            test_end = time.time()
            current = test_end - half_start
            overall = test_end - test_start
            log_print("Test {} duration (sec):  {:>2} s".format(i, overall))
            log_print("Total frames grabbed:   {:<5}".format(test_frame))

            fps = float((test_frame) / current)
            log_print("Current average fps:    {:<5}\n".format(fps))
            # log_print("total_frame:          {}\n".format(total_frame))
            if total_frame >= frame_count:
                try:
                    log_print(55*"=")
                    log_print("Resolution set to %d x %d\n" % (resolution_set[i][0], resolution_set[i][1]))
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_set[i][0])
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_set[i][1])
                    i += 1
                    total_frame = 0
                    half_elapsed = 0
                    overall = 0
                    test_start = time.time()
                    # full_start = time.time()
                except:
                    break
            
            test_frame = 0
            half_start = time.time()

    cap.release()
    cv2.destroyAllWindows()

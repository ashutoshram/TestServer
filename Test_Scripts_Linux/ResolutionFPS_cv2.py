import os
import time
import platform
import numpy as np
import sys
import cv2
from queue import Queue
from datetime import date
import datetime
import AbstractTestClass as ATC
import pprint as p
import json
import subprocess
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-d","--debug", type=bool, default=False, help="Set to True to disable msgs to terminal")
ap.add_argument("-f","--file", type=str, default="sample.json", help="Specify .json file to load test cases")
args = vars(ap.parse_args())
debug = args["debug"]
json_file = args["file"]

input_file = open(json_file)
json_str = input_file.read()
test_cases = json.loads(json_str)

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

current = date.today()
path = os.getcwd()
device_num = 0
reboots = 0

filename = "{}_resolutionfps.log".format(current)
file_path = os.path.join(path+"/resolutionfps", filename)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"/resolutionfps"):
    os.makedirs(path+"/resolutionfps")

log_file = open(file_path, "a")
timestamp = datetime.datetime.now()
log_print(55*"=")
log_print("\n{}\n".format(timestamp))

class FPS(ATC.AbstractTestClass):
    def __init__(self):
        self.FPSTest = FPSTester()

    def get_args(self):
        return ['all']

    def run(self, args):
        return self.FPSTest.test(args)

    def get_progress(self):
        return self.FPSTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_name(self):
        return "ResolutionFPS Test"
    
    def is_done(self):
        if self.FPSTest.progress() == 100:
            return True
        else:
            return False
    
    def get_storage_path(self):
        return self.storage_path

    def generate_report(self):
        return self.FPSTest.results()

class FPSTester():
    def __init__(self):
        self.progress_percent = 0 

    def reboot_device(self):
        log_print("Panacast device error")
        os.system("sudo adb kill-server")
        os.system("sudo adb devices")
        os.system("adb reboot")
        log_print("Rebooting...")
        time.sleep(65)
        global device_num
        global reboots
        device_num = 0
        reboots += 1

        while True:
            self.cam = cv2.VideoCapture(device_num)
            if self.cam.isOpened():
                self.cam = cv2.VideoCapture(device_num)
                log_print("Device back online: {}\n".format(device_num))
                time.sleep(5)
                break
            else:
                device_num += 1
                time.sleep(15)

    def test_fps(self, format_, resolution, framerate, zoom):
        # check if camera stream exists
        global device_num
        if self.cam is None:
            print('cv2.VideoCapture unsuccessful')
            sys.exit(1)
        
        self.cam.open(device_num)

        if format_ == 'YU12':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YU12'))
        elif format_ == 'YUYV':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        elif format_ == 'NV12':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'NV12'))

        fourcc = int(self.cam.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        log_print("Video format set to:    {} ({})".format(codec, fourcc))

        if resolution == '4k':
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        elif resolution == '1200p':
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 4800)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
        elif resolution == '1080p':
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        elif resolution == '720p':
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        elif resolution == '540p':
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        elif resolution == '360p':
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        
        width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        log_print("Resolution set to:      {} x {}".format(width, height))

        # set zoom level
        device = 'v4l2-ctl -d /dev/video{}'.format(device_num)
        log_print("Setting zoom level to:  {}".format(zoom))
        subprocess.call(['{} -c zoom_absolute={}'.format(device, str(zoom))], shell=True)

        # open opencv capture device and set the fps
        log_print("Setting framerate to:   {}".format(framerate))
        self.cam.set(cv2.CAP_PROP_FPS, framerate)
        current_fps = self.cam.get(cv2.CAP_PROP_FPS)
        log_print("Current framerate:      {}\n".format(current_fps))

        # check if device is responding to get/set commands and try rebooting if it isn't
        if width == 0 and height == 0 and current_fps == 0:
            log_print("Device not responding to get/set commands")
            self.reboot_device()

        # set number of frames to be counted
        frames = [(framerate*40)]
        fps_list = []
        prev_frame = 0
        drops, delayed, count, initial_frames, initial_elapsed = (0 for x in range(5))

        # calculate fps
        for f in frames:
            start = time.time()
            # default initial value
            initial_elapsed = 30
            for i in range(0, f):
                try:
                    retval, frame = self.cam.read()
                    current_frame = self.cam.get(cv2.CAP_PROP_POS_MSEC)
                    diff = current_frame - prev_frame
                    prev_frame = current_frame
                    skip = False
                    
                    if framerate == 30:
                        if diff > 38.33 and count > 0:
                            delayed += 1
                            skip = True
                    elif framerate == 15:
                        if diff > 71.67 and count > 0:
                            delayed += 1
                            skip = True

                    if codec == "MJPG" and format_ != "MJPG":
                        log_print("Device negotiated USB 2.0 connection.")
                        self.reboot_device()
                        return -1

                    if skip is False:
                        if retval is False:
                            drops += 1
                            # log_print("Failed to grab frame!")
                            if time.time() > start + 30:
                                raise cv2.error("Timeout error")
                            continue
                        else:
                            count += 1
                    
                    if framerate == 30 and i == 899:
                        initial_frames = count + delayed
                        initial_end = time.time()
                        initial_elapsed = initial_end - start

                except cv2.error as e:
                    log_print("{}".format(e))
                    self.reboot_device()
                    return -1
        
            end = time.time()
            total_elapsed = end - start
            elapsed = total_elapsed - initial_elapsed
            actual_frames = count + delayed

            log_print("Test duration:          {:<5} s".format(total_elapsed))
            log_print("Total frames grabbed:   {:<5}".format(count))
            log_print("Total frames delayed:   {:<5}".format(delayed))
            log_print("Total frames dropped:   {:<5}".format(drops))

            initial_fps = float(initial_frames / initial_elapsed)
            fps_list.append(initial_fps)
            log_print("Initial average fps:    {:<5}".format(initial_fps))

            fps = float((actual_frames-initial_frames) / elapsed)
            fps_list.append(fps)
            log_print("Actual average fps:     {:<5}\n".format(fps))
        
        diff = abs(float(framerate) - float(fps_list[1]))
         
        # success
        if diff <= 1:
            return 1
        # soft failure
        elif diff <= 3 and diff > 1:
            return 0
        # hard failure
        else:
            return -1

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        self.err_code = {}
        global device_num

        zoom_levels = [1, 10, 20, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 
                       34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]

        # set up camera stream
        for k in range(4):
            self.cam = cv2.VideoCapture(k)
            if self.cam.isOpened():
                log_print("Panacast device found:  {}".format(k))
                device_num = k
                break

        # iterate through the dictionary and test each format, resolution, and framerate
        for format_ in test_cases:
            res_dict = test_cases[format_]

            for resolution in res_dict:
                framerate = res_dict[resolution]
                log_print(55*"=")
                log_print("Parameters:             {} {} {}".format(format_, resolution, framerate))

                for fps in framerate:
                    for z in zoom_levels:
                        log_print(55*"=")
                        # special case for YUYV
                        if format_ == "YUYV":
                            log_print("Testing:                {} {} {} {}\n".format(format_, resolution, fps, 1))
                            test_type = "{} {} {} {}".format(format_, resolution, fps, 1)
                            self.err_code[test_type] = self.test_fps(format_, resolution, fps, 1)
                            break

                        log_print("Testing:                {} {} {} {}\n".format(format_, resolution, fps, z))
                        test_type = "{} {} {} {}".format(format_, resolution, fps, z)
                        self.err_code[test_type] = self.test_fps(format_, resolution, fps, z)

            self.progress_percent = 100
            self.cam.release()

        return self.err_code

if __name__ == "__main__":
    t = FPS()
    args = t.get_args()
    t.run(args)

    log_print("\nGenerating report...")
    log_print("Number of video crashes/freezes (that required reboots): {}".format(reboots))
    report = p.pformat(t.generate_report())
    log_print("{}\n".format(report))
    log_file.close()

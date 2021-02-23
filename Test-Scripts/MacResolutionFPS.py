import os
import jabracamera
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
args = vars(ap.parse_args())
debug = args["debug"]

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
        self.start_device()

    def start_device(self):
        log_print("Starting Device")
        self.cam = jabracamera.JabraCamera()
        dn = self.cam.getCameras()
        if dn is None:
            print("No PanaCast Cameras found")
            sys.exit(1)
        self.device = dn[0]


    def test_fps(self, format_, resolution, framerate, zoom):
        # check if camera stream exists
        if self.cam is None:
            print('VideoCapture unsuccessful')
            sys.exit(1)
        
        log_print("Video format set to:    {} ".format(format_))

        if resolution == '4k':

            if not self.cam.setStreamParams(deviceName=self.device, width=3840, height=1080, format=format_,fps=30):
                print("unable to set params to %s %s" %(format_, resolution))
                sys.exit(1)

        elif resolution == '1080p':
            if not self.cam.setStreamParams(deviceName=self.device, width=1920, height=1080, format=format_,fps=30):
                print("unable to set params to %s %s" %(format_, resolution))
                sys.exit(1)
        elif resolution == '720p':
            if not self.cam.setStreamParams(deviceName=self.device, width=1280, height=720, format=format_,fps=30):
                print("unable to set params to %s %s" %(format_, resolution))
                sys.exit(1)
        elif resolution == '540p':
            if not self.cam.setStreamParams(deviceName=self.device, width=960, height=540, format=format_,fps=30):
                print("unable to set params to %s %s" %(format_, resolution))
                sys.exit(1)
        elif resolution == '360p':
            if not self.cam.setStreamParams(deviceName=self.device, width=640, height=360, format=format_,fps=30):
                print("unable to set params to %s %s" %(format_, resolution))
                sys.exit(1)
        
        #width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        #height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        #log_print("Resolution set to:      {} x {}".format(width, height))

        # set zoom level
        #device = 'v4l2-ctl -d /dev/video{}'.format(device_num)
        #log_print("Setting zoom level to:  {}".format(zoom))
        #subprocess.call(['{} -c zoom_absolute={}'.format(device, str(zoom))], shell=True)

        # open opencv capture device and set the fps
        #log_print("Setting framerate to:   {}".format(framerate))
        #self.cam.set(cv2.CAP_PROP_FPS, framerate)
        #current_fps = self.cam.get(cv2.CAP_PROP_FPS)
        #log_print("Current framerate:      {}\n".format(current_fps))

        # check if device is responding to get/set commands and try rebooting if it isn't
        #if width == 0 and height == 0 and current_fps == 0:
        #    log_print("Device not responding to get/set commands")
            #self.reboot_device()

        # set number of frames to be counted
        frames = [(framerate*10)]
        fps_list = []
        prev_frame = 0
        drops, delayed, count, initial_frames = (0 for x in range(4))
        test_passed = False

        # calculate fps
        for f in frames:
            start = time.time()
            for i in range(0, f):
                try:
                    frame = self.cam.getFrame(self.device)
                    count += 1
                    test_passed = True
                    
                    #if framerate == 30 and i == 899:
                    #    initial_end = time.time()
                        # print("HERE")

                except:
                    log_print("Frame Grab Failed")
                    break
        
            end = time.time()
            total_elapsed = end - start
            average_fps = (count / total_elapsed)

            log_print("Test duration:          {:<5} s".format(total_elapsed))
            log_print("Total frames grabbed:   {:<5}".format(count))
            log_print("Average FPS:            {:<5}".format(average_fps))

        if test_passed == False:
            print(test_passed)
            return -1
        else:
            print(test_passed)
            return 0

        

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        self.err_code = {}
        global device_num

        #dictionary of testing parameters
        fps_params = {'YU12': {'1080p': [30], 
                               '720p': [30], 
                               '540p': [30], 
                               '360p': [30]},
                      'NV12': {'1080p': [30], 
                               '720p': [30], 
                               '540p': [30], 
                               '360p': [30]},
                      'YUYV': {'4k': [30]}}

        zoom_levels = [1, 10, 20, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 
                       34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]

        # deep zoom
        # zoom_levels = [1]

        # set up camera stream
        #for k in range(4):
        #    self.cam = cv2.VideoCapture(k)
        #    if self.cam.isOpened():
        #        log_print("Panacast device found:  {}".format(k))
        #        break

        # iterate through the dictionary and test each format, resolution, and framerate
        for format_ in fps_params:
            # skip some formats for now
            if format_ == "YU12":
                continue
            res_dict = fps_params[format_]

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

import os
import time
import platform
import numpy as np
import sys
import cv2
from queue import Queue
import datetime
from datetime import date
import AbstractTestClass as ATC
import pprint as p

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

debug = True
current = date.today()
path = os.getcwd()
device_num = 0

filename = "{}_resolutionfps.log".format(current)
file_path = os.path.join(path+"\\resolutionfps", filename)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"\\resolutionfps"):
    os.makedirs(path+"\\resolutionfps")

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

    def test_fps(self, format_, resolution, framerate):
        # check if camera stream exists
        global device_num
        if self.cam is None:
            print('cv2.VideoCapture unsuccessful')
            sys.exit(1)

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
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        log_print("Resolution set to:      {} x {}".format(int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        if format_ == 'MJPG':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        elif format_ == 'YUYV':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        elif format_ == 'YUY2':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        elif format_ == 'I420':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'I420'))
        elif format_ == 'NV12':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'NV12'))

        fourcc = self.cam.get(cv2.CAP_PROP_FOURCC)
        fourcc = int(fourcc)
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        log_print("Video format set to:    {} ({})".format(codec, fourcc))

        # open opencv capture device and set the fps
        log_print("Setting framerate to:   {}".format(framerate))
        self.cam.set(cv2.CAP_PROP_FPS, framerate)
        current_fps = self.cam.get(cv2.CAP_PROP_FPS)
        log_print("Current framerate:      {}\n".format(current_fps))
        
        # check fps for 1, 5, and 10 second streams
        start = time.time()
        count, skipped = (0 for i in range(2))
        five_yes, ten_yes = (False for i in range(2))

        # calculate fps
        frames = framerate*30
        fps_list = []
        for f in range(0, frames):
            start = time.time()
            for i in range(0, framerate*30):
                try:
                    retval, frame = self.cam.read()
                    if retval is False:
                        raise cv2.error("OpenCV error")
                    if time.time() > start + 30:
                        raise cv2.error("Timeout error")
                except cv2.error as e:
                    log_print("{}".format(e))
                    log_print("Panacast device crashed, rebooting...")
                    os.system("adb reboot")
                    time.sleep(95)
                    device_num = 0
                    while True:
                        self.cam = cv2.VideoCapture(device_num)
                        if self.cam.isOpened():
                            self.cam = cv2.VideoCapture(device_num)
                            log_print("Device back online: {}".format(device_num))
                            time.sleep(20)
                            break
                        else:
                            device_num += 1
                            time.sleep(20)
                    return -1
        
            end = time.time()
            elapsed = 30

            log_print("Test duration:          {:<5} s".format(elapsed))
            log_print("Total frames counted:   {:<5}".format(f))
            fps = float(f / elapsed)
            fps_list.append(f / elapsed)
            log_print("Average fps:            {:<5}\n".format(fps))
        
        # diff5 = abs(float(framerate) - float(fps_list[0]))
        diff10 = abs(float(framerate) - float(fps_list[0])) # change back to fps_list[1]
        
        # set framerate back to default
        self.cam.set(cv2.CAP_PROP_FPS, 30)
        self.cam.release()
 
        # success
        # add "diff5 <= 2 and" to evaluate 5 sec fps 
        if diff10 <= 2:
            return 0
        #failure
        else:
            return -1

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        # dbg_print('FPSTester::test: args = %s' % repr(args))
        self.err_code = {}

        #dictionary of testing parameters
        fps_params = {'YU12': {'1080p': [30], 
                               '720p': [30], 
                               '540p': [30], 
                               '360p': [30]},
                      'NV12': {'1080p': [30], 
                               '720p': [30], 
                               '540p': [30], 
                               '360p': [30]}}

        zoom_levels = [1, 10, 20, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 
                       34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]

        # set up camera stream
        for k in range(4):
            self.cam = cv2.VideoCapture(k)
            if self.cam.isOpened():
                log_print("\nPanacast device found:  {}".format(k))
                device_num = k
                break

        # iterate through the dictionary and test each format, resolution, and framerate
        for format_ in fps_params:
            res_dict = fps_params[format_]

            for resolution in res_dict:
                framerate = res_dict[resolution]
                log_print(55*"=")
                log_print("Parameters:             {} {} {}".format(format_, resolution, framerate))

                for fps in framerate:
                    for z in zoom_levels:
                        log_print("Testing:                {} {} {} {}\n".format(format_, resolution, fps, z))
                        test_type = "{} {} {} {}".format(format_, resolution, fps, z)
                        self.err_code[test_type] = self.test_fps(format_, resolution, fps)
                        self.cam.release()

                # self.progress_percent += 33
            self.progress_percent = 100

        # dbg_print('FPSTester::test: err_code = %s' % repr(self.err_code))
        return self.err_code

if __name__ == "__main__":
    t = FPS()
    args = t.get_args()
    t.run(args)
    # print(t.get_progress())
    # print(t.is_done())

    log_print("\nGenerating report...")
    report = p.pformat(t.generate_report())
    log_print("{}\n".format(report))
    log_file.close()

import os
import time
import platform
import numpy as np
import sys
import cv2
from queue import Queue
from datetime import date
import AbstractTestClass as ATC
import pprint as p

debug = True
current = date.today()
path = os.getcwd()

filename = "{}_fps.log".format(current)
file_path = os.path.join(path+"\\fps", filename)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"\\fps"):
    os.makedirs(path+"\\fps")

log_file = open(file_path, "a")

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

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
        return "FPS Test"
    
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
        if self.cam is None:
            log_print('cv2.VideoCapture unsuccessful')
            sys.exit(1)

        if resolution == '4k':
            # log_print("Resolution to be set to: 3840 x 1080")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        elif resolution == '1080p':
            # log_print("Resolution to be set to: 1920 x 1080")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        elif resolution == '720p':
            # log_print("Resolution to be set to: 1280 x 720")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        elif resolution == '480p':
            # log_print("Resolution to be set to: 640 x 480")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        log_print("Resolution set to:      {} x {}".format(int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        
        if format_ == 'MJPG':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            log_print("Video format set to:    MJPG")
        elif format_ == 'YUYV':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
            log_print("Video format set to:    YUYV")
        elif format_ == 'YUY2':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUY2'))
            log_print("Video format set to:    YUY2")
        elif format_ == 'I420':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'I420'))
            log_print("Video format set to:    I420")
        elif format_ == 'NV12':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'NV12'))
            log_print("Video format set to:    NV12")
        
        # open opencv capture device and set the fps
        log_print("Setting framerate to:   {}".format(framerate))
        self.cam.set(cv2.CAP_PROP_FPS, framerate)
        current_fps = self.cam.get(cv2.CAP_PROP_FPS)
        log_print("Current framerate:      {}\n".format(current_fps))
        
        # check fps for 1, 5, and 10 second streams
        start = time.time()
        one = start + 1
        five = start + 5
        ten = start + 10
        count, skipped = (0 for i in range(2))
        five_yes, ten_yes = (False for i in range(2))

        # calculate fps
        while True:
            if time.time() >= five and five_yes is False:
                duration = time.time() - start
                log_print("Duration:               {:<5} s".format(duration))
                log_print("Total frames counted:   {:<5}".format(count))
                log_print("Total frames skipped:   {:<5}".format(skipped))
                fps5 = count / duration
                log_print("Average fps:            {:<5}\n".format(fps5))
                five_yes = True
            elif time.time() >= ten and ten_yes is False:
                duration = time.time() - start
                log_print("Duration:               {:<5} s".format(duration))
                log_print("Total frames counted:   {:<5}".format(count))
                log_print("Total frames skipped:   {:<5}".format(skipped))
                fps10 = count / duration
                log_print("Average fps:            {:<5}\n".format(fps10))
                ten_yes = True
                break

            retval, frame = self.cam.read()
            if retval is True:
                count += 1
            else:
                skipped += 1
                log_print("Panacast device crashed, rebooting...")
                os.system("adb reboot")
                time.sleep(10)

        diff5 = abs(float(framerate) - float(fps5))
        diff10 = abs(float(framerate) - float(fps10))
        
        # set framerate back to default
        self.cam.set(cv2.CAP_PROP_FPS, 30)
    
        # success
        if diff5 <= 2 and diff10 <= 2:
            # log_print("Success.")
            return 0
        #failure
        else:
            # log_print("Failure.")
            return -1

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        # dbg_print('FPSTester::test: args = %s' % repr(args))
        self.err_code = {}

        #dictionary of testing parameters
        fps_params = {'I420': {'4k': [30, 27, 24, 15]},  
                      'MJPG': {'1080p': [30]},
                      'NV12': {'4k': [30, 27, 24, 15]},
                      'YUY2': {'4k': [30]}}

        # iterate through the dictionary and test each format, resolution, and framerate
        for format_ in fps_params:
            res_dict = fps_params[format_]
            for resolution in res_dict:
                framerate = res_dict[resolution]
                log_print(55*"=")
                log_print("Parameters:             {} {} {}".format(format_, resolution, framerate))
                for fps in framerate:
                    # set up camera stream
                    for k in range(4):
                        self.cam = cv2.VideoCapture(k)
                        if self.cam.isOpened():
                            log_print("\nPanacast device found:  {}".format(k))
                            break

                    log_print("Testing:                {} {} {}\n".format(format_, resolution, fps))
                    test_type = "{} {} {}".format(format_, resolution, fps)
                    self.err_code[test_type] = self.test_fps(format_, resolution, fps)
                    self.cam.release()

                self.progress_percent += 33
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

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

filename = "{}_resolution.log".format(current)
file_path = os.path.join(path+"\\resolution", filename)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"\\resolution"):
    os.makedirs(path+"\\resolution")

log_file = open(file_path, "a")

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

class Resolution(ATC.AbstractTestClass):
    def __init__(self):
        self.ResTest = ResTester()

    def get_args(self):
        return ['all']

    def run(self, args):
        return self.ResTest.test(args)

    def get_progress(self):
        return self.ResTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path
    
    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "Res Test"
    
    def is_done(self):
        if self.ResTest.progress() == 100:
            return True
        else:
            return False

    def generate_report(self):
        return self.ResTest.results()

class ResTester():
    count = 0

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0

    def test_res(self, format_, resolution):
        if resolution == '4k':
            # print("Resolution to be set to: 3840 x 1080")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        elif resolution == '1200p':
            # print("Resolution to be set to: 4800 x 1200")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 4800)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
        elif resolution == '1080p':
            # print("Resolution to be set to: 1920 x 1080")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        elif resolution == '720p':
            # print("Resolution to be set to: 1280 x 720")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        elif resolution == '540p':
            # print("Resolution to be set to: 960 x 540")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        elif resolution == '360p':
            # print("Resolution to be set to: 640 x 360")
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

        t_end = time.time() + 3
        count = 0

        while True:
            try:
                ret, frame = self.cam.read()
                if time.time() > t_end:
                    img = "{}_resolution_{}_{}.png".format(current, format_, resolution)
                    img = os.path.join(path+"\\resolution", img)
                    cv2.imwrite(img, frame)
                    # print("{} captured".format(img))
                    break
                # dbg_print('got frame: count = %d' % count)
                count += 1
            
            except Exception as e:
                log_print("{}".format(e))
                log_print("Panacast device crashed, rebooting...")
                os.system("adb reboot")
                time.sleep(15)
                return -1
                # sys.exit(1)

        h, w = frame.shape[:2]
        log_print("Height:                 {}\nWidth:                  {}\n".format(h, w))

        if resolution == '4k':
            if w == 3840 and h == 1080:
                return 0
            else: 
                return -1
        elif resolution == '1200p':
            if w == 4800 and h == 1200:
                return 0
            else: 
                return -1
        elif resolution == '1080p':
            if w == 1920 and h == 1080:
                return 0
            else: 
                return -1
        elif resolution == '720p':
            if w == 1280 and h == 720:
                return 0
            else: 
                return -1
        elif resolution == '540p':
            if w == 960 and h == 540:
                return 0
            else: 
                return -1
        elif resolution == '360p':
            if w == 640 and h == 360:
                return 0
            else: 
                return -1
       

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        # dbg_print('ResTester::test: args = %s' % repr(args))

        if 'all' in args: 
            tests = []
        else: 
            tests = list(map(int, args))

        self.err_code = {}
        # dbg_print('ResTester::test: tests = %s' % repr(tests))

        #dictionary of format, resolution
        frf = {'I420' : {'4k', '1080p', '720p', '540p', '360p'},
               'MJPG' : {'1080p', '720p', '540p', '360p'},
               'NV12' : {'4k', '1080p', '720p', '540p', '360p'},
               'YUY2' : {'4k', '1200p'}}

        for format_ in frf:
            resdict = frf[format_]
            log_print(70*"=")
            log_print("Parameters:             {} {}".format(format_, resdict))
            for resolution in resdict:
                for k in range(4):
                    self.cam = cv2.VideoCapture(k)
                    if self.cam.isOpened():
                        log_print("\nPanacast device found:  {}".format(k))
                        break
                log_print("Testing:                {} {}\n".format(format_, resolution))
                test_type = "{} {}".format(format_, resolution)
                self.err_code[test_type] = self.test_res(format_, resolution)
                self.progress_percent += 15
                self.cam.release()

        self.progress_percent = 100

        # dbg_print('ResTester::test: err_code = %s' % repr(self.err_code))
        return self.err_code

if __name__ == "__main__":
    t = Resolution()
    args = t.get_args()
    t.run(args)
    # log_print(t.get_progress())
    # log_print(t.is_done())

    log_print("\nGenerating report...")
    report = p.pformat(t.generate_report())
    log_print("{}\n".format(report))
    log_file.close()

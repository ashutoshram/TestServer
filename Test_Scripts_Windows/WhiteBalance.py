import os
import time
import platform
import numpy as np
import sys
import cv2
from queue import Queue

production = False
debug = False 
if not production:
    import AbstractTestClass as ATC
    # import webcamPy as wpy
else:
    import eos.scripts.AbstractTestClass as ATC
    import eos.scripts.webcamPy as wpy

def dbg_print(*args):
    if debug: 
        print("".join(map(str, args)))

class WhiteBal(ATC.AbstractTestClass):
    def __init__(self):
        self.WhiteBalTest = None

    def get_args(self):
        # return [0, 2122, 5000 , 6036 , 6500]
        return [0, 5000, 6500]

    def run(self, args, q, results, wait_q):
        self.WhiteBalTest = WhiteBalTester()
        self.WhiteBalTest.test(args, q, results)
        print("Whitebalance.run: waiting for wait_q")
        # got = wait_q.get()
        # print("Whitebalance.run: got %s" % repr(got))

    def get_progress(self):
        if self.WhiteBalTest is None:
            return 0
        return self.WhiteBalTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "WhiteBalance Test"
    
    def is_done(self):
        if self.WhiteBalTest is None:
            return False
        else:
            if self.WhiteBalTest.progress() == 100:
                return True
            else:
                return False

    def generate_report(self):
        return self.WhiteBalTest.results()

class WhiteBalTester():
    count = 0

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0
        # set up camera stream
        for k in range(4):
            self.cam = cv2.VideoCapture(k)
            if self.cam.isOpened():
                print("Panacast device found: ({})".format(k))
                break

        # self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # check if camera stream exists
        if self.cam is None:
            print('cv2.VideoCapture unsuccessful')
            sys.exit(1)
        print(self.cam)

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args, q, results):
        for whiteBal_level in args:
            return_val = self.test_whiteBal(int(whiteBal_level))
            print(type(return_val))
            print(type(whiteBal_level))
            if return_val == int(whiteBal_level):
                print("Success")
                self.err_code[whiteBal_level] = 0
            else:
                print("Failure")
                self.err_code[whiteBal_level] = -1
            self.progress_percent += 33
            q.put(self.progress_percent)
        self.progress_percent = 100
        q.put(self.progress_percent)
        results.put(self.err_code)
        return self.err_code

    def test_whiteBal(self, whiteBal_level):
        print('entering test_whiteBal')
        # set white balance and capture frame after three second delay
        self.cam.set(cv2.CAP_PROP_TEMPERATURE, whiteBal_level)
        t_end = time.time() + 3
        while True:
            ret, frame = self.cam.read()
            if time.time() > t_end:
                img = "test_wb" + "_{}".format(WhiteBalTester.count) + ".png"
                cv2.imwrite(img, frame)
                print("{} captured".format(img))
                # print(frame)
                break

        current_whiteBal = self.cam.get(cv2.CAP_PROP_TEMPERATURE)
        print("Current white balance temperature: {}".format(current_whiteBal))
        WhiteBalTester.count += 1
        return current_whiteBal

if __name__ == "__main__":
    t = WhiteBal()
    args = t.get_args()
    q = Queue()
    results = Queue()
    wait_q = Queue()
    t.run(args, q, results, wait_q)

    print("Generating report...")
    print(t.generate_report())

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

class Saturation(ATC.AbstractTestClass):

    def __init__(self):
        self.SaturationTest = None

    def get_args(self):
        return [128, 136, 160, 176, 155]

    def run(self, args, q, results, wait_q):
        self.SaturationTest = SaturationTester()
        self.SaturationTest.test(args, q, results)
        print("Saturation.run: waiting for wait_q")
        # got = wait_q.get()
        # print("Saturation.run: got %s" % repr(got))

    def get_progress(self):
        if self.SaturationTest is None:
            return 0
        return self.SaturationTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "Saturation Test"
    
    def is_done(self):
        if self.SaturationTest is None:
            return False
        else:
            if self.SaturationTest.progress() == 100:
                return True
            else:
                return False

    def generate_report(self):
        return self.SaturationTest.results()

class SaturationTester():
    count = 0

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0
        # set up camera stream
        for k in range(4):
            self.cam = cv2.VideoCapture(k)
            if self.cam.isOpened():
                print("Panacast device found")
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
        for saturation_level in args:
            return_val = self.test_saturation(int(saturation_level))
            print(type(return_val))
            print(type(saturation_level))
            if return_val == int(saturation_level):
                print("Success")
                self.err_code[saturation_level] = 0
            else:
                print("Failure")
                self.err_code[saturation_level] = -1
            self.progress_percent += 33
            q.put(self.progress_percent)
        self.progress_percent = 100
        q.put(self.progress_percent)
        results.put(self.err_code)
        return self.err_code


    def test_saturation(self, saturation_level):
        print('entering test_saturation')
        # set saturation and capture frame after three second delay
        print("saturation to be tested: {}".format(saturation_level))
        self.cam.set(cv2.CAP_PROP_SATURATION, saturation_level)
        print("saturation set to: {}".format(self.cam.get(cv2.CAP_PROP_SATURATION)))
        t_end = time.time() + 3
        while True:
            ret, frame = self.cam.read()
            if time.time() > t_end:
                img = "test_saturation" + "_{}".format(SaturationTester.count) + ".png"
                cv2.imwrite(img, frame)
                print("{} captured".format(img))
                # print(frame)
                break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        saturation_average = np.average(s)

        print("Saturation average: {}".format(saturation_average))
        current_saturation = self.cam.get(cv2.CAP_PROP_SATURATION)
        print("Current saturation: {}".format(current_saturation))
        SaturationTester.count += 1
        #reset saturation to default
        self.cam.set(cv2.CAP_PROP_SATURATION, 141)

        return current_saturation

if __name__ == "__main__":
    t = Saturation()
    args = t.get_args()
    q = Queue()
    results = Queue()
    wait_q = Queue()
    t.run(args, q, results, wait_q)

    print("Generating report...")
    print(t.generate_report())

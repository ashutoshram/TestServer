import os
import time
import platform
import numpy as np
import sys
import cv2
from queue import Queue

production = False
debug = True 
if not production:
    import AbstractTestClass as ATC
    # import webcamPy as wpy
else:
    import eos.scripts.AbstractTestClass as ATC
    import eos.scripts.webcamPy as wpy

def dbg_print(*args):
    if debug: 
        print("".join(map(str, args)))

class Sharpness(ATC.AbstractTestClass):
    def __init__(self):
        self.SharpnessTest = None

    def get_args(self):
        return [0, 110, 128, 255, 193]

    def run(self, args, q, results, wait_q):
        self.SharpnessTest = SharpnessTester()
        self.SharpnessTest.test(args, q, results)
        print("Sharpness.run: waiting for wait_q")
        #got = wait_q.get()

    def get_progress(self):
        if self.SharpnessTest is None:
            return 0

        return self.SharpnessTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "Sharpness Test"
    
    def is_done(self):
        if self.SharpnessTest is None:
            return False
        else:
            if self.SharpnessTest.progress() == 100:
                return True
            else:
                return False

    def generate_report(self):
        return self.SharpnessTest.results()

class SharpnessTester():
    count = 0

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0 
        # set up camera stream
        self.cam = cv2.VideoCapture(2)
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
        for sharpness_level in args:
            return_val = self.test_sharpness(int(sharpness_level))
            print(type(return_val))
            print(type(sharpness_level))
            if return_val == int(sharpness_level):
                print("Success")
                self.err_code[sharpness_level] = 0
            else:
                print("Failure")
                self.err_code[sharpness_level] = -1
            self.progress_percent += 20
            q.put(self.progress_percent)
            # time.sleep(3)
        self.progress_percent = 100
        results.put(self.err_code)
        # time.sleep(3)
        q.put(self.progress_percent)
        return self.err_code

    def test_sharpness(self, sharpness_level):
        print('entering test_sharpness')
        # set sharpness and capture frame after three second delay
        self.cam.set(cv2.CAP_PROP_SHARPNESS, sharpness_level)
        t_end = time.time() + 3
        while True:
            ret, frame = self.cam.read()
            if time.time() > t_end:
                img = "test_sharpness" + "_{}".format(SharpnessTester.count) + ".png"
                cv2.imwrite(img, frame)
                print("{} captured".format(img))
                # print(frame)
                break

        current_sharpness = self.cam.get(cv2.CAP_PROP_SHARPNESS)
        print("Current sharpness: {}".format(current_sharpness))
        SharpnessTester.count += 1
        return current_sharpness

if __name__ == "__main__":
    t = Sharpness()
    args = t.get_args()
    q = Queue()
    results = Queue()
    wait_q = Queue()
    t.run(args, q, results, wait_q)

    print("Generating report...")
    print(t.generate_report())

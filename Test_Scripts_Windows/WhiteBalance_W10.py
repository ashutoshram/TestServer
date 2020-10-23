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
        red, green, blue = ([] for i in range(3))
        for whiteBal_level in args:
            r, g, b = self.test_whiteBal(int(whiteBal_level))
            red.append(r)
            green.append(g)
            blue.append(b)
            self.progress_percent += 33
            q.put(self.progress_percent)

        # check if correct # of arguments is returned
        if len(args) != len(red) or len(args) != len(green) or len(args) != len(blue):
            print("Something went wrong: # of color values in each channel does not match # of inputs")
            sys.exit(1)

        for i, j, k, whiteBal_level in zip(range(len(red)), range(len(green)), range(len(blue)), args):
            if i == len(red) - 1:
                if red[i] > red[i - 1] and green[j] < green[j - 1] and blue[k] < blue[k - 1]:
                    self.err_code[whiteBal_level] = 0
                else:
                    self.err_code[whiteBal_level] = -1
            else:
                if red[i] < red[i + 1] and green[j] > green[j + 1] and blue[k] > blue[k + 1]:
                    self.err_code[whiteBal_level] = 0
                else:
                    self.err_code[whiteBal_level] = -1

        self.progress_percent = 100
        q.put(self.progress_percent)
        results.put(self.err_code)

        return self.err_code

    def test_whiteBal(self, whiteBal_level):
        print('entering test_whiteBal')
        # set white balance and capture frame after three second delay
        self.cam.set(cv2.CAP_PROP_TEMPERATURE, whiteBal_level)
        # current_whiteBal = self.cam.get(cv2.CAP_PROP_TEMPERATURE)

        t_end = time.time() + 3
        while True:
            ret, frame = self.cam.read()
            if time.time() > t_end:
                img = "test_wb" + "_{}".format(WhiteBalTester.count) + ".png"
                cv2.imwrite(img, frame)
                print("{} captured".format(img))
                # print(frame)
                break

        # check individual channel values
        b, g, r = cv2.split(frame)
        b = np.average(b)
        g = np.average(g)
        r = np.average(r)
        print("Channel values:")
        for channel, label in zip((r, g, b), ("r", "g", "b")):
            print("{}: {}".format(label, channel))

        # print("Current white balance temperature: {}".format(current_whiteBal))
        WhiteBalTester.count += 1
        return r, g, b

if __name__ == "__main__":
    t = WhiteBal()
    args = t.get_args()
    q = Queue()
    results = Queue()
    wait_q = Queue()
    t.run(args, q, results, wait_q)

    print("Generating report...")
    print(t.generate_report())

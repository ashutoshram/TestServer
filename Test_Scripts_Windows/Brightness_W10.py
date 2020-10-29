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

class Brightness(ATC.AbstractTestClass):
    def __init__(self):
        self.BrightnessTest = None

    def get_args(self):
        return [0, 128, 255]

    def run(self, args, q, results, wait_q):
        self.BrightnessTest = BrightnessTester()
        self.BrightnessTest.test(args, q, results)
        # print("Brightness.run: waiting for wait_q")
        # got = wait_q.get()
        # print("Brightness.run: got %s" % repr(got))

    def get_progress(self):
        if self.BrightnessTest is None:
            return 0

        return self.BrightnessTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "Brightness Test"
    
    def is_done(self):
        if self.BrightnessTest is None:
            return False
        else:
            if self.BrightnessTest.progress() == 100:
                return True
            else:
                return False

    def generate_report(self):
        return self.BrightnessTest.results()

class BrightnessTester():
    count = 0

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0
        # set up camera stream
        for k in range(4):
            self.cam = cv2.VideoCapture(k)
            if self.cam.isOpened():
                print("\nPanacast device found: ({})\n".format(k))
                break

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # check if camera stream exists
        if self.cam is None:
            print('cv2.VideoCapture unsuccessful')
            sys.exit(1)

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args, q, results):
        luma_list = []
        for brightness_level in args:
            return_val, luma = self.test_brightness(int(brightness_level))
            luma_list.append(luma)
            self.progress_percent += 33
            q.put(self.progress_percent)
        
        # hard-coded for now
        if luma_list[1] > luma_list[0] and luma_list[2] > luma_list[1]:
            for bright in args:
                self.err_code[bright] = 0
        else:
            for bright in args:
                self.err_code[bright] = -1

        self.progress_percent = 100
        q.put(self.progress_percent)
        # print("Test is Done, Putting err_code in the results")
        results.put(self.err_code)

        return self.err_code

    def test_brightness(self, brightness_level):
        print("\nBrightness: {}".format(brightness_level))

        # set brightness and capture frame after three second delay
        self.cam.set(cv2.CAP_PROP_BRIGHTNESS, brightness_level)
        t_end = time.time() + 3
        while True:
            ret, frame = self.cam.read()
            if time.time() > t_end:
                img = "test_brightness" + "_{}".format(BrightnessTester.count) + ".png"
                cv2.imwrite(img, frame)
                # print("{} captured".format(img))
                # print(frame)
                break

        # check individual channel values
        b, g, r = cv2.split(frame)
        # print("Channel values:")
        for channel, label in zip((r, g, b), ("r", "g", "b")):
            print("{}:          {}".format(label, np.average(channel)))
        
        # convert to grayscale and calculate luma
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        luma = np.average(f)
        print("luma:       {}".format(luma))        
        BrightnessTester.count += 1
        #reset brightness to default
        self.cam.set(cv2.CAP_PROP_BRIGHTNESS, 111)

        return brightness_level, luma

if __name__ == "__main__":
    t = Brightness()
    args = t.get_args()
    q = Queue()
    results = Queue()
    wait_q = Queue()
    t.run(args, q, results, wait_q)

    print("\nGenerating report...")
    print("{}\n".format(t.generate_report()))

import os
import time
import platform
import numpy as np
import sys
import cv2

production = True
debug = False 
if not production:
    import AbstractTestClass as ATC
    import webcamPy as wpy
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
        print("Brightness.run: waiting for wait_q")
        got = wait_q.get()
        print("Brightness.run: got %s" % repr(got))

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

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0 
        self.cam = wpy.Webcam()
        #print("hello")
        if not self.cam.open(3840, 1080, 30.0, "YUY2"):
            print("PanaCast cannot be opened!!")
        print("opened panacast device")

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
        if luma_list[1] > luma_list[0] and luma_list[2] > luma_list[1]:
            for bright in args:
                self.err_code[bright] = 0
        else:
            for bright in args:
                self.err_code[bright] = -1
        self.progress_percent = 100
        q.put(self.progress_percent)
        print("Test is Done, Putting err_code in the results")
        results.put(self.err_code)
        #self.cam = None
        return self.err_code


    def test_brightness(self, brightness_level):
        print('entering test_brightness')
        if not self.cam.setCameraControlProperty('brightness', brightness_level):
            print('test_brightness: cannot set brightness')
        time.sleep(3)
        f = self.cam.getFrame()
        f = cv2.cvtColor(f, cv2.COLOR_YUV2GRAY_YUY2)
        luma = np.average(f)
        print(brightness_level, luma)
        current_brightness = self.cam.getCameraControlProperty('brightness')[0]
        default_brightness = self.cam.getCameraControlProperty('brightness')[3]
        self.cam.setCameraControlProperty('brightness', default_brightness)
        #print(current_brightness)
        return current_brightness, luma
    


if __name__ == "__main__":
	t = Brightness()
	args = t.get_args()
	t.run(args)
	print(t.generate_report())

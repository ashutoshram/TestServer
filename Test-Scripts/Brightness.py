import os
import time
import platform
import numpy as np
import sys

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

    def run(self, args):
        self.BrightnessTest = BrightnessTester()
        return self.BrightnessTest.test(args)

    def get_progress(self):
        if self.BrightnessTest is None:
            return 0
        return self.BrightnessTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "UVC Test"
    
    def is_done(self):
        if self.BrightnessTest is None:
            return False
        elif self.BrightnessTest.progress() == 100:
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
        print("hello")
        if not self.cam.open(3840, 1080, 30.0, "YUY2"):
            print("PanaCast cannot be opened!!")
            #sys.exit(1)
        print("opened panacast device")

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        for brightness_level in args:
            return_val = self.test_brightness(int(brightness_level))
            if return_val == brightness_level:
                self.err_code[brightness_level] = 0
            else:
                self.err_code[brightness_level] = -1
            time.sleep(0.1)
        return self.err_code


    def test_brightness(self, brightness_level):
        print('entering test_brightness')
        if not self.cam.setCameraControlProperty('brightness', brightness_level):
            print('test_brightness: cannot set brightness')
        #current_brightness = self.cam.getCameraControlProperty('brightness')[0]
        #default_brightness = self.cam.getCameraControlProperty('brightness')[3]
        #self.cam.setCameraControlProperty('contrast', default_brightness)
        current_brightness = 1
        print(current_brightness)
        return current_brightness


if __name__ == "__main__":
	t = Brightness()
	args = t.get_args()
	t.run(args)
	print(t.generate_report())

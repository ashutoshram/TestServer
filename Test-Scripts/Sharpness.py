import os
import time
import platform
import numpy as np
import sys

production = False
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

class Sharpness(ATC.AbstractTestClass):

    def __init__(self):
        self.SharpnessTest = None

    def get_args(self):
        return [0, 110, 128, 255, 193]

    def run(self, args):
        self.SharpnessTest = SharpnessTester()
        return self.SharpnessTest.test(args)

    def get_progress(self):
        if self.SharpnessTest is None:
            return 0
        return self.SharpnessTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "UVC Test"
    
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
        for sharpness_level in args:
            return_val = self.test_sharpness(int(sharpness_level))
            print(type(return_val))
            print(type(sharpness_level))
            if return_val == int(sharpness_level):
                print("Hello")
                self.err_code[sharpness_level] = 0
            else:
                print("goodbye")
                self.err_code[sharpness_level] = -1
            self.progress_percent += 33
        self.progress_percent = 100
        return self.err_code


    def test_sharpness(self, sharpness_level):
        print('entering test_sharpness')
        if not self.cam.setCameraControlProperty('sharpness', sharpness_level):
            print('test_sharpness: cannot set sharpness')
        current_sharpness = self.cam.getCameraControlProperty('sharpness')[0]
        default_sharpness = self.cam.getCameraControlProperty('sharpness')[3]
        self.cam.setCameraControlProperty('hdr', default_sharpness)
        #print(current_sharpness)
        return current_sharpness


if __name__ == "__main__":
	t = Sharpness()
	args = t.get_args()
	t.run(args)
	print(t.generate_report())

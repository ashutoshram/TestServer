import os
import time
import cv2
import platform
import numpy as np
import webcamPy as wpy

production = False
debug = False 
if not production:
    import AbstractTestClass as ATC
else:
    import eos.scripts.AbstractTestClass as ATC

def dbg_print(*args):
    if debug: print("".join(map(str, args)))

class Contrast(ATC.AbstractTestClass):

    def __init__(self):
        self.ContrastTest = ContrastTester()

    def get_args(self):
        return [0, 95, 191]

    def run(self, args):
        return self.ContrastTest.test(args)

    def get_progress(self):
        return self.ContrastTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_name(self):
        return "Contrast Test"
    
    def is_done(self):
        if self.ContrastTest.progress() == 100:
            return True
        else:
            return False

    def generate_report(self):
        return self.ContrastTest.results()


class ContrastTester():

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0
        self.cam = wpy.Webcam()
        if not self.cam.open(3840, 1080, 30.0, "YUY2"):
            print("PanaCast cannot be opened!!")
            sys.exit(1)

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        print(args)
        for contrast_level in args:
            return_val = self.test_contrast(int(contrast_level))
            if return_val == contrast_level:
                self.err_code[contrast_level] = 0
            else:
                self.err_code[contrast_level] = -1
            self.progress_percent += 33
        self.progress_percent = 100 
        return self.err_code


    def test_contrast(self,contrast_level):
        self.cam.setCameraControlProperty('contrast', contrast_level)
        current_contrast = self.cam.getCameraControlProperty('contrast')[0]
        default_contrast = self.cam.getCameraControlProperty('contrast')[3]
        self.cam.setCameraControlProperty('contrast', default_contrast)
        print(current_contrast)
        return current_contrast



if __name__ == "__main__":
	t = Contrast()
	args = t.get_args()
	t.run(args)
	#print(t.get_progress())
	#print(t.is_done())
	#print(t.generate_report())

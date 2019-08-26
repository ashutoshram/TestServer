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

class Saturation(ATC.AbstractTestClass):

    def __init__(self):
        self.SaturationTest = None

    def get_args(self):
        return [128, 136, 160, 176, 155]

    def run(self, args, q, results):
        self.SaturationTest = SaturationTester()
        return self.SaturationTest.test(args, q, results)

    def get_progress(self):
        if self.SaturationTest is None:
            return 0
        return self.SaturationTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "UVC Test"
    
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

    def test(self, args, q, results):
        for saturation_level in args:
            return_val = self.test_saturation(int(saturation_level))
            print(type(return_val))
            print(type(saturation_level))
            if return_val == int(saturation_level):
                print("Hello")
                self.err_code[saturation_level] = 0
            else:
                print("goodbye")
                self.err_code[saturation_level] = -1
            self.progress_percent += 33
            q.put(self.progress_percent)
            q.task_done()
        self.progress_percent = 100
        q.put(self.progress_percent)
        results.put("DONE")
        results.put(self.err_code)
        return self.err_code


    def test_saturation(self, saturation_level):
        print('entering test_saturation')
        if not self.cam.setCameraControlProperty('saturation', saturation_level):
            print('test_saturation: cannot set saturation')
        time.sleep(3)
        f = self.cam.getFrame()
        bgr = cv2.cvtColor(f, cv2.COLOR_YUV2BGR_YUY2)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        saturation_average = np.average(s)
        print(saturation_average)
        current_saturation = self.cam.getCameraControlProperty('saturation')[0]
        default_saturation = self.cam.getCameraControlProperty('saturation')[3]
        self.cam.setCameraControlProperty('hdr', default_saturation)
        #print(current_saturation)
        return current_saturation


if __name__ == "__main__":
	t = Saturation()
	args = t.get_args()
	t.run(args)
	print(t.generate_report())

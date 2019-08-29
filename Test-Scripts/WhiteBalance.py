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

class WhiteBal(ATC.AbstractTestClass):

    def __init__(self):
        self.WhiteBalTest = None

    def get_args(self):
        return [0, 2122, 5000 , 6036 , 6500]

    def run(self, args, q, results, wait_q):
        self.WhiteBalTest = WhiteBalTester()
        self.WhiteBalTest.test(args, q, results)
        print("Whitebalance.run: waiting for wait_q")
        got = wait_q.get()
        print("Whitebalance.run: got %s" % repr(got))

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
        for whiteBal_level in args:
            return_val = self.test_whiteBal(int(whiteBal_level))
            print(type(return_val))
            print(type(whiteBal_level))
            if return_val == int(whiteBal_level):
                print("Hello")
                self.err_code[whiteBal_level] = 0
            else:
                print("goodbye")
                self.err_code[whiteBal_level] = -1
            self.progress_percent += 33
            q.put(self.progress_percent)
        self.progress_percent = 100
        q.put(self.progress_percent)
        results.put(self.err_code)
        return self.err_code


    def test_whiteBal(self, whiteBal_level):
        print('entering test_whiteBal')
        if not self.cam.setCameraControlProperty('whitebalance', whiteBal_level):
            print('test_whiteBal: cannot set whiteBal')
        current_whiteBal = self.cam.getCameraControlProperty('whitebalance')[0]
        default_whiteBal = self.cam.getCameraControlProperty('whitebalance')[3]
        self.cam.setCameraControlProperty('whitebalance', default_whiteBal)
        #print(current_whiteBal)
        return current_whiteBal


if __name__ == "__main__":
	t = WhiteBal()
	args = t.get_args()
	t.run(args)
	print(t.generate_report())

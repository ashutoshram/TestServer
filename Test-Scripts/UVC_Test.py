import os
import time
import cv2
import uvc
import platform
import numpy as np

production = True
debug = False 
if not production:
    import AbstractTestClass as ATC
else:
    import eos.scripts.AbstractTestClass as ATC

def dbg_print(*args):
    if debug: print("".join(map(str, args)))

class UVC(ATC.AbstractTestClass):

    def __init__(self):
        self.UVCTest = UVCTester()

    def get_args(self):
        return ['all']

    def run(self, args):
        return self.UVCTest.test(args)

    def get_progress(self):
        return self.UVCTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_name(self):
        return "UVC Test"
    
    def is_done(self):
        if self.UVCTest.progress() == 100:
            return True
        else:
            return False

    def generate_report(self):
        return self.UVCTest.results()


class UVCTester():

    def __init__(self):
        self.progress_percent = 0 
        self.os_type = platform.system()
        self.device_list = uvc.device_list()
        if self.os_type == 'Linux':
            self.cap = self.uvc.Capture(device_list[0]['uid'])

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        print(cap.frame_mode)
        cap.frame_mode = (3840, 1088, 30)



if __name__ == "__main__":
	t = UVC()
	args = t.get_args()
	t.run(args)
	print(t.get_progress())
	print(t.is_done())
	print(t.generate_report())

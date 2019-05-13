import os
import time
import cv2
import platform
import numpy as np

production = False
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
        return [64, 128, 192]

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
        self.err_code = {}
        self.progress_percent = 0 
        self.os_type = platform.system()
        self.cap = cv2.VideoCapture(0)

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        for brightness_level in args:
            test_brightness(brightness_level)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, args)
        now = time.time()
        while True:

            ret, frame = cap.read()
            cv2.imshow("input", frame)

            
            if (time.time() - now) > 5.0:
                break

            key = cv2.waitKey(10)
            if key == 27:
                break

        cv2.destroyAllWindows()
        cap.release()

        



if __name__ == "__main__":
	t = UVC()
	args = t.get_args()
	t.run(args)
	print(t.get_progress())
	print(t.is_done())
	print(t.generate_report())

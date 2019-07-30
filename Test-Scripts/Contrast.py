import os
import sys
import time
import cv2
import platform
import numpy as np

production = True
debug = True 
if not production:
    import AbstractTestClass as ATC
    import webcamPy as wpy
else:
    import eos.scripts.AbstractTestClass as ATC
    import eos.scripts.webcamPy as wpy

def dbg_print(*args):
    if debug: print("".join(map(str, args)))

class Contrast(ATC.AbstractTestClass):

    def __init__(self):
        self.ContrastTest = None

    def get_args(self):
        #return [0, 95, 191]
        return [0, 95, 191]

    def run(self, args, q, results):
        self.ContrastTest = ContrastTester()
        return self.ContrastTest.test(args, q, results)

    def get_progress(self):
        return self.ContrastTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

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
            #sys.exit(1)

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args, queue, results):
        print(args)
        otsu_list = []
        for contrast_level in args:
            return_val, otsu = self.test_contrast(int(contrast_level))
            otsu_list.append(otsu)
            self.progress_percent += 33
            queue.put(self.progress_percent)
            queue.task_done()
        if self.check(otsu_list[0], otsu_list[1]) and self.check(otsu_list[1], otsu_list[2]):
            for contrast_level in args:
                self.err_code[contrast_level] = 0
        else:
            for contrast_level in args:
                self.err_code[contrast_level] = -1
        self.progress_percent = 100 
        queue.put(self.progress_percent)
        results.put("DONE")
        results.put(self.err_code)

        return self.err_code

    def check(self, otsu1, otsu2):
        diff = otsu1 - otsu2
        if abs(diff) > 1.0:
            return True
        else:
            return False
        

    def test_contrast(self,contrast_level):
        if not self.cam.setCameraControlProperty('contrast', contrast_level):
            print("Contrast cannot be set!")
        time.sleep(3)
        f = self.cam.getFrame()
        #f = cv2.cvtColor(f, cv2.COLOR_YUV2BGR_YUY2)
        f = cv2.cvtColor(f, cv2.COLOR_YUV2GRAY_YUY2)
        ret, thresh = cv2.threshold(f, 0, 255, cv2.THRESH_OTSU)
        otsu = np.average(thresh)
        print(otsu)
        current_contrast = self.cam.getCameraControlProperty('contrast')[0]
        default_contrast = self.cam.getCameraControlProperty('contrast')[3]
        self.cam.setCameraControlProperty('contrast', default_contrast)
        print(current_contrast)
        return current_contrast, otsu



if __name__ == "__main__":
	t = Contrast()
	args = t.get_args()
	t.run(args)
	#print(t.get_progress())
	#print(t.is_done())
	print(t.generate_report())

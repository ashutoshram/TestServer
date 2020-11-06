import os
import time
import platform
import numpy as np
import sys
import cv2
from queue import Queue
from datetime import date
import AbstractTestClass as ATC
import pprint as p

debug = True
current = date.today()
path = os.getcwd()

filename = "{}_contrast.log".format(current)
file_path = os.path.join(path+"\\contrast", filename)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"\\contrast"):
    os.makedirs(path+"\\contrast")

log_file = open(file_path, "a")

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

class Contrast(ATC.AbstractTestClass):
    def __init__(self):
        self.ContrastTest = None

    def get_args(self):
        return [0, 95, 191]

    def run(self, args, q, results, wait_q):
        self.ContrastTest = ContrastTester()
        self.ContrastTest.test(args, q, results)
        # print("Contrast.run: waiting for wait_q")
        # got = wait_q.get()
        # print("Contrast.run: got %s" % repr(got))

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
    count = 0

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0
        # set up camera stream
        for k in range(4):
            self.cam = cv2.VideoCapture(k)
            if self.cam.isOpened():
                log_print(55*"=")
                log_print("\nPanacast device found:  {}".format(k))
                break

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # check if camera stream exists
        if self.cam is None:
            log_print('cv2.VideoCapture unsuccessful')
            sys.exit(1)
        # print(self.cam)

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args, q, results):
        # print(args)
        otsu_list = []
        for contrast_level in args:
            return_val, otsu = self.test_contrast(int(contrast_level))
            otsu_list.append(otsu)
            self.progress_percent += 33
            q.put(self.progress_percent)
        
        # hard-coded for now
        if self.check(otsu_list[0], otsu_list[1]) and self.check(otsu_list[1], otsu_list[2]):
            for contrast_level in args:
                self.err_code[contrast_level] = 0
        else:
            for contrast_level in args:
                self.err_code[contrast_level] = -1

        self.progress_percent = 100 
        q.put(self.progress_percent)
        results.put(self.err_code)

        return self.err_code

    def check(self, otsu1, otsu2):
        diff = otsu1 - otsu2
        if abs(diff) > 1.0:
            return True
        else:
            return False
        
    def test_contrast(self, contrast_level):
        # set contrast and capture frame after three second delay
        log_print("\nContrast level:         {}".format(contrast_level))
        self.cam.set(cv2.CAP_PROP_CONTRAST, contrast_level)
        current_contrast = self.cam.get(cv2.CAP_PROP_CONTRAST)

        t_end = time.time() + 3
        while True:
            try:
                ret, frame = self.cam.read()
                if time.time() > t_end:
                    # capture and save frame as a .png to contrast folder
                    img = "{}_contrast_{}.png".format(current, contrast_level)
                    img = os.path.join(path+"\\contrast", img)
                    cv2.imwrite(img, frame)
                    # print("{} captured".format(img))
                    # print(frame)
                    break
            
            except Exception as e:
                log_print("{}".format(e))
                sys.exit(1)

        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(f, 0, 255, cv2.THRESH_OTSU)
        otsu = np.average(thresh)
        log_print("Otsu threshold:         {}".format(otsu))
        ContrastTester.count += 1
        current_contrast = self.cam.get(cv2.CAP_PROP_CONTRAST)
        #reset contrast to default
        self.cam.set(cv2.CAP_PROP_CONTRAST, 95)

        return current_contrast, otsu

if __name__ == "__main__":
    t = Contrast()
    args = t.get_args()
    q = Queue()
    results = Queue()
    wait_q = Queue()
    t.run(args, q, results, wait_q)

    # print(t.get_progress())
    # print(t.is_done())
    log_print("\nGenerating report...")
    report = p.pformat(t.generate_report())
    log_print("{}\n".format(report))
    log_file.close()

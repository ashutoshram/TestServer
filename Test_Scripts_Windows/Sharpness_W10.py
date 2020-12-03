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

# production = False
# debug = True 
# if not production:
#     import AbstractTestClass as ATC
#     # import webcamPy as wpy
# else:
#     import eos.scripts.AbstractTestClass as ATC
#     import eos.scripts.webcamPy as wpy

debug = True
current = date.today()
path = os.getcwd()

filename = "{}_sharpness.log".format(current)
file_path = os.path.join(path+"\\sharpness", filename)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"\\sharpness"):
    os.makedirs(path+"\\sharpness")

log_file = open(file_path, "a")

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

class Sharpness(ATC.AbstractTestClass):
    def __init__(self):
        self.SharpnessTest = None

    def get_args(self):
        return [0, 110, 128, 255, 193]

    def run(self, args, q, results, wait_q):
        self.SharpnessTest = SharpnessTester()
        self.SharpnessTest.test(args, q, results)
        # print("Sharpness.run: waiting for wait_q")
        #got = wait_q.get()

    def get_progress(self):
        if self.SharpnessTest is None:
            return 0

        return self.SharpnessTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "Sharpness Test"
    
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
    count = 0

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0 
        # set up camera stream
        for k in range(4):
            self.cam = cv2.VideoCapture(k)
            if self.cam.isOpened():
                log_print(55*"=")
                log_print("\nPanacast device found:  {}\n".format(k))
                break

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # check if camera stream exists
        if self.cam is None:
            log_print('cv2.VideoCapture unsuccessful')
            sys.exit(1)

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args, q, results):
        var_list = []
        for sharpness_level in args:
            return_val = self.test_sharpness(int(sharpness_level))
            var_list.append(return_val)
            self.progress_percent += 20
            q.put(self.progress_percent)
        
        # check if correct # of arguments is returned
        if len(args) != len(var_list):
            log_print("Something went wrong: # of sharpness values does not match # of inputs")
            sys.exit(1)

        for i, sharpness_level in zip(range(len(var_list)), args):
            if i == len(var_list) - 2:
                if var_list[i] > var_list[i + 1]:
                    self.err_code[sharpness_level] = 0
                else:
                    self.err_code[sharpness_level] = -1
            elif i == len(var_list) - 1:
                if var_list[i] < var_list[i - 1]:
                    self.err_code[sharpness_level] = 0
                else:
                    self.err_code[sharpness_level] = -1
            else:
                if var_list[i] < var_list[i + 1]:
                    self.err_code[sharpness_level] = 0
                else:
                    self.err_code[sharpness_level] = -1

        self.progress_percent = 100
        results.put(self.err_code)
        q.put(self.progress_percent)

        return self.err_code

    def test_sharpness(self, sharpness_level):
        # print('entering test_sharpness')
        # set sharpness and capture frame after three second delay
        log_print("Sharpness to test:      {}".format(sharpness_level))
        self.cam.set(cv2.CAP_PROP_SHARPNESS, sharpness_level)
        current_sharpness = self.cam.get(cv2.CAP_PROP_SHARPNESS)
        t_end = time.time() + 3

        while True:
            try:
                ret, frame = self.cam.read()
                if time.time() > t_end:
                    img = "{}_sharpness_{}.png".format(current, SharpnessTester.count)
                    img = os.path.join(path+"\\sharpness", img)
                    cv2.imwrite(img, frame)
                    # print("{} captured".format(img))
                    # print(frame)
                    break
            except cv2.error as e:
                log_print("{}".format(e))
                log_print("Panacast device crashed, rebooting...")
                os.system("adb reboot")
                time.sleep(20)
                return -1
        
        f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(f, cv2.CV_64F).var()
        log_print("Laplacian variance:     {}\n".format(variance))
        SharpnessTester.count += 1
        #reset sharpness to default
        self.cam.set(cv2.CAP_PROP_SHARPNESS, 144)

        return variance

if __name__ == "__main__":
    t = Sharpness()
    args = t.get_args()
    q = Queue()
    results = Queue()
    wait_q = Queue()
    t.run(args, q, results, wait_q)

    log_print("\nGenerating report...")
    report = p.pformat(t.generate_report())
    log_print("{}\n".format(report))
    log_file.close()

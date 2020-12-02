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
# debug = False 
# if not production:
#     import AbstractTestClass as ATC
#     # import webcamPy as wpy
# else:
#     import eos.scripts.AbstractTestClass as ATC
#     import eos.scripts.webcamPy as wpy

debug = True
current = date.today()
path = os.getcwd()

filename = "{}_whitebalance.log".format(current)
file_path = os.path.join(path+"\\whitebalance", filename)
# create directory for log and .png files if it doesn't already exist
if not os.path.exists(path+"\\whitebalance"):
    os.makedirs(path+"\\whitebalance")

log_file = open(file_path, "a")

def log_print(args):
    msg = args + "\n"
    log_file.write(msg)
    if debug is True: 
        print(args)

class WhiteBal(ATC.AbstractTestClass):
    def __init__(self):
        self.WhiteBalTest = None

    def get_args(self):
        # return [0, 2122, 5000 , 6036 , 6500]
        return [0, 5000, 6500]

    def run(self, args, q, results, wait_q):
        self.WhiteBalTest = WhiteBalTester()
        self.WhiteBalTest.test(args, q, results)
        # print("Whitebalance.run: waiting for wait_q")
        # got = wait_q.get()
        # print("Whitebalance.run: got %s" % repr(got))

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

        # self.cam = cv2.VideoCapture(0)
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
        red, green, blue = ([] for i in range(3))
        for whiteBal_level in args:
            r, g, b = self.test_whiteBal(int(whiteBal_level))
            red.append(r)
            green.append(g)
            blue.append(b)
            self.progress_percent += 33
            q.put(self.progress_percent)

        # check if correct # of arguments is returned
        if len(args) != len(red) or len(args) != len(green) or len(args) != len(blue):
            log_print("Something went wrong: # of color values in each channel does not match # of inputs")
            sys.exit(1)

        for i, j, k, whiteBal_level in zip(range(len(red)), range(len(green)), range(len(blue)), args):
            if i == len(red) - 1:
                if red[i] > red[i - 1] and green[j] < green[j - 1] and blue[k] < blue[k - 1]:
                    self.err_code[whiteBal_level] = 0
                else:
                    self.err_code[whiteBal_level] = -1
            else:
                if red[i] < red[i + 1] and green[j] > green[j + 1] and blue[k] > blue[k + 1]:
                    self.err_code[whiteBal_level] = 0
                else:
                    self.err_code[whiteBal_level] = -1

        self.progress_percent = 100
        q.put(self.progress_percent)
        results.put(self.err_code)

        return self.err_code

    def test_whiteBal(self, whiteBal_level):
        # print('entering test_whiteBal')
        # set white balance and capture frame after three second delay
        log_print("\nWhite balance:          {}k".format(whiteBal_level))
        self.cam.set(cv2.CAP_PROP_TEMPERATURE, whiteBal_level)
        # current_whiteBal = self.cam.get(cv2.CAP_PROP_TEMPERATURE)

        t_end = time.time() + 3
        while True:
            try:
                ret, frame = self.cam.read()
                if time.time() > t_end:
                    # capture and save frame as a .png to whitebalance folder
                    img = "{}_wb_{}.png".format(current, whiteBal_level)
                    img = os.path.join(path+"\\whitebalance", img)
                    cv2.imwrite(img, frame)
                    # print("{} captured".format(img))
                    # print(frame)
                    break
            except cv2.error as e:
                log_print("{}".format(e))
                log_print("Panacast device crashed, rebooting...")
                os.system("adb reboot")
                time.sleep(15)
                return -1

        # check individual channel values
        b, g, r = cv2.split(frame)
        b = np.average(b)
        g = np.average(g)
        r = np.average(r)
        # print("Channel values:")
        for channel, label in zip((r, g, b), ("r", "g", "b")):
            log_print("{}:                      {}".format(label, channel))

        # print("Current white balance temperature: {}".format(current_whiteBal))
        WhiteBalTester.count += 1
        #reset white balance to default
        self.cam.set(cv2.CAP_PROP_TEMPERATURE, 3700)

        return r, g, b

if __name__ == "__main__":
    t = WhiteBal()
    args = t.get_args()
    q = Queue()
    results = Queue()
    wait_q = Queue()
    t.run(args, q, results, wait_q)

    log_print("\nGenerating report...")
    report = p.pformat(t.generate_report())
    log_print("{}\n".format(report))
    log_file.close()

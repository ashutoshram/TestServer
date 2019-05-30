import os
import uuid
import time
import cv2
import numpy as np

production = True 
debug = False
if not production:
    import AbstractTestClass as ATC
else:
    import eos.scripts.AbstractTestClass as ATC

def dbg_print(*args):
    if debug: print("".join(map(str, args)))

class TimeWaste(ATC.AbstractTestClass):

    def __init__(self):
        self.TimeWaste = TimeWasteTester()

    def get_args(self):
        return ['5']

    def run(self, args):
        return self.TimeWaste.test(args, self.storage_path)

    def get_progress(self):
        return self.TimeWaste.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "TimeWaste"
    
    def is_done(self):
        if self.TimeWaste.progress() == 100:
            return True
        else:
            return False

    def generate_report(self):
        return self.TimeWaste.results()


class TimeWasteTester():

    def __init__(self):
        self.count = 0 
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(1)



    def test_sleep(self, secs, storage_path):
        print(storage_path)
        jamaal = 'time_waster_%d.txt' % (self.count)
        #freddy = 'time_waster_%d.jpg' % (self.count)
        #charles = storage_path + "/" + freddy
        charles = storage_path + "/" + jamaal
        print(charles)
        picture_ = open(charles, "w+")
        picture_.write("This was a success")
        now = time.time()
        #while True:
        #    ret, frame = self.cap.read()
        #    if (time.time() - now) > 10.0:
        #        break
        #cv2.imwrite(charles, frame)

        self.count += 1
        picture_.close()
        return 0

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args, storage_path):

        self.progress_percent = 0
        self.err_code = {}
        
        for sec in args:
            secs = int(sec)
            self.err_code[sec] = self.test_sleep(secs, storage_path)
            self.progress_percent += 25

        self.progress_percent = 100
            
        return self.err_code

if __name__ == "__main__":
    t = TimeWaste()
    tid = uuid.uuid4()
    tid = str(tid)
    name = "TimeWaste" 
    test_path = name + '_' + tid
    real_path = 'data/' + test_path
    os.makedirs(real_path)

    t.set_default_storage_path(real_path)
    args = t.get_args()
    t.run(args)
    print(t.get_progress())
    print(t.is_done())
    print(t.generate_report())

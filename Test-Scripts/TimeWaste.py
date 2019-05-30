import os
import time
import cv2
import numpy as np

production = False 
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
        return ['10','15','20', '30']

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

    def test_sleep(self, secs, storage_path):
        print(storage_path)
        picture_ = ('time_waster_%d.jpg' % (self.count))
        filename = storage_path + picture_ 
        time.sleep(secs)
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cv2.imwrite(filename, frame)
        self.count += 1
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
	args = t.get_args()
	t.run(args)
	print(t.get_progress())
	print(t.is_done())
	print(t.generate_report())

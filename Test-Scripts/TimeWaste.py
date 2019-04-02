import os
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
        return ['10','15','20', '30']

    def run(self, args):
        return self.TimeWaste.test(args)

    def get_progress(self):
        return self.TimeWaste.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_name(self):
        return "TimeWaste Test"
    
    def is_done(self):
        if self.TimeWaste.progress() == 100:
            return True
        else:
            return False

    def generate_report(self):
        return self.TimeWaste.results()


class TimeWasteTester():

    def test_sleep(secs):
        time.sleep(secs)
        return 0

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):

        self.progress_percent = 0
        
        for sec in args:
            secs = int(sec)
            self.err_code[sec] = self.test_sleep(secs)
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

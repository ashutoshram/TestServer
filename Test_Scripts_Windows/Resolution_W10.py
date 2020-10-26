import os
import sys
import time
import cv2
import numpy as np

production = False 
debug = True

if not production:
    import AbstractTestClass as ATC
else:
    import eos.scripts.AbstractTestClass as ATC

def dbg_print(*args):
    if debug: print("".join(map(str, args)))

class Resolution(ATC.AbstractTestClass):
    def __init__(self):
        self.ResTest = ResTester()

    def get_args(self):
        return ['all']

    def run(self, args):
        return self.ResTest.test(args)

    def get_progress(self):
        return self.ResTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path
    
    def get_storage_path(self):
        return self.storage_path

    def get_name(self):
        return "Res Test"
    
    def is_done(self):
        if self.ResTest.progress() == 100:
            return True
        else:
            return False

    def generate_report(self):
        return self.ResTest.results()

class ResTester():
    count = 0

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0

    def test_res(self, resolution, format_):
        if resolution == '4k':
            print("Resolution to be set to: 3840 x 1080")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        elif resolution == '1080p':
            print("Resolution to be set to: 1920 x 1080")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        elif resolution == '720p':
            print("Resolution to be set to: 1280 x 720")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        elif resolution == '480p':
            print("Resolution to be set to: 640 x 480")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
        if format_ == 'MJPG':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        if format_ == 'YUYV':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        if format_ == 'YUY2':
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUY2'))

        dbg_print('capturing at resolution: %d x %d' % (self.cam.get(cv2.CAP_PROP_FRAME_WIDTH), self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        t_end = time.time() + 3
        count = 0

        while True:
            ret, frame = self.cam.read()
            if time.time() > t_end:
                img = "test_resolution_{}_{}.png".format(format_, resolution)
                cv2.imwrite(img, frame)
                print("{} captured".format(img))
                break
            # dbg_print('got frame: count = %d' % count)
            count += 1

        h, w = frame.shape[:2]
        print("Height: {}   Width: {}".format(h, w))

        if resolution == '4k':
            if w == 3840 and h == 1080:
                return 0
            else: 
                return -1
        if resolution == '1080p':
            if w == 1920 and h == 1080:
                return 0
            else: 
                return -1
        if resolution == '720p':
            if w == 1280 and h == 720:
                return 0
            else: 
                return -1
        if resolution == '480p':
            if w == 640 and h == 480:
                return 0
            else: 
                return -1

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        # dbg_print('ResTester::test: args = %s' % repr(args))

        if 'all' in args: 
            tests = []
        else: 
            tests = list(map(int, args))

        self.err_code = {}
        # dbg_print('ResTester::test: tests = %s' % repr(tests))

        #dictionary of format, resolution, framerate
        frf = {'MJPG' : {'4k', '1080p', '720p'}, 'YUY2' : {'4k', '1080p', '720p'}}

        for format_ in frf:
            resdict = frf[format_]
            for resolution in resdict:
                print(resolution, format_)
                test_type = str(resolution) + ' x ' + str(format_)
                
                for k in range(4):
                    self.cam = cv2.VideoCapture(k)
                    if self.cam.isOpened():
                        print("Panacast device found: ({})".format(k))
                        break

                self.err_code[test_type] = self.test_res(resolution, format_)
                self.progress_percent += 15
                self.cam.release()

        self.progress_percent = 100

        # dbg_print('ResTester::test: err_code = %s' % repr(self.err_code))
        return self.err_code

if __name__ == "__main__":
	t = Resolution()
	args = t.get_args()
	t.run(args)
	print(t.get_progress())
	print(t.is_done())
	print(t.generate_report())

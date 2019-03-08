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

class FPS(ATC.AbstractTestClass):

    def __init__(self):
        self.FPSTest = FPSTester()

    def get_args(self):
        return ['all','22','27', '30']

    def run(self, args):
        return self.FPSTest.test(args)

    def get_progress(self):
        return self.FPSTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_name(self):
        return "FPS Test"
    
    def is_done(self):
        if self.FPSTest.progress() == 100:
            return True
        else:
            return False

    def generate_report(self):
        return self.FPSTest.results()



class FPSTester():

    def test_fps(self, framerate, resolution, format_):

        # open opencv capture device and set the fps
        # capture frames over 5 seconds and calculate fps

        cap = cv2.VideoCapture(0)

        if resolution == '4k':
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)

        if resolution == '1080p':
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        if resolution == '720p':
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
        if format_ == 'MJPG':
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        if format_ == 'YUYV':
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        cap.set(cv2.CAP_PROP_FPS, framerate)

        dbg_print('capturing at resolution = %d x %d' % (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        def decode_fourcc(v):
            v = int(v)
            return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])

        fourcc = cap.get(cv2.CAP_PROP_FOURCC)
        dbg_print('capturing format = %s' % decode_fourcc(fourcc))

        start = time.time()
        count = 0
        skip = 10

        while True:

            if (time.time() - start) > 5.0:
                break
            ret, frame = cap.read()
            dbg_print('got frame: count = %d' % count)

            if ret == -1:
                count = 0
                break
            skip -= 1
            if skip == 0:
                start = time.time()
                count = 0
                dbg_print('starting test')
            count += 1

        elapsed = time.time() - start
        dbg_print('elapsed = %f' % elapsed)
        calc_fps = float(count) / elapsed
        dbg_print('calc_fps = %f' % calc_fps)
        eps = 1.0

        abs_diff = abs(calc_fps - framerate)
        if  abs_diff < eps:
            dbg_print('success')
            return 0 # success

        else:
            dbg_print('failure : abs_diff = %f' % abs_diff)
            return -1 #failure

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        dbg_print('FPSTester::test: args = %s' % repr(args))

        if 'all' in args: 
            tests = [22, 27, 30]
        else: 
            tests = list(map(int, args))

        self.err_code = {}

        dbg_print('FPSTester::test: tests = %s' % repr(tests))

        #dictionary of format, resolution, framerate
        #frf = {'MJPG' : {'4k' : 22, '1080p' : 30, '720p' : 30 }, 'YUYV' : {'4k' : 30, '1080p' : 30, '720p' : 30 }}
        frf = {'YUYV' : {'4k' : 30, '1080p' : 27, '720p' : 30 }}

        self.progress_percent = 0 
        for format_ in frf:
            resdict = frf[format_]
            for resolution in resdict:
                framerate = resdict[resolution]
                print(framerate, resolution, format_)
                test_type = str(framerate) + ' x ' + str(resolution) + ' x ' + str(format_)
                self.err_code[test_type] = self.test_fps(framerate, resolution, format_)
                self.progress_percent += 33

        self.progress_percent = 100


        dbg_print('FPSTester::test: err_code = %s' % repr(err_code))
        return self.err_code




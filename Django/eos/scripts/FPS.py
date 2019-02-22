import os
import time
import cv2
import numpy as np

debug = False
if debug:
    import AbstractTestClass as ATC
else:
    import eos.scripts.AbstractTestClass as ATC

def dbg_print(*args, **kwargs):
    if debug: print("".join(map(str, args)), kwargs)

class FPS(ATC.AbstractTestClass):

    def get_args(self):
        return ['all','15','22','27', '30']

    def run(self, args):
        FPSTest = FPSTester()
        return FPSTest.test(args)

    def progress(self):
        return None

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_return_codes(self):
        return {0:'success', -1:'fail'}


class FPSTester():

    def test_fps(self, fps):

        # open opencv capture device and set the fps
        # capture frames over 5 seconds and calculate fps

        cap = cv2.VideoCapture(0)

        cap.set(cv2.CAP_PROP_FPS, fps)

        dbg_print('resolution = %d x %d' % (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        def decode_fourcc(v):
            v = int(v)
            return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])

        fourcc = cap.get(cv2.CAP_PROP_FOURCC)
        dbg_print('fourcc  = %s' % decode_fourcc(fourcc))

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

        abs_diff = abs(calc_fps - fps)
        if  abs_diff < eps:
            dbg_print('success')
            return 0 # success

        else:
            dbg_print('failure : abs_diff = %f' % abs_diff)
            return -1 #failure

    def test(self, args):
        dbg_print('FPSTester::test: args = %s' % repr(args))

        if 'all' in args: 
            tests = [15, 22, 27, 30]
        else: 
            tests = list(map(int, args))

        err_code = {}

        dbg_print('FPSTester::test: tests = %s' % repr(tests))
        for t in tests:
            err_code[t] = self.test_fps(t)

        dbg_print('FPSTester::test: err_code = %s' % repr(err_code))
        return err_code



if __name__ == "__main__":
    F = FPS()
    print(F.run(['all', '15']))




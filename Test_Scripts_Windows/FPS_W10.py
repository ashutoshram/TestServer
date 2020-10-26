import os
import platform
import time
import cv2
import numpy as np
import AbstractTestClass as ATC
debug = True 

def dbg_print(*args):
    if debug: print("".join(map(str, args)))

class FPS(ATC.AbstractTestClass):
    def __init__(self):
        self.FPSTest = FPSTester()

    def get_args(self):
        return ['all']

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
    
    def get_storage_path(self):
        return self.storage_path

    def generate_report(self):
        return self.FPSTest.results()

class FPSTester():
    def __init__(self):
        self.progress_percent = 0 
        self.os_type = platform.system()
        # set up camera stream
        self.cam = cv2.VideoCapture(2)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

        # check if camera stream exists
        if self.cam is None:
            print('cv2.VideoCapture unsuccessful')
            sys.exit(1)
        print(self.cam)

    def dump_props(self):
        fourcc_names = ['CAP_PROP_POS_MSEC', 'CAP_PROP_POS_FRAMES', 'CAP_PROP_POS_AVI_RATIO', 'CAP_PROP_FRAME_WIDTH', 'CAP_PROP_FRAME_HEIGHT', 
        'CAP_PROP_FPS', 'CAP_PROP_FOURCC', 'CAP_PROP_FRAME_COUNT', 'CAP_PROP_FORMAT', 'CAP_PROP_MODE', 'CAP_PROP_BRIGHTNESS', 'CAP_PROP_CONTRAST', 
        'CAP_PROP_SATURATION', 'CAP_PROP_HUE', 'CAP_PROP_GAIN', 'CAP_PROP_EXPOSURE', 'CAP_PROP_CONVERT_RGB', 'CAP_PROP_WHITE_BALANCE_BLUE_U', 
        'CAP_PROP_RECTIFICATION', 'CAP_PROP_MONOCHROME', 'CAP_PROP_SHARPNESS', 'CAP_PROP_AUTO_EXPOSURE', 'CAP_PROP_GAMMA', 'CAP_PROP_TEMPERATURE', 
        'CAP_PROP_TRIGGER', 'CAP_PROP_TRIGGER_DELAY', 'CAP_PROP_WHITE_BALANCE_RED_V', 'CAP_PROP_ZOOM', 'CAP_PROP_FOCUS', 'CAP_PROP_GUID', 
        'CAP_PROP_ISO_SPEED', 'CAP_PROP_BACKLIGHT', 'CAP_PROP_PAN', 'CAP_PROP_TILT', 'CAP_PROP_ROLL', 'CAP_PROP_IRIS', 'CAP_PROP_SETTINGS', 
        'CAP_PROP_BUFFERSIZE', 'CAP_PROP_AUTOFOCUS']

        print('dump_props')
        for i in range(len(fourcc_names)):
                print (i, fourcc_names[i], self.cam.get(i))

    def test_fps(self, framerate, resolution, format_):
        # open opencv capture device and set the fps
        # capture frames over 5 seconds and calculate fps
        t_end = time.time() + 3
        print("Setting framerate to: {}".format(framerate))
        self.cam.set(cv2.CAP_PROP_FPS, framerate)
        print("Current framerate: {}".format(self.cam.get(cv2.CAP_PROP_FPS)))

        while True:
            if time.time() > t_end:
                break

            # grab frame and check if it was successful
            retval, frame = self.cam.read()
            if retval is True:
                dbg_print('obtained frame. count: %d' % count)
                skip -= 1
                count += 1
            else:
                dbg_print('frame not obtained')
                skip -= 1

        elapsed = time.time() - start
        dbg_print('time elapsed: %f' % elapsed)
        calc_fps = float(count) / elapsed
        dbg_print('calc_fps: %f' % calc_fps)
        eps = 1.0
        abs_diff = abs(calc_fps - framerate)

        # success
        if abs_diff < eps:
            dbg_print('success')
            return 0
        #failure
        else:
            dbg_print('failure. abs_diff: %f' % abs_diff)
            return -1

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        dbg_print('FPSTester::test: args = %s' % repr(args))
        self.err_code = {}

        #dictionary of format, resolution, framerate
        #fps_params = {'MJPG' : {'4k' : 22, '1080p' : 30, '720p' : 30 }, 'YUYV' : {'4k' : 30, '1080p' : 30, '720p' : 30 }}
        fps_params = {'YUY2' : {'4k' : 30, '1080p' : 30, '720p' : 30 }}

        for format_ in fps_params:
            resdict = fps_params[format_]
            for resolution in resdict:
                framerate = resdict[resolution]
                print(framerate, resolution, format_)
                test_type = str(framerate) + ' x ' + str(resolution) + ' x ' + str(format_)
                self.err_code[test_type] = self.test_fps(framerate, resolution, format_)
                self.progress_percent += 33

        self.progress_percent = 100

        dbg_print('FPSTester::test: err_code = %s' % repr(self.err_code))
        return self.err_code

if __name__ == "__main__":
	t = FPS()
	args = t.get_args()
	t.run(args)
	print(t.get_progress())
	print(t.is_done())
	print(t.generate_report())

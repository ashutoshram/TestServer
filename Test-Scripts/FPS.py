import os
import time
import cv2
import platform
import numpy as np

production = False
debug = True 
if not production:
    import AbstractTestClass as ATC
else:
    import eos.scripts.AbstractTestClass as ATC

def dbg_print(*args):
    if debug: print("".join(map(str, args)))

class FPS(ATC.AbstractTestClass):

    def __init__(self):
        if platform.system() == 'Darwin':
            cap_id = 1
        else:
            cap_id = 0
        self.FPSTest = FPSTester(cap_id)

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

    def generate_report(self):
        return self.FPSTest.results()


class FPSTester():

    def __init__(self, cap_id=0):
        self.progress_percent = 0 
        self.cap_id = cap_id
        self.os_type = platform.system()
        if self.os_type == 'Windows':
            self.cap = cv2.VideoCapture(self.cap_id,cv2.CAP_DSHOW)
        elif self.os_type == 'Darwin':
            self.cap = cv2.VideoCapture(self.cap_id)
        elif self.os_type == 'Linux':
            self.cap = cv2.VideoCapture(self.cap_id)
        if not self.cap.isOpened():
            print('Failed to open capture device %d' % self.cap_id)
            #FIXME throw an exception

        #self.dump_props()

    def dump_props(self):
        fourcc_names = ['CAP_PROP_POS_MSEC', 'CAP_PROP_POS_FRAMES', 'CAP_PROP_POS_AVI_RATIO', 'CAP_PROP_FRAME_WIDTH', 'CAP_PROP_FRAME_HEIGHT', 'CAP_PROP_FPS', 'CAP_PROP_FOURCC', 'CAP_PROP_FRAME_COUNT', 'CAP_PROP_FORMAT', 'CAP_PROP_MODE', 'CAP_PROP_BRIGHTNESS', 'CAP_PROP_CONTRAST', 'CAP_PROP_SATURATION', 'CAP_PROP_HUE', 'CAP_PROP_GAIN', 'CAP_PROP_EXPOSURE', 'CAP_PROP_CONVERT_RGB', 'CAP_PROP_WHITE_BALANCE_BLUE_U', 'CAP_PROP_RECTIFICATION', 'CAP_PROP_MONOCHROME', 'CAP_PROP_SHARPNESS', 'CAP_PROP_AUTO_EXPOSURE', 'CAP_PROP_GAMMA', 'CAP_PROP_TEMPERATURE', 'CAP_PROP_TRIGGER', 'CAP_PROP_TRIGGER_DELAY', 'CAP_PROP_WHITE_BALANCE_RED_V', 'CAP_PROP_ZOOM', 'CAP_PROP_FOCUS', 'CAP_PROP_GUID', 'CAP_PROP_ISO_SPEED', 'CAP_PROP_BACKLIGHT', 'CAP_PROP_PAN', 'CAP_PROP_TILT', 'CAP_PROP_ROLL', 'CAP_PROP_IRIS', 'CAP_PROP_SETTINGS', 'CAP_PROP_BUFFERSIZE', 'CAP_PROP_AUTOFOCUS']
        print('dump_props')
        for i in range(len(fourcc_names)):
                print (i, fourcc_names[i], self.cap.get(i))



    def decode_fourcc(self,v):
        v = int(v)
        return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])


    def test_fps(self, framerate, resolution, format_):
        # open opencv capture device and set the fps
        # capture frames over 5 seconds and calculate fps


        if resolution == '4k':
            if self.os_type == 'Windows':
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)
            else:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)

        if resolution == '1080p':
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        if resolution == '720p':
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
        self.cap.set(cv2.CAP_PROP_FPS, framerate)

        if format_ == 'MJPG':
            while True:
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
                fourcc = self.decode_fourcc(self.cap.get(cv2.CAP_PROP_FOURCC))
                if fourcc != 'MJPG':
                    dbg_print('capturing format = %s' % fourcc)
                    dbg_print('Not MJPG - trying again')
                    time.sleep(0.5)

        if format_ == 'YUYV':
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))


        dbg_print('capturing at resolution = %d x %d' % (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))


        start = time.time()
        count = 0
        skip = 10

        while True:

            if (time.time() - start) > 5.0:
                break
            ret, frame = self.cap.read()
            #dbg_print('got frame: count = %d' % count)

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

        self.err_code = {}


        #dictionary of format, resolution, framerate

        if self.os_type == 'Windows':
            fps_params = {'MJPG' : {'4k' : 22, '1080p' : 30, '720p' : 30 }, 'YUYV' : {'4k' : 30, '1080p' : 30, '720p' : 30 }}
        elif self.os_type == 'Darwin':
            fps_params = {'MJPG' : {'4k' : 22, '1080p' : 30, '720p' : 30 }, 'YUYV' : {'4k' : 30, '1080p' : 30, '720p' : 30 }}
        elif self.os_type == 'Linux':
            fps_params = {'YUYV' : {'4k' : 30, '1080p' : 27, '720p' : 30 }}

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

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
        # check if camera stream exists
        if self.cam is None:
            print('cv2.VideoCapture unsuccessful')
            sys.exit(1)
            print(self.cam)

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
            print("Video format set to: MJPG")
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        if format_ == 'YUYV':
            print("Video format set to: YUYV")
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        if format_ == 'YUY2':
            print("Video format set to: YUY2")
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUY2'))

        # open opencv capture device and set the fps
        # capture frames over 5 seconds and calculate fps
        print("Setting framerate to: {}".format(framerate))
        self.cam.set(cv2.CAP_PROP_FPS, framerate)
        current_fps = self.cam.get(cv2.CAP_PROP_FPS)
        print("Current framerate set to: {}. Checking video stream...\n".format(current_fps))
        
        # check fps for 1, 5, and 10 second streams
        start = time.time()
        one = start + 1
        five = start + 5
        ten = start + 10
        count, skipped = (0 for i in range(2))
        one_yes, five_yes, ten_yes = (False for i in range(3))

        while True:
            if time.time() >= five and five_yes is False:
                duration = time.time() - start
                print("Actual duration:      {:<5} seconds".format(duration))
                print("Total frames counted: {:<5}".format(count))
                print("Total frames skipped: {:<5}".format(skipped))
                fps5 = count / duration
                print("Average fps:          {:<5}\n".format(fps5))
                five_yes = True
            elif time.time() >= ten and ten_yes is False:
                duration = time.time() - start
                print("Actual duration:      {:<5} seconds".format(duration))
                print("Total frames counted: {:<5}".format(count))
                print("Total frames skipped: {:<5}".format(skipped))
                fps10 = count / duration
                print("Average fps:          {:<5}\n".format(fps10))
                ten_yes = True
                break

            retval, frame = self.cam.read()
            if retval is True:
                count += 1
            else:
                print("Frame skipped")
                skipped += 1

        diff5 = abs(float(framerate) - float(fps5))
        diff10 = abs(float(framerate) - float(fps10))
        
        # set framerate back to default
        self.cam.set(cv2.CAP_PROP_FPS, 30)
    
        # success
        if diff5 <= 2 and diff10 <= 2:
            dbg_print("Success.")
            return 0
        #failure
        else:
            dbg_print("Failure.")
            return -1

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code

    def test(self, args):
        # dbg_print('FPSTester::test: args = %s' % repr(args))
        self.err_code = {}

        #dictionary of format, resolution, framerate
        # fps_params = {'MJPG': {'4k': 30, '1080p': 24, '720p': 15}, 
        #               'YUY2': {'4k': 30, '1080p': 24, '720p': 15}}

        fps_params = {'YUY2': {'4k': 30}}

        for format_ in fps_params:
            res_dict = fps_params[format_]
            for resolution in res_dict:
                framerate = res_dict[resolution]
                print(framerate, resolution, format_)
                test_type = str(framerate) + ' x ' + str(resolution) + ' x ' + str(format_)
                
                # set up camera stream
                for k in range(4):
                    self.cam = cv2.VideoCapture(k)
                    if self.cam.isOpened():
                        print("\nPanacast device found: ({})".format(k))
                        break

                self.err_code[test_type] = self.test_fps(framerate, resolution, format_)
                self.progress_percent += 33
                self.cam.release()

            self.progress_percent = 100

        # dbg_print('FPSTester::test: err_code = %s' % repr(self.err_code))
        return self.err_code

if __name__ == "__main__":
	t = FPS()
	args = t.get_args()
	t.run(args)
	print(t.get_progress())
	print(t.is_done())
	print(t.generate_report())

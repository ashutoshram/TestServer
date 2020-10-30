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
        elif resolution == '1200p':
            print("Resolution to be set to: 4800 x 1200")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 4800)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
        elif resolution == '1080p':
            print("Resolution to be set to: 1920 x 1080")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        elif resolution == '720p':
            print("Resolution to be set to: 1280 x 720")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        elif resolution == '540p':
            print("Resolution to be set to: 960 x 540")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        elif resolution == '360p':
            print("Resolution to be set to: 640 x 360")
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if format_ == 'MJPG':
            print("Video format set to: MJPG")
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        elif format_ == 'YUYV':
            print("Video format set to: YUYV")
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
        elif format_ == 'YUY2':
            print("Video format set to: YUY2")
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUY2'))
        elif format_ == 'I420':
            print("Video format set to: I420")
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'I420'))
        elif format_ == 'NV12':
            print("Video format set to: NV12")
            self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'NV12'))

        # open opencv capture device and set the fps
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

        # calculate fps
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

        #dictionary of testing parameters
        fps_params = {'I420': {'4k': [30, 27, 24, 15], '1080p': [30, 27, 24, 15], '720p': [30, 27, 24, 15], '540p': [30, 27, 24, 15], '360p': [30, 27, 24, 15]}, 
                      'YUY2': {'4k': [30], '1200p': [15]}, 
                      'MJPG': {'1080p': [30], '720p': [30], '540p': [30], '360p': [30]}, 
                      'NV12': {'4k': [30, 27, 24, 15], '1080p': [30, 27, 24, 15], '720p': [30, 27, 24, 15], '540p': [30, 27, 24, 15], '360p': [30, 27, 24, 15]}}

        # fps_params = {'MJPG': {'4k': [30, 27, 24, 15], '1080p': [30, 27, 24, 15], '720p': [30, 27, 24, 15]}, 
        #               'YUY2': {'4k': [30, 27, 24, 15], '1080p': [30, 27, 24, 15], '720p': [30, 27, 24, 15]}}

        # iterate through the dictionary and test each format, resolution, and framerate
        for format_ in fps_params:
            res_dict = fps_params[format_]
            for resolution in res_dict:
                framerate = res_dict[resolution]
                for fps in framerate:
                    print(format_, resolution, fps)
                    test_type = str(framerate) + ' x ' + str(resolution) + ' x ' + str(format_)
                
                    # set up camera stream
                    for k in range(4):
                        self.cam = cv2.VideoCapture(k)
                        if self.cam.isOpened():
                            print("\nPanacast device found: ({})".format(k))
                            break

                    self.err_code[test_type] = self.test_fps(fps, resolution, format_)
                    self.progress_percent += 33
                    self.cam.release()

            self.progress_percent = 100

        # dbg_print('FPSTester::test: err_code = %s' % repr(self.err_code))
        return self.err_code

if __name__ == "__main__":
    t = FPS()
    args = t.get_args()
    t.run(args)
    # print(t.get_progress())
    # print(t.is_done())

    print("\nGenerating report...")
    print("{}\n".format(t.generate_report()))

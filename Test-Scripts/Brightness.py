import os
import time
import cv2
import platform
import numpy as np

production = False
debug = False 
if not production:
    import AbstractTestClass as ATC
else:
    import eos.scripts.AbstractTestClass as ATC

def dbg_print(*args):
    if debug: 
        print("".join(map(str, args)))


class UVC(ATC.AbstractTestClass):

    def __init__(self):
        self.UVCTest = UVCTester()

    def get_args(self):
        return [0, 128, 256]

    def run(self, args):
        return self.UVCTest.test(args)

    def get_progress(self):
        return self.UVCTest.progress()

    def set_default_storage_path(self, path):
        self.storage_path = path

    def get_name(self):
        return "UVC Test"
    
    def is_done(self):
        if self.UVCTest.progress() == 100:
            return True
        else:
            return False

    def generate_report(self):
        return self.UVCTest.results()


class UVCTester():

    def __init__(self):
        self.err_code = {}
        self.progress_percent = 0 
        self.os_type = platform.system()
        if self.os_type == 'Windows':
            self.cap_id = 1
        else:
            self.cap_id = 0
        if self.os_type == 'Windows':
            self.cap = cv2.VideoCapture(self.cap_id,cv2.CAP_DSHOW)
        elif self.os_type == 'Darwin':
            self.cap = cv2.VideoCapture(self.cap_id)
        elif self.os_type == 'Linux':
            self.cap = cv2.VideoCapture(self.cap_id)
        if not self.cap.isOpened():
            print('Failed to open capture device %d' % self.cap_id)
            self.cap = cv2.VideoCapture(self.cap_id+1)

    def progress(self):
        return self.progress_percent

    def results(self):
        return self.err_code


    def dump_props(self):
        fourcc_names = ['CAP_PROP_POS_MSEC', 'CAP_PROP_FRAME_WIDTH', 'CAP_PROP_FRAME_HEIGHT', 'CAP_PROP_FPS', 'CAP_PROP_FOURCC', 'CAP_PROP_FORMAT', 'CAP_PROP_MODE', 'CAP_PROP_BRIGHTNESS', 'CAP_PROP_CONTRAST', 'CAP_PROP_SATURATION', 'CAP_PROP_GAIN', 'CAP_PROP_CONVERT_RGB', 'CAP_PROP_SHARPNESS', 'CAP_PROP_TEMPERATURE', 'CAP_PROP_ZOOM', 'CAP_PROP_PAN', 'CAP_PROP_TILT', 'CAP_PROP_BUFFERSIZE', 'CAP_PROP_AUTOFOCUS']
        print('dump_props')
        for i in range(len(fourcc_names)):
                print (i, fourcc_names[i], self.cap.get(i))

    def test(self, args):
        brightness_values = {}
        for brightness_level in args:
            return_val = self.test_brightness(int(brightness_level))
            print("The Brightness Value is %f" % return_val)
            brightness_values[brightness_level] = return_val
        print(brightness_values)
        b = list(brightness_values.values())
        if b[1] > b[0] and b[2] > b[1]:
            for h in args:
                self.err_code[h] = 0


        return self.err_code


    def test_brightness(self,brightness_level):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness_level)

        now = time.time()
        while True:

            ret, frame = self.cap.read()
            cv2.imshow("input", frame)
            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            print(np.average(img_gray))

            
            if (time.time() - now) > 5.0:
                return (np.average(img_gray))
                break

            key = cv2.waitKey(10)
            if key == 27:
                break

        cv2.destroyAllWindows()
        cap.release()

        



if __name__ == "__main__":
	t = UVC()
	args = t.get_args()
	t.run(args)
	print(t.generate_report())

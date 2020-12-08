import cv2
import subprocess
import re

cam_props = {'brightness': 127, 'contrast': 191, 'saturation': 134,
             'sharpness': 128,'zoom_absolute': 12, 
             'white_balance_temperature_auto': 0, 
             'white_balance_temperature': 3300}

#cam_props = {'brightness': 128}

for key in cam_props:
    subprocess.call(['v4l2-ctl -d /dev/video0 -c {}={}'.format(key, str(cam_props[key]))], shell=True)

    s = subprocess.check_output(['v4l2-ctl -d /dev/video0 -C {}'.format(key)], shell=True)
    s = s.decode('UTF-8')
    value = re.match("(.*): (\d+)", s)
    if value.group(2) != str(cam_props[key]):
        print("FAIL: {} get/set not working as intended".format(str(key)))
        print("Exiting now!")
    else:
        print("PASS: Successful {} Test conducted".format(str(key)))
        print("%s now set to %s" % (key, value.group(2)))
        print("Exiting now!")
